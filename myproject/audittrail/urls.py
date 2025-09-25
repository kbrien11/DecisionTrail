from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path("captureDecision", views.slack_decision, name="slack_decision"),
    path("interactivity", views.slack_interactivity, name="slack_decision"),
    path("command", views.slack_command, name="command"),
]
