# models.py
from django.db import models


class Decision(models.Model):
    user_id = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    company_id = models.CharField(max_length=50)
    company_domain = models.CharField(max_length=100)
    summary = models.TextField()
    context = models.TextField()
    team = models.CharField(max_length=100)
    tags = models.CharField(max_length=250)
    source = models.CharField(max_length=50, default="slack")
    created_at = models.DateTimeField(auto_now_add=True)  # Slack, Teams, Webex, etc.
    review_flag = models.BooleanField(default=False)
    rationale = models.TextField()
    jira_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d')} | {self.username}: {self.summary[:50]}"


# Create your models here.
