from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path("captureDecision", views.slack_decision, name="slack_decision"),
    path("interactivity", views.slack_interactivity, name="slack_decision"),
    path("command", views.slack_command, name="command"),
    path(
        "api/decisions",
        views.get_decisions_by_company,
        name="get_decisions_by_company",
    ),
    path(
        "api/analytics",
        views.team_audit_summary,
        name="get_team_audit_summary",
    ),
    path(
        "api/getTeams",
        views.decision_summary_by_team,
        name="get_decision_summary_by_team",
    ),
    path(
        "api/decisions/update/<int:id>", views.update_decision, name="update-decision"
    ),
    path(
        "api/decisions/delete/<int:id>", views.delete_decision, name="update-decision"
    ),
]
