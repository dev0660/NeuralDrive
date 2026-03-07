from django.db import models
from django.contrib.auth.models import AbstractUser

class fredDavis(AbstractUser):
    callID = models.CharField(max_length=100, unique=True)
    assistant = models.CharField(max_length=100, blank=True)
    assistantPhoneNumber = models.IntegerField(blank=True, null=True)
    

    def __str__(self):
        return self.username