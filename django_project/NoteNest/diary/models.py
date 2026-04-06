from django.db import models

# Create your models here.
#code from ai

from django.contrib.auth.models import User

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Links to a user
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

