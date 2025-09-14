# core/models.py

from django.db import models
from django.contrib.auth.models import User
import datetime


# NEW: Model to represent departments
class Department(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., CSAI, AIDS, IOT
    
    def __str__(self):
        return self.name

# Model for the subjects (OOP, MI, etc.)
# In core/models.py

class Subject(models.Model):
    name = models.CharField(max_length=100)
    syllabus = models.TextField(blank=True, null=True, help_text="Enter each syllabus topic on a new line.")
    # FIX: Set a default department ID (assuming CSAI is ID=1)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects', default=1)

    # The __str__ method no longer needs the "if" check
    def __str__(self):
        return f"{self.name} ({self.department.name})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)
    # FIX: Set a default department ID (assuming CSAI is ID=1)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='users', null=True, blank=True, default=1)

    def __str__(self):
        return f'{self.user.username}\'s Profile'
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
