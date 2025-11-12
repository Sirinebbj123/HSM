from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import datetime # Ajouté pour simuler les données ou filtrer plus tard
from users.serializers import PatientRegisterSerializer, AdminRegisterSerializer

# ===============================
# 🌐 Configuration de l'API Backend
# ===============================
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
# 👤 Page d’inscription (Register)
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
            messages.success(request, "Compte patient créé avec succès !")
            return redirect("login")
        else:
            messages.error(request, f"Erreur lors de la création du compte : {serializer.errors}")

    return render(request, "register.html")

# ===============================
# 🔐 Page de connexion (Login)
# ===============================
def login_page(request):
    # Si déjà connecté → rediriger automatiquement
    if request.session.get("role") == "admin":
        return redirect("admin_dashboard")
    elif request.session.get("role") == "doctor":
        return redirect("doctor_dashboard")
    elif request.session.get("role") == "patient":
        return redirect("patient_dashboard")

    # Si utilisateur envoie le formulaire
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            response = requests.post(API_BASE + "users/login/", json={
                "username": username,
                "password": password
            })

            # Si la connexion est réussie
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access")
                refresh_token = data.get("refresh")
                role = data.get("role")

                # Sauvegarde dans la session Django
                request.session["username"] = username
                request.session["access_token"] = access_token
                request.session["refresh_token"] = refresh_token
                request.session["role"] = role

                messages.success(request, f"Bienvenue {username} 👋")

                # Redirection selon le rôle
                if role == "admin":
                    return redirect("admin_dashboard")
                elif role == "doctor":
                    return redirect("doctor_dashboard")
                elif role == "patient":
                    return redirect("patient_dashboard")
                else:
                    messages.error(request, "Rôle utilisateur inconnu ❌")
                    return redirect("login")

            else:
                # Erreur de connexion (identifiants invalides)
                messages.error(request, "Nom d’utilisateur ou mot de passe invalide ❌")
                return redirect("login")

        except requests.exceptions.ConnectionError:
            messages.error(request, "Erreur de connexion au serveur backend 🚫")
            return redirect("login")

    # Si simple affichage du formulaire
    return render(request, "login.html")
# ===============================
# 🚪 Déconnexion
# ===============================
def logout_user(request):
    request.session.flush()
    messages.success(request, "Vous êtes déconnecté avec succès 👋")
    return redirect("login")


# ===============================
# 🩺 Interface Médecin
# ===============================
def doctor_dashboard(request):
    role = request.session.get("role")
    username = request.session.get("username")
    access_token = request.session.get("access_token")

    # 1. Vérification de l'authentification et du rôle
    if role != "doctor" or not access_token:
        messages.error(request, "Accès non autorisé. Veuillez vous connecter en tant que médecin.")
        return redirect("login")

    # 2. Définition des Headers d'autorisation pour l'API Backend
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 3. Récupération des données du Dashboard
    try:
        # --- A. Statistiques principales ---
        # Remplacez ceci par un appel API réel pour les statistiques du Dr.
        # response_stats = requests.get(API_BASE + f"doctors/{username}/stats/", headers=headers)
        # stats = response_stats.json()
        
        # Données SIMULÉES (à remplacer) :
        stats = {
            'total_patients': 78,
            'today_appointments': 5,
            'new_reports': 2,
            'new_patients': 3,
            'doctor_name': "Dr. Taher Zaied", # Assurez-vous d'avoir le nom complet
            'doctor_specialization': "Internal Medicine"
        }


        # --- B. Rendez-vous du Jour ---
        # Remplacez ceci par un appel API réel :
        # response_schedule = requests.get(API_BASE + f"doctors/{username}/appointments/today/", headers=headers)
        # schedule = response_schedule.json()
        
        # Données SIMULÉES (à remplacer) :
        schedule = [
            {'time': '09:00 AM', 'name': 'Khalid Al-Ghamdi', 'status': 'Confirmed'},
            {'time': '09:30 AM', 'name': 'Fatima Al-Zahrani', 'status': 'Confirmed'},
            {'time': '10:30 AM', 'name': 'Sarah Abdullah', 'status': 'Confirmed'},
        ]
        
        # --- C. Alertes Critiques ---
        # Remplacez ceci par un appel API réel :
        # response_alerts = requests.get(API_BASE + "alerts/", headers=headers)
        # alerts = response_alerts.json()
        
        # Données SIMULÉES (à remplacer) :
        alerts = [
            {'type': 'Potassium level', 'patient': 'Sarah Abdullah', 'value': '5.2 mEq/L', 'time': '10:30 AM', 'drug': 'N/A'},
            {'type': 'Drug Interaction', 'patient': 'Waleed Al-Ghamdi', 'value': 'Potential serious drug interaction', 'time': '09:15 AM', 'drug': 'Warfarin and Aspirin'},
        ]
        
        # --- D. Données pour le Graphique de Performance ---
        # Données SIMULÉES (à remplacer par des données structurées) :
        weekly_performance_data = [
            {'day': 'Sat', 'patients': 13},
            {'day': 'Sun', 'patients': 19},
            {'day': 'Mon', 'patients': 15},
            {'day': 'Tue', 'patients': 21},
            {'day': 'Wed', 'patients': 18},
            {'day': 'Thu', 'patients': 24},
            {'day': 'Fri', 'patients': 16},
        ]

    except requests.exceptions.RequestException:
        messages.warning(request, "Erreur de connexion au serveur backend. Certaines données peuvent être manquantes.")
        # Utiliser des listes/dictionnaires vides en cas d'erreur
        stats = {}
        schedule = []
        alerts = []
        weekly_performance_data = []


    # 4. Préparation du contexte pour le template
    context = {
        "username": username,
        "stats": stats,
        "schedule": schedule,
        "alerts": alerts,
        "weekly_performance_data": weekly_performance_data,
    }
    
    return render(request, "dashboards/doctor_dashboard.html", context)


def patient_dashboard(request):
    role = request.session.get("role")
    if role != "patient":
        return redirect("login")
    username = request.session.get("username")
    
    # ... Logique de récupération des données patient ...
    return render(request, "dashboards/patient_dashboard.html", {"username": username})

def admin_dashboard(request):
    role = request.session.get("role")
    if role != "admin":
        return redirect("login")
    username = request.session.get("username")
    
    # ... Logique de récupération des données admin ...
    return render(request, "dashboards/admin_dashboard.html", {"username": username})

def book_appointment_page(request, doctor_id):
    role = request.session.get("role")
    username = request.session.get("username")
    access_token = request.session.get("access_token")

    # 1. Vérification du rôle
    if role != "patient" or not access_token:
        messages.error(request, "Accès non autorisé. Veuillez vous connecter en tant que patient.")
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    doctor_details = None
    
    # 2. Récupération des détails du docteur via l'API
    try:
        # Supposons que vous avez un endpoint dans l'API pour obtenir les détails d'un docteur par son ID.
        # Ex: GET /api/users/doctor-details/1/
        response = requests.get(API_BASE + f"users/doctor-details/{doctor_id}/", headers=headers)
        
        if response.status_code == 200:
            doctor_details = response.json()
        else:
            messages.error(request, "Impossible de trouver les détails de ce docteur.")
            # Redirection vers le dashboard si le docteur n'est pas trouvé
            return redirect("patient_dashboard") 

    except requests.exceptions.RequestException:
        messages.error(request, "Erreur de connexion au serveur backend lors de la récupération des détails du docteur.")
        return redirect("patient_dashboard")

    # 3. Traitement du formulaire de réservation (méthode POST)
    if request.method == "POST":
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason")
        
        # Exemple de données à envoyer à l'API de réservation
        appointment_data = {
            "doctor_id": doctor_id,
            "patient_username": username,
            "date": appointment_date,
            "time": appointment_time,
            "reason": reason
        }

        try:
            # Supposons un endpoint API pour créer un rendez-vous
            response_booking = requests.post(API_BASE + "appointments/create/", json=appointment_data, headers=headers)
            
            if response_booking.status_code == 201:
                messages.success(request, "Rendez-vous réservé avec succès !")
                # Redirection vers la liste des rendez-vous du patient
                return redirect("patient_dashboard") 
            else:
                error_message = response_booking.json().get("detail", "Erreur lors de la réservation.")
                messages.error(request, error_message)

        except requests.exceptions.RequestException:
            messages.error(request, "Erreur de communication avec le serveur lors de la réservation.")
            
    # 4. Affichage de la page (méthode GET ou après échec du POST)
    context = {
        "username": username,
        "doctor": doctor_details,
        "doctor_id": doctor_id,
    }
    
    # Assurez-vous d'avoir un template 'book_appointment.html'
    return render(request, "appointment/book_appointment.html", context)


def patient_dashboard(request):
    """
    Affiche le tableau de bord du patient et charge la liste des docteurs via l'API.
    """
    # Récupération des données de session (utilisés après la connexion)
    role = request.session.get("role")
    username = request.session.get("username")
    access_token = request.session.get("access_token")

    # Vérification de l'authentification et du rôle
    if role != "patient" or not access_token:
        messages.error(request, "Accès refusé. Veuillez vous connecter en tant que patient.")
        return redirect("login")

    # Configuration pour l'appel API
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    doctors = []
    
    # 💥 LOGIQUE CLÉ : Appel à l'API du Backend pour les docteurs 💥
    try:
        # L'URL doit correspondre exactement à celle du backend DRF
        response = requests.get(API_BASE + "users/doctor-list/", headers=headers)
        
        if response.status_code == 200:
            # L'API a réussi. Les données sont la liste des docteurs.
            doctors = response.json()
        elif response.status_code == 403:
            # Problème de permission (si vous avez oublié de mettre IsAuthenticated)
            messages.error(request, "Erreur de permission: vous n'êtes pas autorisé à voir cette liste.")
        else:
            # Gérer les autres erreurs HTTP
            messages.error(request, f"Erreur lors du chargement des docteurs: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de connexion réseau (backend éteint, etc.)
        messages.error(request, f"Erreur de connexion au serveur API: {e}")
    
    
    context = {
        "username": username,
        "doctors": doctors, # 👈 Les données des docteurs sont passées au template
    }

    return render(request, "dashboards/patient_dashboard.html", context)