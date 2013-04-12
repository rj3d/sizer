from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DBUser(models.Model):
    user = models.OneToOneField(User, related_name="db")
    access_token = models.CharField(max_length=256)
    access_token_secret = models.CharField(max_length=256)