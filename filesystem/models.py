from django.db import models
from django.contrib.auth.models import User

class FSUser(models.Model):
    user = models.OneToOneField(User, related_name="fs")
    root_id = models.OneToOneField(Filesystem)
    cursor = models.TextField()

class Filesystem(models.Model):
    parent = models.ForeignKey('self', null=True, db_index=True)
    size = models.IntegerField()
    is_dir = models.BooleanField()
