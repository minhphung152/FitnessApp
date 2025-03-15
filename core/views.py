from django.shortcuts import render, redirect

from weight_tracker.models import WeightLog, Goal, BMILog

from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm

class CustomLogoutView(LogoutView):
    next_page = 'core:index'

require_http_methods(["GET", "POST"])
def custom_login(request):
    # Redirect logged-in users
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate required fields
        if not username or not password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'core/login.html')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                # Login successful
                login(request, user)

                return redirect('core:index')
            else:
                messages.error(request, 'This account is inactive')
        else:
            messages.error(request, 'Invalid username or password')
        
        return render(request, 'core/login.html')

    # GET request - show login form
    context = {
        'next': request.GET.get('next', '')
    }
    return render(request, 'core/login.html', context)

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db() # Load profile instance
            user.save()

            # Auto-login after registration
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('core:index')
    else:
        form = SignUpForm()
    return render(request, 'core/register.html', {'form': form})

# Render the index
def index(request):
    return render(request, 'core/index.html')