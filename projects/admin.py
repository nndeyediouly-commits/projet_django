# projects/admin.py

from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter  = ['created_at']
    search_fields = ['name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status', 'deadline']
    list_filter  = ['status', 'deadline']
    search_fields = ['title']
    search_fields: Any = ['title']