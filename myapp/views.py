from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import random
from .models import Artifact

# --- AUTHENTICATION VIEWS ---

def signup_view(request):
    # Redirects any old registration routes directly to our combined page
    return redirect('/login/?tab=register')

def login_view(request):
    error_context = {}  # Holds our error information if something goes wrong
    
    if request.method == "POST":
        # 1. HANDLE LOGIN FORM SUBMISSION
        if 'submit_login' in request.POST:
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        
        # 2. HANDLE MULTI-STEP REGISTRATION FORM SUBMISSION
        elif 'submit_register' in request.POST:
            # Capture inputs and apply .strip() to handle sneaky empty space submissions
            name = request.POST.get('reg_name', '').strip()
            role = request.POST.get('reg_role', '').strip()
            username = request.POST.get('reg_username', '').strip()
            email = request.POST.get('reg_email', '').strip()
            password = request.POST.get('reg_password', '') # Don't strip passwords to keep spaces intentional
            
            # Keep track of what they typed so they don't have to re-enter it if it reloads
            error_context = {
                'typed_name': name,
                'typed_role': role,
                'typed_username': username,
                'typed_email': email,
            }

            # ULTIMATE BACKEND ENFORCEMENT: Enforce password rules & check if fields are missing
            has_number = any(char.isdigit() for char in password)
            
            if not name or not role or not username or not email or not password:
                messages.error(request, "Registration rejected. All configurations must be fully filled out.")
                error_context['reg_error'] = True
                
            elif len(password) < 6 or not has_number:
                messages.error(request, "Security breach protection: Passwords must be at least 6 characters and contain a number.")
                error_context['reg_error'] = True
                
            elif User.objects.filter(username=username).exists():
                messages.error(request, "System ID/Username is already registered in the vault.")
                error_context['username_taken'] = True
                error_context['reg_error'] = True
                
            else:
                # Create standard Django user account safely
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                # Instantly log the new user in and send them to the home page
                login(request, user)
                return redirect('home')

    # For standard GET requests, initialize a clean login form instance
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, **error_context})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- LIBRARY VIEWS (Protected) ---

@login_required(login_url='login')
def library_view(request):
    search_id = request.GET.get('search_id')
    artifacts = Artifact.objects.filter(owner=request.user)
    
    if search_id:
        artifacts = artifacts.filter(id=search_id)
        
    return render(request, 'library.html', {'artifacts': artifacts})

@login_required(login_url='login')
def create_artifact(request):
    if request.method == "POST":
        name = request.POST.get('artifact_name')
        rarity = random.choice(["Common", "Rare", "Legendary", "Mythical"])
        power = random.randint(10, 100)
        Artifact.objects.create(name=name, rarity=rarity, power=power, owner=request.user)
        return redirect('home')
    return render(request, 'create.html')

# --- UPDATE & DELETE VIEWS ---

@login_required(login_url='login')
def update_artifact(request, art_id):
    # Find the artifact belonging to the logged-in user
    artifact = get_object_or_404(Artifact, id=art_id, owner=request.user)
    
    if request.method == "POST":
        # Capture all the editable options from the form fields
        artifact.name = request.POST.get('artifact_name')
        artifact.power = request.POST.get('artifact_power')
        artifact.rarity = request.POST.get('artifact_rarity')
        
        # Save the updated changes to the database
        artifact.save()
        return redirect('home')
        
    return render(request, 'update.html', {'artifact': artifact})

@login_required(login_url='login')
def delete_artifact(request, art_id):
    artifact = get_object_or_404(Artifact, id=art_id, owner=request.user)
    artifact.delete()
    return redirect('home')
from django.contrib.auth.models import User
from django.http import JsonResponse

def check_username_availability(request):
    username = request.GET.get('username', '').strip()
    # Check if a user with this username already exists in your database
    is_taken = User.objects.filter(username__iexact=username).exists() if username else False
    return JsonResponse({'is_taken': is_taken})