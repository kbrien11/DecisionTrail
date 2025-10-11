# views.py
from collections import defaultdict
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count, Q
import requests
from rest_framework import status
from .serializers import PaginatorSerializer
from .utils import open_decision_modal, get_user_teams, verify_token
from .models import Decision
from rest_framework.decorators import action, api_view
from django.core.cache import cache
from decouple import config
from django.core.paginator import Paginator


SLACK_BOT_TOKEN = config("SLACK_BOT_TOKEN")


@csrf_exempt
def slack_decision(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        username = request.POST.get("user_name")
        channel_id = request.POST.get("channel_id")
        channel_name = request.POST.get("channel_name")
        text = request.POST.get("text")
        company = request.POST.get("domain")

        Decision.objects.create(
            user_id=user_id,
            username=username,
            channel_id=channel_id,
            channel_name=channel_name,
            summary=text,
            confidence=3,
            source="slack",
        )

        return JsonResponse(
            {"response_type": "ephemeral", "text": f"✅ Decision captured: *{text}*"}
        )


@csrf_exempt
def slack_interactivity(request):
    if request.method == "POST":
        payload = json.loads(request.POST.get("payload"))
        print(payload)

        if payload["type"] == "block_actions":
            trigger_id = payload["trigger_id"]
            user_id = payload["user"]["id"]
            username = payload["user"].get("username") or payload["user"].get("name")

            decision_text = cache.get(f"decision_text_{user_id}", "")
            print(f"[CACHE GET] decision_text_{user_id} = {decision_text}")

            open_decision_modal(trigger_id, decision_text, user_id, username)
            return JsonResponse({})  # ✅ This handles block_actions

        elif payload["type"] == "view_submission":
            user_id = payload["user"]["id"]
            username = payload["user"].get("username") or payload["user"].get("name")
            company_id = payload["team"]["id"]
            company_domain = payload["team"]["domain"]

            state = payload["view"]["state"]["values"]

            summary = state["summary"]["summary_input"]["value"]
            context = state["context"]["context_input"]["value"]
            team = state["team"]["team_input"]["value"]
            rationale = state["rationale"]["rationale_input"]["value"]
            jira_url = state["jira"]["jira_input"]["value"]
            tags = state["tags"]["tags_input"]["value"]
            state = payload["view"]["state"]["values"]

            # Check if the checkbox was selected
            selected_options = (
                state.get("review_flag", {})
                .get("review_checkbox", {})
                .get("selected_options", [])
            )

            # If selected, get the value
            review_flag = bool(selected_options)

            Decision.objects.create(
                user_id=user_id,
                username=username,
                company_id=company_id,
                company_domain=company_domain,
                summary=summary,
                context=context,
                team=team,
                tags=tags,
                source="slack",
                review_flag=review_flag,
                rationale=rationale,
                jira_url=jira_url,
            )

        # Handle modal submission here
        return JsonResponse({"response_action": "clear"})  # ✅ Required

    # ✅ Catch-all fallback for other methods or types
    return JsonResponse({"status": "ignored"})


@csrf_exempt
def slack_command(request):
    user_id = request.POST.get("user_id")  # ✅ Use user_id instead of username

    decision_text = request.POST.get("text")

    # Store decision text in cache for 5 minutes
    cache.set(f"decision_text_{user_id}", decision_text, timeout=300)

    # Respond with button
    return JsonResponse(
        {
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Want to capture this decision for strategic recall?",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Capture Decision"},
                            "action_id": "open_decision_modal",
                        }
                    ],
                },
            ],
        }
    )


@api_view(["GET"])
def get_decisions_by_company(request):
    company_domain = request.GET.get("company_domain")
    project = request.GET.get("project")
    page_number = int(request.GET.get("page", 1))  # default to page 1
    page_size = int(request.GET.get("page_size", 2))
    auth_token = request.COOKIES.get("authToken")  # default to 2 per page

    if not company_domain:
        return JsonResponse({"error": "Missing company_domain"}, status=400)

    if not auth_token or not verify_token(auth_token):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user_teams = get_user_teams(auth_token)

    # Start with base queryset
    decisions = Decision.objects.filter(company_domain=company_domain, project=project)

    # Apply dynamic filters
    allowed_filters = {
        "tags": "tags__icontains",
        "team": "team__icontains",
        "username": "username__icontains",
        "context": "context__icontains",
        "rationale": "rationale__icontains",
    }
    for param, lookup in allowed_filters.items():
        value = request.GET.get(param)
        if value:
            # Cast booleans and numbers if needed
            if param == "review_flag":
                value = value.lower() == "true"
            elif param == "confidence":
                try:
                    value = int(value)
                except ValueError:
                    continue
            decisions = decisions.filter(**{lookup: value})

    paginator = Paginator(decisions.order_by("-created_at"), page_size)
    page_obj = paginator.get_page(page_number)

    data = [
        {
            "id": d.id,
            "summary": d.summary,
            "context": d.context,
            "tags": d.tags,
            "team": d.team,
            "review_flag": d.review_flag,
            "jira_url": d.jira_url,
            "created_at": d.created_at.isoformat(),
            "username": d.username,
            "rationale": d.rationale,
        }
        for d in page_obj
    ]

    return JsonResponse(
        {
            "decisions": data,
            "projects": user_teams,
            "status": status.HTTP_200_OK,
            "page_size": page_size,
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        },
        status=200,
    )


@api_view(["GET"])
def team_audit_summary(request):
    company_domain = request.GET.get("company_domain")
    project = request.GET.get("project")
    auth_token = request.COOKIES.get("authToken")

    print(auth_token)

    # if not auth_token or not verify_token(auth_token):
    #     return JsonResponse({"error": "Unauthorized"}, status=401)
    if not company_domain:
        return JsonResponse({"error": "Missing company_domain"}, status=400)

    # Aggregate counts by team and status
    teams = (
        Decision.objects.filter(company_domain=company_domain, project=project)
        .values("team")
        .annotate(
            Open=Count("id", filter=Q(status="open")),
            Closed=Count("id", filter=Q(status="closed")),
        )
        .order_by("team")
    )

    return JsonResponse({"teams": list(teams), "company": company_domain}, status=200)


@api_view(["GET"])
def decision_summary_by_team(request):
    company_domain = request.GET.get("company_domain")
    project = request.GET.get("project")

    auth_token = request.COOKIES.get("authToken")

    # if not auth_token or not verify_token(auth_token):
    #     return JsonResponse({"error": "Unauthorized"}, status=401)

    if not company_domain:
        return JsonResponse({"error": "Missing company_domain"}, status=400)

    decisions = Decision.objects.filter(company_domain=company_domain, project=project)

    team_data = defaultdict(
        lambda: {"team_name": "", "decision_count": 0, "tags": set()}
    )

    for decision in decisions:
        team_name = decision.team
        tag_list = [tag.strip() for tag in decision.tags.split(",") if tag.strip()]

        team_data[team_name]["team_name"] = team_name
        team_data[team_name]["decision_count"] += 1
        team_data[team_name]["tags"].update(tag_list)

    result = [
        {
            "name": data["team_name"],
            "count": data["decision_count"],
            "tags": sorted(data["tags"]),
        }
        for data in team_data.values()
    ]

    return JsonResponse({"data": result})
