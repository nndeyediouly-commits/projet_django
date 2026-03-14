# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('professeur', 'Professeur'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='etudiant',
        verbose_name="Rôle"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True, blank=True,
        verbose_name="Photo de profil"
    )
    bio = models.TextField(
        blank=True, null=True,
        verbose_name="Biographie"
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_professeur(self):
        return self.role == 'professeur'

    @property
    def is_etudiant(self):
        return self.role == 'etudiant'