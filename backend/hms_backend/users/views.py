from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from .models import User, Doctor, Patient
from .serializers import RegisterSerializer,PatientRegisterSerializer,AdminRegisterSerializer, DoctorRegisterSerializer, DoctorListSerializer, DoctorUpdateSerializer,PatientListSerializer, PatientUpdateSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

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