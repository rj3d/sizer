from django.db import models
from django.contrib.auth.models import User

class FSNode(models.Model):
    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, db_index=True)
    name = models.TextField()
    size = models.BigIntegerField()
    is_dir = models.BooleanField()
    full_path = models.TextField()

class FSUser(models.Model):
    user = models.OneToOneField(User, related_name="fs")
    root = models.OneToOneField(FSNode, unique=True)
    complete = models.BooleanField(default=False)
    cursor = models.TextField()

