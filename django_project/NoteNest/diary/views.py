from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django import forms
import re

from .models import Entry


# ------------------------------------------------------------------
# Custom signup form with enhanced server-side validation
# ------------------------------------------------------------------

class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Username is already taken.')
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError(
                'Username may only contain letters, digits, and @/./+/-/_ characters.'
            )
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        errors = []
        if len(password) < 8:
            errors.append('at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('at least one uppercase letter')
        if not re.search(r'\d', password):
            errors.append('at least one number')
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append('at least one special character')
        if errors:
            raise forms.ValidationError(
                'Password must contain: ' + ', '.join(errors) + '.'
            )
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']
        return User.objects.create_user(username=username, password=password)


# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------

@login_required
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Entry.objects.create(user=request.user, title=title, description=description)
        return redirect('index')
    entries = Entry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'index.html', {'entries': entries})


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'registration/signup.html', {'form': form})


@require_GET
def check_username(request):
    username = request.GET.get('username', '').strip()
    if len(username) < 3:
        return JsonResponse({'status': 'too_short', 'message': 'Username must be at least 3 characters.'})
    if not re.match(r'^[\w.@+-]+$', username):
        return JsonResponse({'status': 'invalid', 'message': 'Username contains invalid characters.'})
    taken = User.objects.filter(username__iexact=username).exists()
    if taken:
        return JsonResponse({'status': 'taken', 'message': 'Username already taken.'})
    return JsonResponse({'status': 'available', 'message': 'Username is available!'})
