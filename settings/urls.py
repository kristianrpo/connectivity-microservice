"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/connectivity/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/connectivity/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/connectivity/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # External API (for auth-microservice integration)
    # Auth-microservice calls this with OAuth2 Client Credentials token
    path('api/connectivity/external/', include('apps.citizen_validation.urls')),
    
    # Health check
    path('api/connectivity/health/', include('health_check.urls')),
    
    # Prometheus metrics
    path('api/connectivity/', include('django_prometheus.urls')),
]
