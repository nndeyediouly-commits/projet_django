# ESMT — Application de Gestion des Taches Collaboratives 
Application Web developpee avec Django et React pour gerer des taches 
collaboratives a l ESMT, destinee aux enseignants et etudiants.
# Pour les fonctionnalites

## Gestion des utilisateurs
- Inscription et connexion securisee
- Deux roles : Etudiant et Professeur
- Mise a jour du profil (nom, avatar, email, mot de passe)

## Gestion des projets
- Creer, modifier et supprimer des projets 
-  Ajouter des membres a un projet
- Seul le createur peut gerer les membres et les taches 

## Gestion des taches
- Creer des taches avec titre, description, date limite et statut
- Statuts disponibles : A faire, En cours, Termine
- Les membres assignes peuvent uniquement changer le statut
- Un etudiant ne peut pas assigner un professeur a une tache

## Les Statistiques et les Primes
- Statisques trimestrielles et annuelles
- Calcul automatique des primes pour les professeurs :
- 100000 Fcfa pour 100% des taches dans les delais
- 30000 Fcfa pour 90% ou plus dans les delais
 
## API REST 
- Authentification JWT
- Endpoints pour projets, taches et statistiques
- Connectee au frontend React

## Fonctionnalites Bonus
- Notifications par email pour les taches prohes de leur echeance
- Recherche avancee et filtres pour les taches
- Integration Google Calendar pour ajouter les taches au calendrier
- Chat en temps reel par projet via Django Channels

# Technologies utilisees

## Backend
**technologie**
Python 3.14
Django 6.0
Django REST Framework
djangorestframework-simplejwt
django-cors-headers
Django Channels
Pillow
SQLite
pytest-django

**Role**
Langage principal
Framework backend
API RESTful
Authentification jwt
CORS pour le frontend React
Chat WebSocket temps reel
Gestion des images
Base de donnees 
Tests unitaires

## Frontend (Objectif 1 - Django Templates)
**Technologie**         | **Role**
Django Templates        | Rendu HTML cote serveur
Bootstrap 5             | Interface utilisateur
Bootstrap Icons         | Icones
JavaScript              | Interactions dynamiques

## Frontend (Objectif 2 - React)
**Technologie**         |  **Role**
React 18                | Framework JavaScript   
React Router            | Navigation entre pages
Axios                   | Appels API vers Django
Bootstrap 5             | Interface utilisateur
Bootstrap Icons         | Icones

# Installation et Configuration 
 
## Prerequis 
- Python 3.14
- Node.js 18
- npm 9

### Backend Django 
# 1. Cloner le projet
git clone https://github.com/nndeyediouly-commits/projet_django.git
cd esmt_tasks 

# 2. Creer et activer l environnement virtuel
python -m venv venv
venv\Scripts\activate
# 3. Installer les dependances 
pip install django djangorestframework
djangoframework-simplejwt django-cors-headers channels
pillow pytest-django google-auth google-auth-oauthlib google-auth-httplib2
google-api-python-client

# 4. Appliquer les migrations 
python manage.py makemigrations
python manage.py migrate

# 5. Creer un puperutilisateur 
 python manage.py createsuperuser

# 6.Lancer le serveur Django 
python manage.py runserver 8004

**accessible sur http://127.0.0.1:8004**

### Frontend React 
# 1. Aller dans le dossier React
cd esmt-react

# 2. Installer les dependances 
npm install

# 3. Lancer React
npm start

**accessible sur http://localhost:3000**

### Lancer les deux en meme temps
Nous avons ouvert **deux terminaux** :

**Terminal 1 - Django**
cd esmt_tasks
python manage.py runserver 8004

**Terminal 2 - React**
cd esmt-react 
npm start

#### Structure de mon projet 

├── esmt_tasks/                  # Backend Django
│   ├── accounts/                # App gestion des utilisateurs
│   │   ├── models.py            # Modèle User personnalisé
│   │   ├── views.py             # Vues login, register, profil
│   │   ├── forms.py             # Formulaires
│   │   └── urls.py              # URLs
│   ├── projects/                # App projets et tâches
│   │   ├── models.py            # Modèles Project et Task
│   │   ├── views.py             # Vues Django Templates
│   │   ├── api_views.py         # Vues API REST
│   │   ├── api_urls.py          # URLs API
│   │   ├── serializers.py       # Serializers DRF
│   │   ├── consumers.py         # WebSocket Chat
│   │   ├── routing.py           # Routes WebSocket
│   │   ├── cron.py              # Notifications email
│   │   └── google_calendar.py   # Intégration Google Calendar
│   ├── templates/               # Templates HTML Django
│   ├── static/                  # CSS, JS
│   ├── tests/                   #  Mes Tests unitaires
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_api.py
│   ├── pytest.ini               # Configuration tests
│   └── manage.py
│
└── esmt-react/    
    └── src/
        ├── components/
        │   ├── auth/            # Login, Register
        │   ├── dashboard/       # Dashboard
        │   ├── projects/        # ProjectList, ProjectDetail, ProjectForm
        │   ├── tasks/           # TaskList, TaskForm
        │   ├── statistics/      # Statistiques et primes
        │   ├── profile/         # Profil utilisateur
        │   └── layout/          # Navbar
        ├── services/
        │   └── api.js           # Configuration Axios + JWT
        ├── context/
        │   └── AuthContext.js   # Gestion authentification
        └── App.js               # Routes React

#### Modeles de donnees 
# User 
**Champ**     | **Type**     | **Description**
username      | CharField    | Nom d utilisateur unique
email         | EmailField   | Adresse email
first_name    | CharField    | Prenom
last_name     | CharField    | Nom de famille    
role          | CharField    | etudiant ou professeur 
avatar        | ImageField   | Photo de profil  
bio           | TextField    | Biographie

# Project
**Champ**     | **Type**            | **Description**   
name          | CharField           | Nom du projet
description   | TextField           | Description
created_by    | ForeignKey          | Createur (User)
members       | ManyToManyField     | Membres du projet
created_at    | DateTimeField       | Date de creation

# Task
**Champ**     | **Type**            | **Description**   
Title         | CharField           | Titre de la tache
description   | TextField           | Description
project       | ForeignKey          | Projet associe
Deadline      | ManyToManyField     | Date limite
status        | CharField           | todo, in_progress, done
assigned_to   | ForeignKey          | Utilisateur assigne
created_by    | ForeignKey          | Createur
completed_at  | DateTimeField       | Date de competition
 
# Routes API disponibles
### Authentification
**Methode**   | **URL**              | **Description**   
POST          | /api/auth/register/  | Inscription
POST          | /api/auth/login/     | Connexion qui retourne JWT
POST          | /api/auth/refresh/   | Rafraichir le token
GET/PUT       | /api/auth/profile/   | Voir/modifier le profil

### Projets 
**Methode**   | **URL**              | **Description**   
POST          | /api/auth/register/  | Inscription
POST          | /api/auth/login/     | Connexion qui retourne JWT
POST          | /api/auth/refresh/   | Rafraichir le token
GET/PUT       | /api/auth/profile/   | Voir/modifier le profil

### Taches
**Methode**   | **URL**                        | **Description**   
GET           | /api/projects/{id}/tasks/      | Liste des taches
POST          | /api/projects/{id}/tasks/      | Créer une tâche
POST          | /api/projects/{id}/tasks/{id}/ | Modifier le statut
GET/PUT       | /api/projects/{id}/tasks/{id}/ | Supprimer une tâche

### Statistiques
**Methode**   | **URL**                        | **Description**   
GET           | /api/statistics/               | Stats + primes

# 1. Se connecter 
POST /api/auth/login/
{ "username": "votre_username", "password": "votre_password" }
# 2. Utiliser le token dans les requetes
Authorization: Bearer <access_token>

##Lancer les tests
cd esmt_tasks
pytest tests/ -v

## Roles et permissions
**Action**                       |**Etudiant**  |**Professeur**
Creer un projet                  | permi        | permi 
MOdifier son projet              | permi        | permi 
Assigner un professeur           | pas permi    | permi 
Modifier le statut de ses taches | permi        | permi 
Voir les stats de l equipe       | pas permi    | permi 
Recevoir une prime               | pas permi    | permi 
  
## Calcul des primes
**Taux dans les delais**  | **Prime**
100%                      | 100000 Fcfa
90% a 99%                 | 30000Fcfa
Moins de 90%              | pas de prime



