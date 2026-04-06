from django.shortcuts import render

# Create your views here.
#code from ai

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Entry

@login_required
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        # Save entry specifically for the logged-in user
        Entry.objects.create(user=request.user, title=title, description=description)
        return redirect('index')
    
    # Filter entries so users only see their own
    entries = Entry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'index.html', {'entries': entries})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

