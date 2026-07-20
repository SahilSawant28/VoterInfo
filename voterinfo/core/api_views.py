"""
core/api_views.py
-------------------
Django REST Framework API views.

Polling Booth API:
    GET    /api/booths/                -> list all booths (paginated)
    GET    /api/booths/<pin_code>/     -> get booth(s) by PIN code
    POST   /api/booths/                -> create booth
    PUT    /api/booths/<booth_number>/ -> update booth
    DELETE /api/booths/<booth_number>/ -> delete booth

Complaint API:
    POST   /api/complaints/                    -> file a complaint
    GET    /api/complaints/                    -> list complaints
    PUT    /api/complaints/<complaint_id>/status/ -> update status
    DELETE /api/complaints/<complaint_id>/     -> delete complaint

Eligibility API:
    POST   /api/eligibility/  -> {dob, aadhaar} -> {age, is_eligible}
"""

import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.pagination import PageNumberPagination

from core.mongo_models import PollingBooth, Complaint
from core.serializers import (
    PollingBoothSerializer, ComplaintSerializer, EligibilityRequestSerializer,
)
from core.booth_locator import calculate_age, InvalidInputError
from core.validators import is_valid_aadhaar

logger = logging.getLogger('core')


class SimplePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ------------------------------------------------------------------
# POLLING BOOTH API
# ------------------------------------------------------------------
class BoothListCreateAPIView(APIView):
    """GET (list, paginated) + POST (create) for /api/booths/"""

    def get(self, request):
        qs = PollingBooth.objects.all()
        paginator = SimplePagination()
        page = paginator.paginate_queryset([b.to_dict() for b in qs], request)
        serializer = PollingBoothSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PollingBoothSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if PollingBooth.objects.filter(booth_number=data['booth_number']).first():
            return Response(
                {"detail": "A booth with this booth_number already exists."},
                status=http_status.HTTP_409_CONFLICT,
            )

        booth = PollingBooth(**data).save()
        return Response(booth.to_dict(), status=http_status.HTTP_201_CREATED)


class BoothByPincodeAPIView(APIView):
    """GET /api/booths/<pin_code>/ -> all booths for that PIN code"""

    def get(self, request, pin_code):
        qs = PollingBooth.objects.filter(pin_code=pin_code)
        if not qs:
            return Response({"detail": f"No booth found for PIN Code {pin_code}."},
                             status=http_status.HTTP_404_NOT_FOUND)
        data = [b.to_dict() for b in qs]
        serializer = PollingBoothSerializer(data, many=True)
        return Response(serializer.data)


class BoothDetailAPIView(APIView):
    """PUT/DELETE /api/booths/detail/<booth_number>/"""

    def _get_object(self, booth_number):
        return PollingBooth.objects.filter(booth_number=booth_number).first()

    def put(self, request, booth_number):
        booth = self._get_object(booth_number)
        if not booth:
            return Response({"detail": "Booth not found."}, status=http_status.HTTP_404_NOT_FOUND)

        serializer = PollingBoothSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

        for field, value in serializer.validated_data.items():
            setattr(booth, field, value)
        booth.save()
        return Response(booth.to_dict())

    def delete(self, request, booth_number):
        booth = self._get_object(booth_number)
        if not booth:
            return Response({"detail": "Booth not found."}, status=http_status.HTTP_404_NOT_FOUND)
        booth.delete()
        return Response({"detail": f"Booth {booth_number} deleted."}, status=http_status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------
# COMPLAINT API
# ------------------------------------------------------------------
class ComplaintListCreateAPIView(APIView):

    def get(self, request):
        qs = Complaint.objects.all()
        paginator = SimplePagination()
        page = paginator.paginate_queryset([c.to_dict() for c in qs], request)
        serializer = ComplaintSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ComplaintSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data.pop('status', None)
        complaint = Complaint(**data).save()
        return Response(complaint.to_dict(), status=http_status.HTTP_201_CREATED)


class ComplaintStatusAPIView(APIView):
    """PUT /api/complaints/<complaint_id>/status/"""

    def put(self, request, complaint_id):
        complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
        if not complaint:
            return Response({"detail": "Complaint not found."}, status=http_status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in Complaint.STATUS_CHOICES:
            return Response(
                {"detail": f"Status must be one of {Complaint.STATUS_CHOICES}."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        complaint.status = new_status
        complaint.save()
        return Response(complaint.to_dict())


class ComplaintDeleteAPIView(APIView):
    """DELETE /api/complaints/<complaint_id>/"""

    def delete(self, request, complaint_id):
        complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
        if not complaint:
            return Response({"detail": "Complaint not found."}, status=http_status.HTTP_404_NOT_FOUND)
        complaint.delete()
        return Response({"detail": f"Complaint {complaint_id} deleted."},
                         status=http_status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------
# ELIGIBILITY API
# ------------------------------------------------------------------
class EligibilityAPIView(APIView):
    """POST /api/eligibility/ -> {dob, aadhaar} -> {age, is_eligible}"""

    def post(self, request):
        serializer = EligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

        dob = serializer.validated_data['dob']
        aadhaar = serializer.validated_data['aadhaar']

        try:
            age = calculate_age(dob)
        except InvalidInputError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)

        docs_valid = is_valid_aadhaar(aadhaar)
        is_eligible = age >= 18 and docs_valid

        return Response({
            "age": age,
            "documents_valid": docs_valid,
            "is_eligible": is_eligible,
            "message": "Eligible for Voter Registration" if is_eligible else "Not Eligible Yet",
        })
