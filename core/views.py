# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Department, Subject, Content, UserContentState, UserProfile # Add UserProfile
from django.db.models import Count, Q
from datetime import date, timedelta # Add timedelta

# ... (home_view, signup_view, logout_view are unchanged)
def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def signup_view(request):
    # Pass all departments to the template for the dropdown
    departments = Department.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        department_id = request.POST.get('department') # Get department ID from form

        if password != password_confirm:
            return render(request, 'core/signup.html', {'error': 'Passwords do not match', 'departments': departments})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'core/signup.html', {'error': 'Username already exists', 'departments': departments})

        # Create user and their profile with the selected department
        user = User.objects.create_user(username=username, password=password, first_name=first_name)
        department = Department.objects.get(id=department_id)
        UserProfile.objects.create(user=user, department=department) # Create profile
        
        login(request, user)
        return redirect('dashboard')

    return render(request, 'core/signup.html', {'departments': departments})

def logout_view(request):
    logout(request)
    return redirect('home')


# UPDATED: dashboard_view with streak logic
# In core/views.py

# Replace the old dashboard_view with this one
@login_required
def dashboard_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # --- Streak Logic (remains the same) ---
    today = date.today()
    streak_increased = False
    if profile.last_login_date is None or profile.last_login_date < today:
        yesterday = today - timedelta(days=1)
        if profile.last_login_date == yesterday:
            profile.current_streak += 1
            streak_increased = True
        else:
            profile.current_streak = 1
        profile.last_login_date = today
        profile.save()

    # --- UPDATED: Subject Filtering Logic ---
    user_department = profile.department
    if user_department:
        subjects = Subject.objects.filter(department=user_department)
    else:
        subjects = Subject.objects.none() # Show no subjects if department is not set
    # --- End of new logic ---

    subject_progress = []
    for subject in subjects:
        total_content = Content.objects.filter(subject=subject).count()
        completed_content = UserContentState.objects.filter(
            user=request.user, 
            content__subject=subject, 
            is_completed=True
        ).count()
        percentage = int((completed_content / total_content) * 100) if total_content > 0 else 0
        subject_progress.append({'subject': subject, 'percentage': percentage})

    context = {
        'subject_progress': subject_progress,
        'current_streak': profile.current_streak,
        'streak_increased': streak_increased,
        'user_department': user_department, # Pass department to template
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def subject_detail_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    content_list = Content.objects.filter(subject=subject)
    
    # --- NEW Simplified Logic ---
    # Get all user states for this subject in one query
    user_progress = UserContentState.objects.filter(
        user=request.user, 
        content__subject=subject
    ).values('content_id', 'is_completed', 'marked_for_revision')

    # Create a dictionary for fast lookups: {content_id: {status}}
    progress_map = {item['content_id']: item for item in user_progress}

    # Attach the progress directly to each content object
    for content in content_list:
        progress = progress_map.get(content.id)
        if progress:
            content.is_completed = progress['is_completed']
            content.marked_for_revision = progress['marked_for_revision']
        else:
            content.is_completed = False
            content.marked_for_revision = False
    # --- End of New Logic ---

    # We still need the syllabus logic
    completed_content_titles = {
        c.title for c in content_list if c.is_completed
    }
    syllabus_topics = subject.syllabus.splitlines() if subject.syllabus else []
    completed_content_count = len(completed_content_titles)
    
    context = {
        'subject': subject,
        'content_list': content_list,
        'syllabus_topics': syllabus_topics,
        'completed_content_titles': completed_content_titles,
        'total_content_count': content_list.count(),
        'completed_content_count': completed_content_count,
    }
    return render(request, 'core/subject_detail.html', context)

# ... (rest of the views are unchanged)
# At the top of core/views.py, add these new imports
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# Replace your old content_detail_view with this one
# In core/views.py

# Replace your old content_detail_view with this one
@login_required
def content_detail_view(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    highlighted_code = None
    pygments_css = None

    # If it's a lab with code, highlight it
    if content.content_type == 'Lab' and content.solution_code:
        lexer = get_lexer_by_name('cpp', stripall=True)
        # FIX: Changed full=True to full=False
        formatter = HtmlFormatter(style='solarized-dark', full=False, linenos=True)
        highlighted_code = highlight(content.solution_code, lexer, formatter)
        # NEW: Generate the CSS for the theme
        pygments_css = formatter.get_style_defs('.highlight')

    context = {
        'content': content,
        'highlighted_code': highlighted_code,
        'pygments_css': pygments_css, # Pass the CSS to the template
    }
    return render(request, 'core/content_detail.html', context)

@login_required
def toggle_complete_view(request, content_id):
    if request.method == 'POST':
        content = get_object_or_404(Content, id=content_id)
        state, created = UserContentState.objects.get_or_create(user=request.user, content=content)
        state.is_completed = not state.is_completed
        state.save()
        return redirect('subject_detail', subject_id=content.subject.id)
    return redirect('dashboard')

@login_required
def toggle_revision_view(request, content_id):
    if request.method == 'POST':
        content = get_object_or_404(Content, id=content_id)
        state, created = UserContentState.objects.get_or_create(user=request.user, content=content)
        state.marked_for_revision = not state.marked_for_revision
        state.save()
        return redirect('subject_detail', subject_id=content.subject.id)
    return redirect('dashboard')

@login_required
def revision_hub_view(request):
    revision_items = Content.objects.filter(usercontentstate__user=request.user, usercontentstate__marked_for_revision=True)
    context = {'revision_items': revision_items}
    return render(request, 'core/revision_hub.html', context)

# Add this new view at the end of core/views.py

@login_required
def feedback_view(request, content_id):
    if request.method == 'POST':
        content = get_object_or_404(Content, id=content_id)
        vote_type = request.POST.get('vote_type')

        # Check if user has already voted
        if request.user in content.users_voted.all():
            return redirect('content_detail', content_id=content_id)

        if vote_type == 'helpful':
            content.helpful_votes += 1
        elif vote_type == 'unhelpful':
            content.unhelpful_votes += 1
        
        content.users_voted.add(request.user)
        content.save()
        
    return redirect('content_detail', content_id=content_id)