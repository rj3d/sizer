from django.db import models
from django.contrib.auth.models import User

class FSNode(models.Model):
    parent = models.ForeignKey('self', null=True, db_index=True)
    name = models.TextField()
    size = models.IntegerField()
    is_dir = models.BooleanField()

class FSUser(models.Model):
    user = models.OneToOneField(User, related_name="fs")
    root = models.OneToOneField(FSNode, unique=True)
    cursor = models.TextField()

