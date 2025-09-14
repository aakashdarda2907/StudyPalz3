# core/admin.py

from django.contrib import admin
# UPDATED: Import the Department and UserProfile models
from .models import Subject, Content, UserContentState, Department, UserProfile

# NEW: Admin view for the Department model
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# This allows you to add/edit Content directly from the Subject page in the admin panel
class ContentInline(admin.TabularInline):
    model = Content
    extra = 1

class SubjectAdmin(admin.ModelAdmin):
    inlines = [ContentInline]
    list_display = ('name', 'department') # Added department to the display
    list_filter = ('department',)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'content_type', 'created_at', 'helpful_votes', 'unhelpful_votes')
    list_filter = ('subject__department', 'subject', 'content_type') # Filter by department
    search_fields = ('title', 'notes', 'problem_statement')
    
    # ... (rest of ContentAdmin is unchanged) ...
    fieldsets = (
        ('General Information', {
            'fields': ('subject', 'title', 'content_type')
        }),
        ('Theory Content (Leave blank if Lab)', {
            'fields': ('youtube_link', 'notes', 'viva_questions')
        }),
        ('Lab Content (Leave blank if Theory)', {
            'fields': ('problem_statement', 'solution_code', 'explanation')
        }),
    )

class UserContentStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_completed', 'marked_for_revision')
    list_filter = ('is_completed', 'marked_for_revision')

# Register your models here
admin.site.register(Department, DepartmentAdmin) # NEW: Register Department
admin.site.register(UserProfile)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(UserContentState, UserContentStateAdmin)