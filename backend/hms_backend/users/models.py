from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return self.username
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=150)
    age = models.IntegerField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    experience_years = models.IntegerField()
    description = models.TextField(blank=True, null=True)  # optionnel

    def __str__(self):
        return f"{self.full_name} ({self.specialization})"
# Dans models.py, assurez-vous d'importer User, Doctor, Patient si ce n'est pas déjà fait

class Appointment(models.Model):
    # Clé étrangère vers le modèle Doctor
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    # Clé étrangère vers le modèle Patient (si vous avez un modèle Patient)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_appointments')
    
    # Alternativement, si vous liez directement à l'utilisateur :
    # patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'En attente'),
            ('CONFIRMED', 'Confirmé'),
            ('CANCELLED', 'Annulé'),
            ('COMPLETED', 'Terminé')
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RDV: {self.patient.full_name} avec Dr. {self.doctor.full_name} le {self.date}"