from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10)
    email = models.EmailField(unique=True)

    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.sex}) - {self.email}"
