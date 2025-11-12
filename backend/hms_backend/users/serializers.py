from rest_framework import serializers
from .models import Appointment, User, Patient, Doctor
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='patient'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PatientRegisterSerializer(serializers.Serializer):
    # Champs du User
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    # Champs du Patient
    full_name = serializers.CharField()
    age = serializers.IntegerField()
    phone = serializers.CharField()
    address = serializers.CharField()

    def create(self, validated_data):
        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError({"username": "Ce nom d'utilisateur existe déjà."})
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({"email": "Cet email existe déjà."})
        # Création de l'utilisateur
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role="patient"
        )
        user.set_password(validated_data['password'])
        user.save()

        # Création du profil Patient
        patient = Patient.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            age=validated_data['age'],
            phone=validated_data['phone'],
            address=validated_data['address']
        )

        # On retourne les deux objets pour la représentation
        return {"user": user, "patient": patient}

    def to_representation(self, instance):
        """
        Personnalisation de la réponse renvoyée à l'utilisateur.
        """
        user = instance["user"]
        patient = instance["patient"]

        return {
            "message": "Patient enregistré avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            },
            "patient": {
                "full_name": patient.full_name,
                "age": patient.age,
                "phone": patient.phone,
                "address": patient.address
            }
        }
class AdminRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def create(self, validated_data):
        # Vérifie s’il existe déjà un admin
        if User.objects.filter(role='admin').exists():
            raise serializers.ValidationError("Un administrateur existe déjà.")

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role="admin",
            is_staff=True,
            is_superuser=True
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def to_representation(self, instance):
        return {
            "message": "Administrateur créé avec succès",
            "user": {
                "id": instance.id,
                "username": instance.username,
                "email": instance.email,
                "role": instance.role
            }
        }
class DoctorRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    full_name = serializers.CharField()
    specialization = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()
    experience_years = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        # Vérifier si le username existe déjà
        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError({"username": "Ce nom d'utilisateur existe déjà."})
        
        # Création du compte User
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role="doctor",
            is_staff=False
        )
        user.set_password(validated_data['password'])
        user.save()

        # Création du profil Doctor
        Doctor.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            specialization=validated_data['specialization'],
            phone=validated_data['phone'],
            email=validated_data['email'],
            address=validated_data['address'],
            experience_years=validated_data['experience_years'],
            description=validated_data.get('description', '')
        )

        return user

    def to_representation(self, instance):
        doctor = instance.doctor_profile
        return {
            "message": "Docteur créé avec succès",
            "doctor": {
                "username": instance.username,
                "email": instance.email,
                "full_name": doctor.full_name,
                "specialization": doctor.specialization,
                "phone": doctor.phone,
                "address": doctor.address,
                "experience_years": doctor.experience_years,
                "description": doctor.description
            }
        }

class DoctorListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Doctor
        fields = [
            'id',  # 💥 AJOUTEZ L'ID ICI 💥
            'username',
            'email',
            'full_name',
            'specialization',
            'phone',
            'address',
            'experience_years',
            'description'
        ]
class DoctorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'full_name',
            'specialization',
            'phone',
            'address',
            'experience_years',
            'description'
        ]

class PatientListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Patient
        fields = [
            'username',
            'email',
            'full_name',
            'age',
            'phone',
            'address'
        ]

class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['full_name', 'age', 'phone', 'address']



# ... (Après tous les autres sérialiseurs)

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date', 'time', 'reason']

    def validate(self, data):
        # 💡 NOTE : Vous devez implémenter ici la logique pour valider
        # que l'heure et la date ne sont pas déjà réservées par le docteur.
        # Vous devez également vous assurer que 'doctor' et 'patient' sont des instances valides.
        return data