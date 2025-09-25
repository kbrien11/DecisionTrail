# views.py
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
from .utils import open_decision_modal
from .models import Decision
from rest_framework.decorators import action, api_view
from django.core.cache import cache
from decouple import config


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
