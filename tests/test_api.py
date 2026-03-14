# tests/test_api.py

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from projects.models import Project, Task


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def etudiant(db):
    return User.objects.create_user(
        username='etudiant1', password='Test@1234',
        email='etudiant@esmt.sn', role='etudiant'
    )


@pytest.fixture
def professeur(db):
    return User.objects.create_user(
        username='prof1', password='Test@1234',
        email='prof@esmt.sn', role='professeur'
    )


@pytest.fixture
def auth_client_prof(api_client, professeur):
    """Client API authentifié en tant que professeur."""
    response = api_client.post('/api/auth/login/', {
        'username': 'prof1',
        'password': 'Test@1234'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def auth_client_etudiant(api_client, etudiant):
    """Client API authentifié en tant qu'étudiant."""
    response = api_client.post('/api/auth/login/', {
        'username': 'etudiant1',
        'password': 'Test@1234'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


# ─────────────────────────────────────────
#  TESTS API AUTH
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestAPIAuth:

    def test_inscription_api(self, api_client):
        """L'API permet de s'inscrire."""
        response = api_client.post('/api/auth/register/', {
            'username':   'newuser',
            'first_name': 'Awa',
            'last_name':  'Ndiaye',
            'email':      'awa@esmt.sn',
            'role':       'etudiant',
            'password':   'Test@1234',
            'password2':  'Test@1234',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_api(self, api_client, etudiant):
        """L'API retourne un token JWT après connexion."""
        response = api_client.post('/api/auth/login/', {
            'username': 'etudiant1',
            'password': 'Test@1234'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_login_incorrect_api(self, api_client):
        """Un mauvais mot de passe retourne 401."""
        response = api_client.post('/api/auth/login/', {
            'username': 'inexistant',
            'password': 'mauvais'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profil_sans_token(self, api_client):
        """Sans token, le profil retourne 401."""
        response = api_client.get('/api/auth/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ─────────────────────────────────────────
#  TESTS API PROJETS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestAPIProjects:

    def test_creer_projet(self, auth_client_prof):
        """Un professeur connecté peut créer un projet via l'API."""
        response = auth_client_prof.post('/api/projects/', {
            'name':        'Projet API',
            'description': 'Test API'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Projet API'

    def test_liste_projets(self, auth_client_prof):
        """L'API retourne la liste des projets."""
        response = auth_client_prof.get('/api/projects/')
        assert response.status_code == status.HTTP_200_OK

    def test_stats_professeur(self, auth_client_prof):
        """Un professeur peut voir les statistiques."""
        response = auth_client_prof.get('/api/statistics/')
        assert response.status_code == status.HTTP_200_OK
        assert 'annual' in response.data
        assert 'quarterly' in response.data
        assert 'prime' in response.data

    def test_stats_sans_token(self, api_client):
        """Sans token, les stats retournent 401."""
        response = api_client.get('/api/statistics/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED