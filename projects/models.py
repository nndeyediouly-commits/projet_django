from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.
# projects/models.py

class Project(models.Model):
    """Un projet regroupe plusieurs tâches."""

    name = models.CharField(max_length=200, verbose_name="Nom du projet")
    description = models.TextField(blank=True, verbose_name="Description")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        verbose_name="Créateur"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=True,
        verbose_name="Membres"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Projet"
        ordering = ['-created_at']


class Task(models.Model):
    """Une tâche appartient à un projet et est assignée à un utilisateur."""

    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Projet"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")

    deadline = models.DateTimeField(verbose_name="Date limite")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="Statut"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name="Assigné à"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name="Créé par"
    )

    completed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Terminé le"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    def save(self, *args, **kwargs):
        # Enregistre automatiquement la date de completion
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_on_time(self):
        """Vérifie si la tâche a été terminée dans les délais."""
        if self.completed_at and self.deadline:
            return self.completed_at <= self.deadline
        return False

    class Meta:
        verbose_name = "Tâche"
        ordering = ['deadline']