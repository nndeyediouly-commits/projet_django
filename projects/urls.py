# projects/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.project_list,    name='project_list'),
    path('create/',                        views.project_create,  name='project_create'),
    path('<int:pk>/',                      views.project_detail,  name='project_detail'),
    path('<int:pk>/edit/',                 views.project_edit,    name='project_edit'),
    path('<int:pk>/delete/',               views.project_delete,  name='project_delete'),
    path('<int:project_pk>/tasks/create/', views.task_create,     name='task_create'),
    path('tasks/',                         views.task_list,       name='task_list'),
    path('tasks/<int:pk>/edit/',           views.task_edit,       name='task_edit'),
    path('tasks/<int:pk>/delete/',         views.task_delete,     name='task_delete'),
    path('statistics/',                    views.statistics_view, name='statistics'),
    #path('google/auth/',              views.google_auth,      name='google_auth'),
    #path('google/callback/',          views.google_callback,  name='google_callback'),
    #path('tasks/<int:task_pk>/calendar/', views.add_to_calendar, name='add_to_calendar'),
]
