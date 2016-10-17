from __future__ import unicode_literals

from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    image_url = models.URLField()