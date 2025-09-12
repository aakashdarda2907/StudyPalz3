# core/models.py

from django.db import models
from django.contrib.auth.models import User
import datetime

# Model for the subjects (OOP, MI, etc.)
class Subject(models.Model):
    name = models.CharField(max_length=100)
    # NEW: Field to store the official syllabus text
    syllabus = models.TextField(blank=True, null=True, help_text="Enter each syllabus topic on a new line.")

    def __str__(self):
        return self.name

# Model for the daily content pieces
class Content(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('Theory', 'Theory'),
        ('Lab', 'Lab'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    
    # ... (rest of the Content model is unchanged)
    youtube_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    viva_questions = models.TextField(blank=True, null=True)
    problem_statement = models.TextField(blank=True, null=True)
    solution_code = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    helpful_votes = models.IntegerField(default=0)
    unhelpful_votes = models.IntegerField(default=0)
    users_voted = models.ManyToManyField(User, related_name='voted_content', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.subject.name} - {self.title}'

# Model to track each user's progress on each piece of content
class UserContentState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    marked_for_revision = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'content')

    def __str__(self):
        return f'{self.user.username} - {self.content.title}'

# NEW: Model to store user-specific info like streaks
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}\'s Profile'