# projects/cron.py
from projects.cron import send_deadline_notifications
send_deadline_notifications()
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Task


def send_deadline_notifications():
    """
    Envoie un email aux utilisateurs dont les tâches
    arrivent à échéance dans les 24h ou 48h.
    """
    now = timezone.now()

    # Tâches qui arrivent à échéance dans 48h
    deadline_soon = Task.objects.filter(
        deadline__gte=now,
        deadline__lte=now + timedelta(hours=48),
        status__in=['todo', 'in_progress']
    ).select_related('assigned_to', 'project')

    # Grouper les tâches par utilisateur
    tasks_by_user = {}
    for task in deadline_soon:
        if task.assigned_to:
            user = task.assigned_to
            if user not in tasks_by_user:
                tasks_by_user[user] = []
            tasks_by_user[user].append(task)

    # Envoyer un email à chaque utilisateur
    for user, tasks in tasks_by_user.items():
        if not user.email:
            continue

        # Construire le message
        task_list = '\n'.join([
            f"- {task.title} (Projet: {task.project.name}) "
            f"— Échéance: {task.deadline.strftime('%d/%m/%Y à %H:%M')}"
            for task in tasks
        ])

        message = f"""
Bonjour {user.first_name or user.username},

Vous avez {len(tasks)} tâche(s) qui arrivent bientôt à échéance :

{task_list}

Connectez-vous à ESMT Tasks pour les consulter :
http://127.0.0.1:8004/projects/tasks/

Cordialement,
L'équipe ESMT Tasks
        """

        send_mail(
            subject=f' {len(tasks)} tâche(s) arrivent à échéance bientôt !',
            message=message,
            from_email=None,  # utilise DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            fail_silently=True,
        )
        print(f"Email envoyé à {user.email} ({len(tasks)} tâches)")