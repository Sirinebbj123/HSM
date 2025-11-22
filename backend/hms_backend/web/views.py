from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from django.urls import reverse
from django.utils import timezone
from users.models import Doctor, Patient, User, Appointment
from users.serializers import PatientRegisterSerializer, AdminRegisterSerializer, DoctorRegisterSerializer

API_BASE = "http://127.0.0.1:8000/api/"

# ===============================
# 🏠 Page d'accueil publique
# ===============================
def homepage(request):
    role = request.session.get("role")
    if role == "admin":
        return redirect("admin_dashboard")
    elif role == "doctor":
        return redirect("doctor_dashboard")
    elif role == "patient":
        return redirect("patient_dashboard")
    return render(request, 'home.html')


# ===============================
# 👤 Inscription (Patient)
# ===============================
def register_page(request):
    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "full_name": request.POST.get("full_name"),
            "age": request.POST.get("age"),
            "phone": request.POST.get("phone"),
            "address": request.POST.get("address"),
        }

        serializer = PatientRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Compte patient créé avec succès ✅")
            return redirect("login")
        else:
            messages.error(request, f"Erreur : {serializer.errors}")
    return render(request, "register.html")


# ===============================
# 🔐 Connexion
# ===============================
def login_page(request):
    if request.session.get("role") in ["admin", "doctor", "patient"]:
        return redirect(f"{request.session.get('role')}_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            response = requests.post(API_BASE + "users/login/", json={"username": username, "password": password})

            if response.status_code == 200:
                data = response.json()
                request.session["username"] = username
                request.session["access_token"] = data.get("access")
                request.session["refresh_token"] = data.get("refresh")
                request.session["role"] = data.get("role")

                messages.success(request, f"Bienvenue {username} 👋")

                return redirect(f"{data.get('role')}_dashboard")
            else:
                messages.error(request, "Nom d’utilisateur ou mot de passe invalide ❌")
        except requests.exceptions.ConnectionError:
            messages.error(request, "Erreur de connexion au serveur backend 🚫")

    return render(request, "login.html")


# ===============================
# 🚪 Déconnexion
# ===============================
def logout_user(request):
    request.session.flush()
    messages.success(request, "Déconnexion réussie 👋")
    return redirect("login")


# ===============================
# 🩺 Dashboard Médecin
# ===============================
def doctor_dashboard(request):
    role = request.session.get("role")
    username = request.session.get("username")
    access_token = request.session.get("access_token")

    if role != "doctor" or not access_token:
        messages.error(request, "Accès non autorisé.")
        return redirect("login")

    headers = {"Authorization": f"Bearer {access_token}"}
    stats, schedule, alerts, weekly_performance_data = {}, [], [], []

    try:
        resp_stats = requests.get(f"{API_BASE}doctors/{username}/stats/", headers=headers)
        stats = resp_stats.json() if resp_stats.status_code == 200 else {}

        resp_schedule = requests.get(f"{API_BASE}doctors/{username}/appointments/today/", headers=headers)
        schedule = resp_schedule.json() if resp_schedule.status_code == 200 else []

        resp_alerts = requests.get(f"{API_BASE}doctors/{username}/alerts/", headers=headers)
        alerts = resp_alerts.json() if resp_alerts.status_code == 200 else []

        resp_perf = requests.get(f"{API_BASE}doctors/{username}/weekly-performance/", headers=headers)
        weekly_performance_data = resp_perf.json() if resp_perf.status_code == 200 else []

    except requests.exceptions.RequestException:
        messages.warning(request, "Erreur de connexion au backend.")

    return render(request, "dashboards/doctor_dashboard.html", {
        "username": username,
        "stats": stats,
        "schedule": schedule,
        "alerts": alerts,
        "weekly_performance_data": weekly_performance_data,
    })


# ===============================
# 🧑‍⚕️ Dashboard Patient
# ===============================
def patient_dashboard(request):
    role = request.session.get("role")
    username = request.session.get("username")
    access_token = request.session.get("access_token")

    if role != "patient" or not access_token:
        messages.error(request, "Accès refusé. Connectez-vous comme patient.")
        return redirect("login")

    headers = {"Authorization": f"Bearer {access_token}"}
    doctors = []

    try:
        response = requests.get(API_BASE + "users/doctor-list/", headers=headers)
        if response.status_code == 200:
            doctors = response.json()
        else:
            messages.error(request, f"Erreur : {response.status_code}")
    except requests.exceptions.RequestException:
        messages.error(request, "Erreur de communication avec le serveur.")

    return render(request, "dashboards/patient_dashboard.html", {
        "username": username,
        "doctors": doctors,
    })


# ===============================
# 🩺 Réserver un rendez-vous
# ===============================
def book_appointment_view(request, doctor_id):
    role = request.session.get("role")
    access_token = request.session.get("access_token")

    if role != "patient" or not access_token:
        messages.error(request, "Connectez-vous comme patient.")
        return redirect("login")

    headers = {"Authorization": f"Bearer {access_token}"}
    doctor_details = {"id": doctor_id, "full_name": f"Docteur {doctor_id}", "specialization": "Médecin généraliste"}

    if request.method == "POST":
        appointment_data = {
            "doctor": doctor_id,
            "date": request.POST.get("date"),
            "time": request.POST.get("time"),
            "reason": request.POST.get("reason"),
        }

        try:
            response_booking = requests.post(API_BASE + "users/appointments/create/", json=appointment_data, headers=headers)
            if response_booking.status_code == 201:
                messages.success(request, "Rendez-vous réservé avec succès ✅")
                return redirect("patient_dashboard")
            else:
                messages.error(request, f"Erreur : {response_booking.json()}")
        except requests.exceptions.RequestException:
            messages.error(request, "Erreur réseau lors de la réservation.")

    return render(request, "book_appointment.html", {"doctor": doctor_details})


# ===============================
# 🧑‍💼 Dashboard Admin
# ===============================
def admin_dashboard(request):
    role = request.session.get("role")
    if role != "admin":
        return redirect("login")

    username = request.session.get("username")
    today = timezone.localdate()

    total_patients = User.objects.filter(role='patient').count()
    total_doctors = User.objects.filter(role='doctor').count()
    appointments_today = Appointment.objects.filter(date=today).count()

    recent_appointments = Appointment.objects.select_related('doctor', 'patient').order_by('-created_at')[:10]

    context = {
        "username": username,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "appointments_today": appointments_today,
        "recent_appointments": recent_appointments,
        "today": today,
    }
    return render(request, "dashboards/admin_dashboard.html", context)


# ===============================
# 🧩 Gestion des utilisateurs (Admin)
# ===============================
def admin_add_user(request):
    if request.session.get("role") != "admin":
        messages.error(request, "Accès refusé.")
        return redirect("login")

    if request.method == "POST":
        user_type = request.POST.get("user_type")
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "full_name": request.POST.get("full_name"),
            "age": request.POST.get("age"),
            "phone": request.POST.get("phone"),
            "address": request.POST.get("address"),
        }

        if user_type == "patient":
            serializer = PatientRegisterSerializer(data=data)
        elif user_type == "doctor":
            data["specialization"] = request.POST.get("specialization")
            data["experience_years"] = request.POST.get("experience_years")
            data["description"] = request.POST.get("description", "")
            serializer = DoctorRegisterSerializer(data=data)
        else:
            messages.error(request, "Type invalide.")
            return redirect("admin_add_user")

        if serializer.is_valid():
            serializer.save()
            messages.success(request, f"Compte {user_type} créé ✅")
            return redirect("admin_dashboard")
        else:
            messages.error(request, f"Erreur : {serializer.errors}")

    return render(request, "admin_add_user.html")


# ===============================
# 👥 Liste des patients et docteurs
# ===============================
def list_patients(request):
    if request.session.get("role") != "admin":
        messages.error(request, "Accès refusé.")
        return redirect("login")

    patients = User.objects.filter(role="patient")
    return render(request, "admin_patients_list.html", {"patients": patients})


def list_doctors(request):
    if request.session.get("role") != "admin":
        messages.error(request, "Accès refusé.")
        return redirect("login")

    doctors = User.objects.filter(role="doctor")
    return render(request, "admin_doctors_list.html", {"doctors": doctors})


# ===============================
# 👤 Profil utilisateur
# ===============================
def profile_info(request):
    username = request.session.get("username")
    role = request.session.get("role")
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Veuillez vous connecter.")
        return redirect("login")

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(API_BASE + f"users/profile/{username}/", headers=headers)
        user_data = response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        user_data = {}

    return render(request, "profile_info.html", {"user_data": user_data})
