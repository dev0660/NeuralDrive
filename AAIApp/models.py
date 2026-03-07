from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import re

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_admin_user = models.BooleanField(default=True)
    monthly_seconds_used = models.IntegerField(default=0)  # Track seconds used per month
    dealership = models.ForeignKey(
        'Dealership', on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )

    def reset_monthly_usage_if_needed(self):
        # Optionally add logic here to reset usage each month
        pass

    def is_over_usage_limit(self):
        return self.monthly_seconds_used >= 24000  # 400 minutes in seconds

    def __str__(self):
        return self.username
    
class CallRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assistant_name = models.CharField(max_length=100)
    call_id = models.CharField(max_length=255, unique=True)  # <--- NEW
    timestamp = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(null=True, blank=True)
    success_evaluation = models.TextField()
    summary = models.TextField()
    transcript = models.TextField()
    recording_url = models.URLField(null=True, blank=True)
    success_score = models.IntegerField(null=True, blank=True)
    outcome = models.CharField(
        max_length=10,
        choices=[("pass", "Pass"), ("fail", "Fail")],
        null=True
    )
    
    def save(self, *args, **kwargs):
        if self.success_evaluation:
            match = re.search(r'Total Score:\s*(\d+)/\d+', self.success_evaluation)
            if match:
                self.success_score = int(match.group(1))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Call for {self.user.username} ({self.assistant_name})"
    
class CallAnalysis(models.Model):
    # 📞 Core Metadata
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    call_id = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    assistant_name = models.CharField(max_length=100, null=True, blank=True)

    # 📞 Vapi Data
    outcome = models.CharField(
        max_length=10,
        choices=[("pass", "Pass"), ("fail", "Fail")],
        null=True,
        blank=True
    )
    recording_url = models.URLField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)

    # 🤖 OpenAI Rubric Data
    success_score = models.IntegerField(null=True, blank=True)

    acknowledging_score = models.IntegerField(null=True, blank=True)
    acknowledging_reason = models.TextField(null=True, blank=True)
    acknowledging_suggestion = models.TextField(null=True, blank=True)

    reframing_score = models.IntegerField(null=True, blank=True)
    reframing_reason = models.TextField(null=True, blank=True)
    reframing_suggestion = models.TextField(null=True, blank=True)

    handling_score = models.IntegerField(null=True, blank=True)
    handling_reason = models.TextField(null=True, blank=True)
    handling_suggestion = models.TextField(null=True, blank=True)

    securing_score = models.IntegerField(null=True, blank=True)
    securing_reason = models.TextField(null=True, blank=True)
    securing_suggestion = models.TextField(null=True, blank=True)

    respect_score = models.IntegerField(null=True, blank=True)
    respect_reason = models.TextField(null=True, blank=True)
    respect_suggestion = models.TextField(null=True, blank=True)

    final_comments = models.TextField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["user", "assistant_name"]),
            models.Index(fields=["user", "call_id"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"CallAnalysis for {self.user.username} ({self.call_id})"
    
class Dealership(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name