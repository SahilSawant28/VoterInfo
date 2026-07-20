from django.urls import path
from core import api_views

urlpatterns = [
    # Polling Booth API
    path('booths/', api_views.BoothListCreateAPIView.as_view(), name='api_booth_list_create'),
    path('booths/<str:pin_code>/', api_views.BoothByPincodeAPIView.as_view(), name='api_booth_by_pincode'),
    path('booths/detail/<str:booth_number>/', api_views.BoothDetailAPIView.as_view(), name='api_booth_detail'),

    # Complaint API
    path('complaints/', api_views.ComplaintListCreateAPIView.as_view(), name='api_complaint_list_create'),
    path('complaints/<str:complaint_id>/status/', api_views.ComplaintStatusAPIView.as_view(), name='api_complaint_status'),
    path('complaints/<str:complaint_id>/', api_views.ComplaintDeleteAPIView.as_view(), name='api_complaint_delete'),

    # Eligibility API
    path('eligibility/', api_views.EligibilityAPIView.as_view(), name='api_eligibility'),
]
