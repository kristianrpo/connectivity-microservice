"""
URL patterns for external API endpoints.
"""

from django.urls import path
from . import external_views

urlpatterns = [
    path('citizens/<int:idCitizen>/exists/', external_views.check_citizen_exists, name='check-citizen-exists'),
]
