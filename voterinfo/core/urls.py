from django.contrib.auth.views import LogoutView
from django.urls import path
from core import views, dashboard_views

urlpatterns = [
    path('', views.home, name='home'),
    path('booth-locator/', views.booth_locator, name='booth_locator'),
    path('eligibility-checker/', views.eligibility_checker, name='eligibility_checker'),
    path('registration-guide/', views.registration_guide, name='registration_guide'),
    path('required-documents/', views.required_documents, name='required_documents'),
    path('complaint-form/', views.complaint_form, name='complaint_form'),
    path('complaint-form/export/', views.export_complaints_csv, name='export_complaints_csv'),
    path('about/', views.about, name='about'),

    # AJAX / background-task endpoints
    path('search/', views.search_booth_ajax, name='search_booth_ajax'),
    path('import/start/', views.trigger_import, name='trigger_import'),
    path('import/status/', views.import_status, name='import_status'),

    # Custom Admin Dashboard (MongoDB-aware)
    path('dashboard/login/', dashboard_views.DashboardLoginView.as_view(), name='dashboard_login'),
    path('dashboard/logout/', LogoutView.as_view(next_page='home'), name='dashboard_logout'),
    path('dashboard/', dashboard_views.dashboard_home, name='dashboard_home'),
    path('dashboard/booths/', dashboard_views.dashboard_booths, name='dashboard_booths'),
    path('dashboard/complaints/', dashboard_views.dashboard_complaints, name='dashboard_complaints'),
    path('dashboard/users/', dashboard_views.dashboard_users, name='dashboard_users'),
    path('dashboard/stats/', dashboard_views.dashboard_stats, name='dashboard_stats'),
]
