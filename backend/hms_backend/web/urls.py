from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),

    # Auth
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('rendez-vous/prendre/<int:doctor_id>/', views.book_appointment_page, name='book_appointment'),
    # Dashboards
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
