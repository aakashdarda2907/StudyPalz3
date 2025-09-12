# core/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Auth pages
    path('signup/', views.signup_view, name='signup'),
    # Using Django's built-in LoginView. We just tell it which template to use.
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Content pages
    path('subject/<int:subject_id>/', views.subject_detail_view, name='subject_detail'),
    path('content/<int:content_id>/', views.content_detail_view, name='content_detail'),
    
    # Action URLs for progress tracking
    path('content/<int:content_id>/toggle_complete/', views.toggle_complete_view, name='toggle_complete'),
    path('content/<int:content_id>/toggle_revision/', views.toggle_revision_view, name='toggle_revision'),

    # Revision Hub
    path('revision-hub/', views.revision_hub_view, name='revision_hub'),
     path('content/<int:content_id>/feedback/', views.feedback_view, name='feedback'),
]