# tests/test_views.py

import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from projects.models import Project, Task


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
def project(professeur):
    p = Project.objects.create(
        name='Projet Test',
        created_by=professeur
    )
    p.members.add(professeur)
    return p


# ─────────────────────────────────────────
#  TESTS AUTHENTIFICATION
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestAuthentification:

    def test_page_login_accessible(self, client):
        """La page de login est accessible sans être connecté."""
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_page_register_accessible(self, client):
        """La page d'inscription est accessible."""
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_login_correct(self, client, etudiant):
        """Un utilisateur peut se connecter avec les bons identifiants."""
        response = client.post(reverse('login'), {
            'username': 'etudiant1',
            'password': 'Test@1234'
        })
        assert response.status_code == 302  # redirection après login
        assert response.url == '/dashboard/'

    def test_login_incorrect(self, client):
        """Un mauvais mot de passe empêche la connexion."""
        response = client.post(reverse('login'), {
            'username': 'etudiant1',
            'password': 'mauvais_mdp'
        })
        assert response.status_code == 200  # reste sur la page login

    def test_inscription(self, client):
        """Un nouvel utilisateur peut s'inscrire."""
        response = client.post(reverse('register'), {
            'username':   'nouveau_user',
            'first_name': 'Fatou',
            'last_name':  'Sow',
            'email':      'fatou@esmt.sn',
            'role':       'etudiant',
            'password1':  'Test@1234',
            'password2':  'Test@1234',
        })
        assert response.status_code == 302
        assert User.objects.filter(username='nouveau_user').exists()

    def test_dashboard_redirige_si_non_connecte(self, client):
        """Le dashboard redirige vers login si non connecté."""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302
        assert '/login/' in response.url


# ─────────────────────────────────────────
#  TESTS PROJETS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestProjectViews:

    def test_liste_projets_connecte(self, client, professeur):
        """Un utilisateur connecté peut voir la liste des projets."""
        client.login(username='prof1', password='Test@1234')
        response = client.get(reverse('project_list'))
        assert response.status_code == 200

    def test_creation_projet(self, client, professeur):
        """Un utilisateur connecté peut créer un projet."""
        client.login(username='prof1', password='Test@1234')
        response = client.post(reverse('project_create'), {
            'name':        'Nouveau Projet',
            'description': 'Description',
            'members':     []
        })
        assert response.status_code == 302
        assert Project.objects.filter(name='Nouveau Projet').exists()

    def test_modification_projet_createur(self, client, professeur, project):
        """Le créateur peut modifier son projet."""
        client.login(username='prof1', password='Test@1234')
        response = client.post(
            reverse('project_edit', kwargs={'pk': project.pk}),
            {'name': 'Projet Modifié', 'description': 'Nouvelle desc', 'members': []}
        )
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.name == 'Projet Modifié'

    def test_modification_projet_non_createur(self, client, etudiant, project):
        """Un non-créateur ne peut pas modifier le projet."""
        client.login(username='etudiant1', password='Test@1234')
        response = client.post(
            reverse('project_edit', kwargs={'pk': project.pk}),
            {'name': 'Projet Piraté', 'description': '', 'members': []}
        )
        # Redirige avec message d'erreur
        project.refresh_from_db()
        assert project.name != 'Projet Piraté'

    def test_suppression_projet_createur(self, client, professeur, project):
        """Le créateur peut supprimer son projet."""
        client.login(username='prof1', password='Test@1234')
        response = client.post(
            reverse('project_delete', kwargs={'pk': project.pk})
        )
        assert response.status_code == 302
        assert not Project.objects.filter(pk=project.pk).exists()