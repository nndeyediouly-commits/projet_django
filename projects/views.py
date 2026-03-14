from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
# Create your views here.
# projects/views.py
from .models import Project, Task
from .forms import ProjectForm, TaskForm, TaskStatusForm
from accounts.models import User


# ─────────────────────────────────────────
#  PROJETS
# ─────────────────────────────────────────

@login_required
def project_list(request):
    """Liste de tous les projets de l'utilisateur."""

    # Projets créés par l'utilisateur OU dont il est membre
    projects = Project.objects.filter(
        Q(created_by=request.user) | Q(members=request.user)
    ).distinct().annotate(task_count=Count('tasks'))

    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    """Créer un nouveau projet."""

    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user   # le créateur = utilisateur connecté
            project.save()
            form.save_m2m()   # sauvegarde les membres (ManyToMany)
            # Ajouter automatiquement le créateur comme membre
            project.members.add(request.user)
            messages.success(request, f'Projet "{project.name}" créé avec succès !')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(user=request.user)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'action': 'Créer'
    })


@login_required
def project_detail(request, pk):
    """Détail d'un projet avec ses tâches et filtres."""

    project = get_object_or_404(Project, pk=pk)

    # Vérifier que l'utilisateur a accès au projet
    if request.user != project.created_by and request.user not in project.members.all():
        messages.error(request, "Vous n'avez pas accès à ce projet.")
        return redirect('project_list')

    # Récupérer les tâches avec filtres
    tasks = project.tasks.all().select_related('assigned_to')

    # Filtre par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Filtre par utilisateur assigné
    user_filter = request.GET.get('user', '')
    if user_filter:
        tasks = tasks.filter(assigned_to__id=user_filter)

    is_creator = (request.user == project.created_by)

    context = {
        'project':       project,
        'tasks':         tasks,
        'is_creator':    is_creator,
        'status_filter': status_filter,
        'user_filter':   user_filter,
        'members':       project.members.all(),
        'status_choices': Task.STATUS_CHOICES,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_edit(request, pk):
    """Modifier un projet (créateur uniquement)."""

    project = get_object_or_404(Project, pk=pk)

    # Seul le créateur peut modifier
    if request.user != project.created_by:
        messages.error(request, "Seul le créateur peut modifier ce projet.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Projet modifié avec succès !")
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project, user=request.user)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'project': project,
        'action': 'Modifier'
    })


@login_required
def project_delete(request, pk):
    """Supprimer un projet (créateur uniquement)."""

    project = get_object_or_404(Project, pk=pk)

    if request.user != project.created_by:
        messages.error(request, "Seul le créateur peut supprimer ce projet.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        project.delete()
        messages.success(request, "Projet supprimé.")
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {
        'project': project
    })


# ─────────────────────────────────────────
#  TÂCHES
# ─────────────────────────────────────────

@login_required
def task_list(request):
    """Tâches avec recherche avancée et filtres."""
    tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('project').order_by('deadline')

    # Filtre par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Filtre par projet
    project_filter = request.GET.get('project', '')
    if project_filter:
        tasks = tasks.filter(project__id=project_filter)

    # Filtre par date limite
    deadline_filter = request.GET.get('deadline', '')
    if deadline_filter == 'today':
        tasks = tasks.filter(deadline__date=timezone.now().date())
    elif deadline_filter == 'week':
        tasks = tasks.filter(
            deadline__date__lte=timezone.now().date() + timedelta(days=7)
        )
    elif deadline_filter == 'overdue':
        tasks = tasks.filter(
            deadline__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )

    # Recherche par mot-clé
    search = request.GET.get('search', '')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(project__name__icontains=search)
        )

    # Projets de l'utilisateur pour le filtre
    user_projects = Project.objects.filter(
        Q(created_by=request.user) | Q(members=request.user)
    ).distinct()

    return render(request, 'projects/task_list.html', {
        'tasks':          tasks,
        'status_filter':  status_filter,
        'project_filter': project_filter,
        'deadline_filter': deadline_filter,
        'search':         search,
        'status_choices': Task.STATUS_CHOICES,
        'user_projects':  user_projects,
    })

@login_required
def task_create(request, project_pk):
    """Créer une tâche dans un projet (créateur du projet uniquement)."""

    project = get_object_or_404(Project, pk=project_pk)

    # Seul le créateur du projet peut ajouter des tâches
    if request.user != project.created_by:
        messages.error(request, "Seul le créateur du projet peut ajouter des tâches.")
        return redirect('project_detail', pk=project_pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project, current_user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.project    = project
            task.created_by = request.user
            task.save()
            messages.success(request, f'Tâche "{task.title}" créée !')
            return redirect('project_detail', pk=project_pk)
    else:
        form = TaskForm(project=project, current_user=request.user)

    return render(request, 'projects/task_form.html', {
        'form':    form,
        'project': project,
        'action':  'Créer'
    })


@login_required
def task_edit(request, pk):
    """
    Modifier une tâche.
    - Le créateur du projet → peut tout modifier.
    - L'utilisateur assigné → peut uniquement changer le statut.
    """
    task = get_object_or_404(Task, pk=pk)
    project = task.project

    is_creator  = (request.user == project.created_by)
    is_assigned = (request.user == task.assigned_to)

    if not is_creator and not is_assigned:
        messages.error(request, "Vous n'avez pas la permission de modifier cette tâche.")
        return redirect('project_detail', pk=project.pk)

    if request.method == 'POST':
        if is_creator:
            form = TaskForm(request.POST, instance=task,
                            project=project, current_user=request.user)
        else:
            # Membre assigné : seulement le statut
            form = TaskStatusForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            messages.success(request, "Tâche mise à jour !")
            return redirect('project_detail', pk=project.pk)
    else:
        if is_creator:
            form = TaskForm(instance=task, project=project, current_user=request.user)
        else:
            form = TaskStatusForm(instance=task)

    return render(request, 'projects/task_form.html', {
        'form':        form,
        'task':        task,
        'project':     project,
        'is_creator':  is_creator,
        'action':      'Modifier'
    })


@login_required
def task_delete(request, pk):
    """Supprimer une tâche (créateur du projet uniquement)."""

    task    = get_object_or_404(Task, pk=pk)
    project = task.project

    if request.user != project.created_by:
        messages.error(request, "Seul le créateur du projet peut supprimer des tâches.")
        return redirect('project_detail', pk=project.pk)

    if request.method == 'POST':
        task.delete()
        messages.success(request, "Tâche supprimée.")
        return redirect('project_detail', pk=project.pk)

    return render(request, 'projects/task_confirm_delete.html', {
        'task': task
    })


# ─────────────────────────────────────────
#  STATISTIQUES & PRIMES
# ─────────────────────────────────────────

@login_required
def statistics_view(request):
    """
    Statistiques trimestrielles et annuelles.
    Calcul des primes pour les professeurs.
    """
    now   = timezone.now()
    year  = now.year

    # Déterminer le trimestre actuel
    quarter = (now.month - 1) // 3 + 1
    quarter_start_month = (quarter - 1) * 3 + 1
    quarter_start = timezone.datetime(year, quarter_start_month, 1,
                                      tzinfo=timezone.get_current_timezone())

    def get_stats_for_user(user, start_date, end_date):
        """Calcule les stats d'un utilisateur sur une période."""
        tasks = Task.objects.filter(
            assigned_to=user,
            deadline__gte=start_date,
            deadline__lt=end_date
        )
        total     = tasks.count()
        done      = tasks.filter(status='done').count()
        on_time   = sum(1 for t in tasks.filter(status='done') if t.is_on_time)
        pct_done  = round((done / total * 100) if total > 0 else 0, 1)
        pct_time  = round((on_time / total * 100) if total > 0 else 0, 1)
        return {
            'total': total, 'done': done,
            'on_time': on_time,
            'pct_done': pct_done,
            'pct_on_time': pct_time
        }

    # Stats personnelles
    year_start    = timezone.datetime(year, 1, 1, tzinfo=timezone.get_current_timezone())
    year_end      = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())

    my_annual     = get_stats_for_user(request.user, year_start, year_end)
    my_quarterly  = get_stats_for_user(request.user, quarter_start, now)

    # Calcul de la prime (uniquement pour les professeurs)
    prime = 0
    if request.user.is_professeur:
        pct = my_annual['pct_on_time']
        if pct == 100:
            prime = 100000
        elif pct >= 90:
            prime = 30000

    # Stats de toute l'équipe (visibles par les professeurs uniquement)
    team_stats = []
    if request.user.is_professeur:
        professors = User.objects.filter(role='professeur')
        for prof in professors:
            stats = get_stats_for_user(prof, year_start, year_end)
            p = 0
            if stats['pct_on_time'] == 100:
                p = 100000
            elif stats['pct_on_time'] >= 90:
                p = 30000
            team_stats.append({
                'user': prof,
                'stats': stats,
                'prime': p
            })

    context = {
        'my_annual':    my_annual,
        'my_quarterly': my_quarterly,
        'prime':        prime,
        'quarter':      quarter,
        'year':         year,
        'team_stats':   team_stats,
    }
    return render(request, 'projects/statistics.html', context)
from django.shortcuts import redirect
#from .google_calendar import get_google_flow, add_task_to_calendar
import json

@login_required
def google_auth(request):
    """Redirige vers Google pour autorisation."""
    flow = get_google_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['google_state'] = state
    return redirect(auth_url)


@login_required
def google_callback(request):
    """Reçoit le code OAuth2 de Google."""
    flow = get_google_flow()
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Sauvegarder les credentials dans la session
    request.session['google_credentials'] = {
        'token':         credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri':     credentials.token_uri,
        'client_id':     credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes':        credentials.scopes,
    }
    messages.success(request, "Google Calendar connecté avec succès !")
    return redirect('task_list')


@login_required
def add_to_calendar(request, task_pk):
    """Ajoute une tâche à Google Calendar."""
    task = get_object_or_404(Task, pk=task_pk)
    credentials = request.session.get('google_credentials')

    if not credentials:
        messages.warning(request, "Connectez d'abord votre Google Calendar.")
        return redirect('google_auth')

    link = add_task_to_calendar(credentials, task)
    messages.success(request, f"Tâche ajoutée à Google Calendar !")
    return redirect('project_detail', pk=task.project.pk)