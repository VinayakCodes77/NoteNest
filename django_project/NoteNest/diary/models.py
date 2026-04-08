from django.db import models
from django.contrib.auth.models import User


MOOD_CHOICES = [
    ('happy',   '😊 Happy'),
    ('neutral', '😐 Neutral'),
    ('sad',     '😢 Sad'),
    ('angry',   '😡 Angry'),
]

MOOD_EMOJI = {'happy': '😊', 'neutral': '😐', 'sad': '😢', 'angry': '😡'}


class Entry(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200)
    description = models.TextField()
    mood        = models.CharField(max_length=10, choices=MOOD_CHOICES, default='neutral', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} – {self.title}"

    @property
    def mood_emoji(self):
        return MOOD_EMOJI.get(self.mood, '😐')

    @property
    def word_count(self):
        return len(self.description.split())
