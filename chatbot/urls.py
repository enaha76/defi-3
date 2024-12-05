from django.urls import path
from .views import agent_query

urlpatterns = [
    path('agent_query/', agent_query, name='agent_query'),
]
