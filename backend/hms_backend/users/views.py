from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from .models import User, Doctor, Patient , Appointment
from .serializers import RegisterSerializer,PatientRegisterSerializer,AdminRegisterSerializer, DoctorRegisterSerializer, DoctorListSerializer, DoctorUpdateSerializer,PatientListSerializer, PatientUpdateSerializer,AppointmentSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Bienvenue " + request.user.username})
    
def home(request):
    return render(request, 'home.html')  # Assurez-vous que 'home.html' existe
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
class PatientRegisterView(generics.CreateAPIView):
    serializer_class = PatientRegisterSerializer
    permission_classes = [AllowAny]
class AdminRegisterView(generics.CreateAPIView):
    serializer_class = AdminRegisterSerializer
    permission_classes = [AllowAny]

class DoctorRegisterView(generics.CreateAPIView):
    serializer_class = DoctorRegisterSerializer
    permission_classes = [IsAdminUser]  # Seul l'admin peut créer

    queryset = User.objects.filter(role="doctor")

# class DoctorListView(generics.ListAPIView):
#     queryset = Doctor.objects.all() 
#     serializer_class = DoctorListSerializer
#     permission_classes = [IsAdminUser]
from rest_framework.permissions import IsAuthenticated # S'assurer que ceci est importé

class DoctorListView(APIView):
    # 💥 AJOUTER CECI : Seuls les utilisateurs connectés peuvent voir la liste 💥
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):
        doctors = Doctor.objects.all()  # 🔹 Récupère tous les docteurs
        serializer = DoctorListSerializer(doctors, many=True)
        # 💥 ATTENTION : 'status' n'est pas directement importé, il faut utiliser drf.status 💥
        # Si vous utilisez status=status.HTTP_200_OK, assurez-vous de l'import :
        # from rest_framework import status 
        return Response(serializer.data, status=200) # Utiliser 200 si vous ne voulez pas importer drf.status

class DoctorUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorUpdateSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'  # On utilise l'id du profil Doctor

class DoctorDeleteView(generics.DestroyAPIView):
    queryset = Doctor.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'  # On utilise l'id du profil Doctor

class PatientListView(generics.ListAPIView):
    queryset = Patient.objects.all()  # Tous les profils Patient
    serializer_class = PatientListSerializer
    permission_classes = [IsAdminUser]

class PatientUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientUpdateSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'  # On utilise l'id du profil Patient

class PatientDeleteView(generics.DestroyAPIView):
    queryset = Patient.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != 'patient':
        # Lance une exception gérée par DRF pour un statut 403 Forbidden
           raise PermissionDenied("Seuls les patients peuvent réserver un rendez-vous.")

        try:
        # Assurez-vous que le profil Patient existe
           patient = user.patient_profile
        except Patient.DoesNotExist:
        # Ceci devrait en théorie ne pas arriver si le role est 'patient', 
        # mais c'est une sécurité.
           raise PermissionDenied("Votre compte Patient n'est pas correctement configuré.")

        serializer.save(patient=patient)

 


# ✅ Un docteur consulte ses rendez-vous
class DoctorAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'doctor':
            return Appointment.objects.filter(doctor=self.request.user.doctor_profile)
        elif self.request.user.role == 'admin':
            return Appointment.objects.all()
        else:
            return Appointment.objects.none()


# ✅ Le docteur peut confirmer, rejeter ou terminer le rendez-vous
class AppointmentStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            appointment = Appointment.objects.get(id=id)
        except Appointment.DoesNotExist:
            return Response({"error": "Rendez-vous introuvable."}, status=404)

        if request.user.role != 'doctor':
            return Response({"error": "Seul le docteur peut modifier le statut."}, status=403)

        status_value = request.data.get('status')
        if status_value not in ['CONFIRMED', 'CANCELLED', 'COMPLETED']:
            return Response({"error": "Statut invalide."}, status=400)

        appointment.status = status_value
        appointment.save()
        return Response({
            "message": f"Rendez-vous {status_value.lower()} avec succès.",
            "appointment": AppointmentSerializer(appointment).data
        })    
    
class PatientAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs['id']  # Récupère l’ID depuis l’URL
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Appointment.objects.none()  # Si patient introuvable → aucun résultat

        user = self.request.user

        # 🛡️ Sécurité :
        # - Le patient ne peut voir que ses propres rendez-vous
        # - Un docteur ne peut pas voir les rendez-vous d’un autre patient
        # - L’admin peut tout voir
        if user.role == 'patient' and patient.user != user:
            return Appointment.objects.none()

        if user.role == 'doctor':
            # Un docteur ne voit que ses propres rendez-vous liés à ce patient
            return Appointment.objects.filter(doctor=user.doctor_profile, patient=patient)

        # L’admin voit tous les rendez-vous du patient
        return Appointment.objects.filter(patient=patient) 

class MyDoctorAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 🛡️ Vérifie que c’est bien un docteur
        if user.role != 'doctor':
            return Appointment.objects.none()

        # 🩺 Récupère le profil docteur du user
        doctor = user.doctor_profile

        # 🔍 Retourne tous les rendez-vous liés à ce docteur
        return Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')       