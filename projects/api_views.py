# projects/api_views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone

from .models import Project, Task
from accounts.models import User
from .serializers import (
    ProjectSerializer, TaskSerializer,
    UserSerializer, RegisterSerializer
)


# ─────────────────────────────────────────
#  AUTHENTIFICATION
# ─────────────────────────────────────────

class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Crée un nouveau compte utilisateur.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Génère les tokens JWT directement après inscription
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    """
    POST /api/auth/login/
    Connecte un utilisateur et retourne les tokens JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': 'Identifiants incorrects.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        })


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/auth/profile/  → voir son profil
    PUT  /api/auth/profile/  → modifier son profil
    """
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─────────────────────────────────────────
#  PROJETS
# ─────────────────────────────────────────

class ProjectViewSet(viewsets.ModelViewSet):
    """
    GET    /api/projects/          → liste des projets
    POST   /api/projects/          → créer un projet
    GET    /api/projects/{id}/     → détail d'un projet
    PUT    /api/projects/{id}/     → modifier un projet
    DELETE /api/projects/{id}/     → supprimer un projet
    """
    serializer_class   = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retourne uniquement les projets de l'utilisateur connecté
        return Project.objects.filter(
            Q(created_by=self.request.user) | Q(members=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # Le créateur est automatiquement l'utilisateur connecté
        project = serializer.save(created_by=self.request.user)
        project.members.add(self.request.user)

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user != project.created_by:
            return Response(
                {'error': 'Seul le créateur peut modifier ce projet.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user != project.created_by:
            return Response(
                {'error': 'Seul le créateur peut supprimer ce projet.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ─────────────────────────────────────────
#  TÂCHES
# ─────────────────────────────────────────

class TaskViewSet(viewsets.ModelViewSet):
    """
    GET    /api/projects/{project_id}/tasks/       → liste des tâches
    POST   /api/projects/{project_id}/tasks/       → créer une tâche
    GET    /api/projects/{project_id}/tasks/{id}/  → détail d'une tâche
    PUT    /api/projects/{project_id}/tasks/{id}/  → modifier une tâche
    DELETE /api/projects/{project_id}/tasks/{id}/  → supprimer une tâche
    """
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            project__id=self.kwargs['project_pk']
        ).select_related('assigned_to', 'created_by')

    def perform_create(self, serializer):
        project = Project.objects.get(pk=self.kwargs['project_pk'])

        # Vérification créateur
        if self.request.user != project.created_by:
            raise PermissionError("Seul le créateur peut ajouter des tâches.")

        # Vérification : étudiant ne peut pas assigner un professeur
        assigned_to = serializer.validated_data.get('assigned_to')
        if self.request.user.is_etudiant and assigned_to and assigned_to.is_professeur:
            raise PermissionError("Un étudiant ne peut pas assigner un professeur.")

        serializer.save(created_by=self.request.user, project=project)

    def update(self, request, *args, **kwargs):
        task       = self.get_object()
        project    = task.project
        is_creator = (request.user == project.created_by)
        is_assigned = (request.user == task.assigned_to)

        if not is_creator and not is_assigned:
            return Response(
                {'error': 'Permission refusée.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Membre assigné → uniquement le statut
        if not is_creator and is_assigned:
            allowed = {'status': request.data.get('status')}
            serializer = self.get_serializer(task, data=allowed, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if request.user != task.project.created_by:
            return Response(
                {'error': 'Seul le créateur du projet peut supprimer des tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ─────────────────────────────────────────
#  STATISTIQUES
# ─────────────────────────────────────────

class StatisticsAPIView(generics.GenericAPIView):
    """
    GET /api/statistics/
    Retourne les stats personnelles + équipe (professeurs).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now   = timezone.now()
        year  = now.year
        quarter = (now.month - 1) // 3 + 1
        quarter_start_month = (quarter - 1) * 3 + 1
        quarter_start = timezone.datetime(
            year, quarter_start_month, 1,
            tzinfo=timezone.get_current_timezone()
        )
        year_start = timezone.datetime(year, 1, 1, tzinfo=timezone.get_current_timezone())
        year_end   = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())

        def get_stats(user, start, end):
            tasks    = Task.objects.filter(assigned_to=user, deadline__gte=start, deadline__lt=end)
            total    = tasks.count()
            done     = tasks.filter(status='done').count()
            on_time  = sum(1 for t in tasks.filter(status='done') if t.is_on_time)
            return {
                'total':       total,
                'done':        done,
                'on_time':     on_time,
                'pct_done':    round((done / total * 100) if total > 0 else 0, 1),
                'pct_on_time': round((on_time / total * 100) if total > 0 else 0, 1),
            }

        my_annual    = get_stats(request.user, year_start, year_end)
        my_quarterly = get_stats(request.user, quarter_start, now)

        # Calcul prime
        prime = 0
        if request.user.is_professeur:
            if my_annual['pct_on_time'] == 100:
                prime = 100000
            elif my_annual['pct_on_time'] >= 90:
                prime = 30000

        response_data = {
            'year':         year,
            'quarter':      quarter,
            'annual':       my_annual,
            'quarterly':    my_quarterly,
            'prime':        prime,
            'team_stats':   []
        }

        # Stats équipe pour les professeurs
        if request.user.is_professeur:
            team = []
            for prof in User.objects.filter(role='professeur'):
                stats = get_stats(prof, year_start, year_end)
                p = 0
                if stats['pct_on_time'] == 100:
                    p = 100000
                elif stats['pct_on_time'] >= 90:
                    p = 30000
                team.append({
                    'user':  UserSerializer(prof).data,
                    'stats': stats,
                    'prime': p
                })
            response_data['team_stats'] = team

        return Response(response_data)