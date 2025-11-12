from django.urls import path
from .views import (
    ProtectedView, RegisterView, PatientRegisterView, AdminRegisterView,
    DoctorRegisterView, DoctorListView, DoctorUpdateView, DoctorDeleteView,
    PatientListView, PatientUpdateView, PatientDeleteView
)
from .custom_token import CustomTokenObtainPairView  # ✅ ICI
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # ✅ remplacé
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),

    # CRUD utilisateurs
    path('patient-register/', PatientRegisterView.as_view(), name='patient_register'),
    path('admin-register/', AdminRegisterView.as_view(), name='admin_register'),
    path('doctor-register/', DoctorRegisterView.as_view(), name='doctor_register'),
    path('doctor-list/', DoctorListView.as_view(), name='doctor_list'),
    path('doctor-update/<int:id>/', DoctorUpdateView.as_view(), name='doctor_update'),
    path('doctor-delete/<int:id>/', DoctorDeleteView.as_view(), name='doctor_delete'),
    path('patient-list/', PatientListView.as_view(), name='patient_list'),
    path('patient-update/<int:id>/', PatientUpdateView.as_view(), name='patient_update'),
    path('patient-delete/<int:id>/', PatientDeleteView.as_view(), name='patient_delete'),
]
