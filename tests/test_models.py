# tests/test_models.py

import pytest
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from projects.models import Project, Task


@pytest.fixture
def etudiant():
    """Crée un étudiant de test."""
    return User.objects.create_user(
        username='etudiant1',
        password='Test@1234',
        email='etudiant@esmt.sn',
        role='etudiant',
        first_name='Mamadou',
        last_name='Diop'
    )


@pytest.fixture
def professeur():
    """Crée un professeur de test."""
    return User.objects.create_user(
        username='prof1',
        password='Test@1234',
        email='prof@esmt.sn',
        role='professeur',
        first_name='Ibrahima',
        last_name='Fall'
    )


@pytest.fixture
def project(professeur):
    """Crée un projet de test."""
    p = Project.objects.create(
        name='Projet Test',
        description='Description test',
        created_by=professeur
    )
    p.members.add(professeur)
    return p


@pytest.fixture
def task(project, professeur, etudiant):
    """Crée une tâche de test."""
    return Task.objects.create(
        project=project,
        title='Tâche Test',
        description='Description tâche',
        deadline=timezone.now() + timedelta(days=7),
        status='todo',
        assigned_to=etudiant,
        created_by=professeur
    )


# ─────────────────────────────────────────
#  TESTS MODÈLE USER
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestUserModel:

    def test_creation_etudiant(self, etudiant):
        """Un étudiant est bien créé avec le bon rôle."""
        assert etudiant.role == 'etudiant'
        assert etudiant.is_etudiant == True
        assert etudiant.is_professeur == False

    def test_creation_professeur(self, professeur):
        """Un professeur est bien créé avec le bon rôle."""
        assert professeur.role == 'professeur'
        assert professeur.is_professeur == True
        assert professeur.is_etudiant == False

    def test_str_user(self, etudiant):
        """La représentation string d'un user est correcte."""
        assert 'Mamadou Diop' in str(etudiant)
        assert 'Étudiant' in str(etudiant)

    def test_password_hache(self, etudiant):
        """Le mot de passe est bien hashé."""
        assert etudiant.password != 'Test@1234'
        assert etudiant.check_password('Test@1234') == True


# ─────────────────────────────────────────
#  TESTS MODÈLE PROJECT
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestProjectModel:

    def test_creation_projet(self, project, professeur):
        """Un projet est bien créé."""
        assert project.name == 'Projet Test'
        assert project.created_by == professeur

    def test_createur_est_membre(self, project, professeur):
        """Le créateur est automatiquement membre."""
        assert professeur in project.members.all()

    def test_str_projet(self, project):
        """La représentation string d'un projet est correcte."""
        assert project.name in str(project)

    def test_ajout_membre(self, project, etudiant):
        """On peut ajouter un membre au projet."""
        project.members.add(etudiant)
        assert etudiant in project.members.all()


# ─────────────────────────────────────────
#  TESTS MODÈLE TASK
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestTaskModel:

    def test_creation_tache(self, task, etudiant, project):
        """Une tâche est bien créée."""
        assert task.title == 'Tâche Test'
        assert task.status == 'todo'
        assert task.assigned_to == etudiant
        assert task.project == project

    def test_statut_par_defaut(self, task):
        """Le statut par défaut est 'todo'."""
        assert task.status == 'todo'

    def test_completion_dans_delais(self, task):
        """Une tâche terminée avant deadline est dans les délais."""
        task.status = 'done'
        task.save()
        assert task.completed_at is not None
        assert task.is_on_time == True

    def test_completion_hors_delais(self, task):
        """Une tâche terminée après deadline n'est pas dans les délais."""
        # Mettre la deadline dans le passé
        task.deadline = timezone.now() - timedelta(days=1)
        task.status = 'done'
        task.save()
        assert task.is_on_time == False

    def test_remise_en_cours(self, task):
        """Remettre une tâche en cours efface la date de completion."""
        task.status = 'done'
        task.save()
        assert task.completed_at is not None

        task.status = 'in_progress'
        task.save()
        assert task.completed_at is None

    def test_str_tache(self, task):
        """La représentation string d'une tâche est correcte."""
        assert 'Tâche Test' in str(task)