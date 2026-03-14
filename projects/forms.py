# projects/forms.py

from django import forms
from .models import Project, Task
from accounts.models import User


class ProjectForm(forms.ModelForm):
    """Formulaire de création/modification d'un projet."""

    class Meta:
        model = Project
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du projet'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du projet...'
            }),
            'members': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        # On récupère l'utilisateur connecté pour l'exclure des membres
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # On ne peut pas s'ajouter soi-même comme membre
            self.fields['members'].queryset = User.objects.exclude(pk=self.user.pk)


class TaskForm(forms.ModelForm):
    """Formulaire de création/modification d'une tâche."""

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la tâche'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description...'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'   # input calendrier HTML5
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        if self.project:
            # On ne peut assigner qu'aux membres du projet
            members = self.project.members.all()
            # Inclure aussi le créateur du projet
            creator = User.objects.filter(pk=self.project.created_by.pk)
            assignable = (members | creator).distinct()

            # RÈGLE MÉTIER : un étudiant ne peut pas assigner un professeur
            if self.current_user and self.current_user.is_etudiant:
                assignable = assignable.filter(role='etudiant')

            self.fields['assigned_to'].queryset = assignable


class TaskStatusForm(forms.ModelForm):
    """
    Formulaire simplifié pour mettre à jour uniquement le statut.
    Utilisé par les membres assignés à une tâche.
    """
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }