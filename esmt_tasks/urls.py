# esmt_tasks/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import dashboard_view

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('accounts.urls')),
    path('dashboard/',  dashboard_view, name='dashboard'),
    path('',            dashboard_view, name='home'),
    path('projects/',   include('projects.urls')),

    # ← API REST (nouvelle ligne)
    path('api/', include('projects.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
