# core/admin.py

from django.contrib import admin
from .models import Subject, Content, UserContentState, UserProfile

# This allows you to add/edit Content directly from the Subject page in the admin panel
class ContentInline(admin.TabularInline):
    model = Content
    extra = 1 # Shows one extra blank form for adding new content

class SubjectAdmin(admin.ModelAdmin):
    inlines = [ContentInline]
    list_display = ('name',)

class ContentAdmin(admin.ModelAdmin):
    # FIX: Added the two new fields to this line
    list_display = ('title', 'subject', 'content_type', 'created_at', 'helpful_votes', 'unhelpful_votes')
    list_filter = ('subject', 'content_type')
    search_fields = ('title', 'notes', 'problem_statement')
    # This helps organize the form in the admin panel
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

# Registering UserProfile so you can see it in admin
admin.site.register(UserProfile)
# Unregister the basic Subject admin and register it with the enhanced version
# The line below might cause an error if the server is not restarted. If it does, you can comment it out.
# admin.site.unregister(Subject) 
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(UserContentState, UserContentStateAdmin)