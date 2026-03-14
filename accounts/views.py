# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, PasswordChangeCustomForm


def register_view(request):
    """
    Vue d'inscription.
    GET  → affiche le formulaire vide.
    POST → valide, crée l'utilisateur et redirige vers le dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connecte directement après inscription
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé.")
            return redirect('dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Vue de connexion.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bon retour, {user.first_name or user.username} !")
            # Redirige vers la page (si l'utilisateur a été renvoyé vers login)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Vue de déconnexion (POST uniquement pour la sécurité).
    """
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')


@login_required
def profile_view(request):
    """
    Vue du profil : affiche et met à jour les infos de l'utilisateur.
    """
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = PasswordChangeCustomForm()

    if request.method == 'POST':

        # Soumission du formulaire de profil
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(
                request.POST,
                request.FILES,   # pour l'avatar (image)
                instance=request.user
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profil mis à jour avec succès !")
                return redirect('profile')

        # Soumission du formulaire de mot de passe
        elif 'change_password' in request.POST:
            password_form = PasswordChangeCustomForm(request.POST)
            if password_form.is_valid():
                user = request.user
                old_pwd = password_form.cleaned_data['old_password']
                new_pwd = password_form.cleaned_data['new_password1']

                if user.check_password(old_pwd):
                    user.set_password(new_pwd)
                    user.save()
                    # Maintient la session active après changement de mot de passe
                    update_session_auth_hash(request, user)
                    messages.success(request, "Mot de passe modifié avec succès !")
                    return redirect('profile')
                else:
                    messages.error(request, "L'ancien mot de passe est incorrect.")

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def dashboard_view(request):
    """
    Tableau de bord principal.
    Affiche les projets et tâches de l'utilisateur connecté.
    """
    from projects.models import Project, Task

    # Projets dont l'utilisateur est membre OU créateur
    user_projects = Project.objects.filter(
        members=request.user
    ) | Project.objects.filter(
        created_by=request.user
    )
    user_projects = user_projects.distinct()

    # Tâches assignées à l'utilisateur
    my_tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('project').order_by('deadline')

    # Statistiques rapides pour le dashboard
    stats = {
        'total_projects': user_projects.count(),
        'total_tasks':    my_tasks.count(),
        'tasks_done':     my_tasks.filter(status='done').count(),
        'tasks_todo':     my_tasks.filter(status='todo').count(),
        'tasks_inprog':   my_tasks.filter(status='in_progress').count(),
    }

    context = {
        'projects': user_projects,
        'my_tasks': my_tasks[:5],   # 5 tâches les plus proches
        'stats':    stats,
    }
    return render(request, 'accounts/dashboard.html', context)