# projects/api_urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

# Le router génère automatiquement toutes les URLs CRUD
router = DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet, basename='api-project')

urlpatterns = [
    # Auth
    path('auth/register/', api_views.RegisterAPIView.as_view(),  name='api-register'),
    path('auth/login/',    api_views.LoginAPIView.as_view(),     name='api-login'),
    path('auth/refresh/',  TokenRefreshView.as_view(),           name='api-token-refresh'),
    path('auth/profile/',  api_views.ProfileAPIView.as_view(),   name='api-profile'),

    # Projets + Tâches
    path('', include(router.urls)),
    path(
        'projects/<int:project_pk>/tasks/',
        api_views.TaskViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='api-task-list'
    ),
    path(
        'projects/<int:project_pk>/tasks/<int:pk>/',
        api_views.TaskViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy'
        }),
        name='api-task-detail'
    ),

    # Statistiques
    path('statistics/', api_views.StatisticsAPIView.as_view(), name='api-statistics'),
]