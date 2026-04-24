from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import random
from .models import Artifact

# --- AUTHENTICATION VIEWS ---
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- LIBRARY VIEWS (Now Protected) ---
@login_required(login_url='login')
def library_view(request):
    search_id = request.GET.get('search_id')
    # This line ensures you only see artifacts YOU created
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
        # Assign the logged-in user as the owner
        Artifact.objects.create(name=name, rarity=rarity, power=power, owner=request.user)
        return redirect('home')
    return render(request, 'create.html')
# --- UPDATE & DELETE VIEWS ---

@login_required(login_url='login')
def update_artifact(request, art_id):
    # This finds the artifact but only if it belongs to the logged-in user
    artifact = get_object_or_404(Artifact, id=art_id, owner=request.user)
    if request.method == "POST":
        artifact.name = request.POST.get('artifact_name')
        artifact.save()
        return redirect('home')
    return render(request, 'update.html', {'artifact': artifact})

@login_required(login_url='login')
def delete_artifact(request, art_id):
    # This ensures users can only delete their own items
    artifact = get_object_or_404(Artifact, id=art_id, owner=request.user)
    artifact.delete()
    return redirect('home')