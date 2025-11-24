from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.homepage, name='home'),

    # Auth
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),
    # Dashboards
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    #haroun_confugiration
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('api/admin/overview/', api_views.admin_overview, name='api_admin_overview'),
    path('add-user/admin/', views.admin_add_user, name='admin_add_user'),
    path("patients/admin/", views.list_patients, name="list_patients"),
    path("doctors/admin/", views.list_doctors, name="list_doctors"),
    path("profile/", views.profile_info, name="profile_info"),


    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment_view, name='book_appointment'),
    path('appointments/<int:id>/edit/', views.edit_appointment_view, name='edit_appointment'),
    path('appointments/<int:id>/delete/', views.delete_appointment_view, name='delete_appointment'),

]
