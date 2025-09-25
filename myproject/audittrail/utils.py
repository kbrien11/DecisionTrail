import requests
from decouple import config
import requests


SLACK_BOT_TOKEN = config("SLACK_BOT_TOKEN")


def open_decision_modal(trigger_id, decision_text, user_id, username):
    modal_payload = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Capture Decision"},
            "submit": {"type": "plain_text", "text": "Save"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "section",
                    "block_id": "user_info",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Captured by:* <@{user_id}> ({username})",
                    },
                },
                {
                    "type": "input",
                    "block_id": "summary",
                    "label": {"type": "plain_text", "text": "Decision Summary"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "summary_input",
                        "initial_value": decision_text
                        if decision_text
                        else "No summary provided",
                    },
                },
                {
                    "type": "input",
                    "block_id": "context",
                    "label": {"type": "plain_text", "text": "Strategic Context"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "context_input",
                        "multiline": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "tags",
                    "label": {"type": "plain_text", "text": "Tags (comma-separated)"},
                    "element": {"type": "plain_text_input", "action_id": "tags_input"},
                },
                {
                    "type": "input",
                    "block_id": "team",
                    "label": {"type": "plain_text", "text": "Team"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "team_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "e.g. Engineering, Finance, Product",
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "review_flag",
                    "label": {"type": "plain_text", "text": "Flag for Review?"},
                    "element": {
                        "type": "checkboxes",
                        "action_id": "review_checkbox",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Needs follow-up or review",
                                },
                                "value": "review",
                            }
                        ],
                    },
                },
                {
                    "type": "input",
                    "block_id": "rationale",
                    "label": {"type": "plain_text", "text": "Rationale"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "rationale_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "What led to this decision?",
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "jira",
                    "label": {"type": "plain_text", "text": "Related Jira URL"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "jira_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "https://yourcompany.atlassian.net/browse/JIRA-1234",
                        },
                    },
                },
            ],
        },
    }

    print(trigger_id, decision_text, username)

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://slack.com/api/views.open", json=modal_payload, headers=headers
    )

    return response.json()
