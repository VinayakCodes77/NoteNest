from datetime import timedelta

from django.db import models as db_models
from django.utils import timezone as django_tz
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django import forms
import re

from .models import Entry


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def calculate_streak(user):
    """Count consecutive days (IST) ending today or yesterday with entries."""
    # Convert every stored UTC datetime to IST date
    entry_dates = set(
        django_tz.localtime(e.created_at).date()
        for e in Entry.objects.filter(user=user).only('created_at')
    )
    today = django_tz.localtime(django_tz.now()).date()
    check = today if today in entry_dates else today - timedelta(days=1)
    streak = 0
    while check in entry_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


# ------------------------------------------------------------------
# Custom signup form with enhanced server-side validation
# ------------------------------------------------------------------

class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=150, min_length=3,
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
            raise forms.ValidationError('Password must contain: ' + ', '.join(errors) + '.')
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
        )


# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------

@login_required
def index(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        mood        = request.POST.get('mood', 'neutral')
        if title and description:
            Entry.objects.create(user=request.user, title=title, description=description, mood=mood)
        return redirect('index')

    entries = Entry.objects.filter(user=request.user)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        entries = entries.filter(
            db_models.Q(title__icontains=q) | db_models.Q(description__icontains=q)
        )

    # Mood filter
    mood_filter = request.GET.get('mood', '')
    if mood_filter:
        entries = entries.filter(mood=mood_filter)

    # Date filter
    date_filter = request.GET.get('date', '')
    if date_filter:
        entries = entries.filter(created_at__date=date_filter)

    # Use IST-aware "today" for correct date boundaries
    now_ist   = django_tz.localtime(django_tz.now())
    today_ist = now_ist.date()
    day_start = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end   = day_start + timedelta(days=1)

    total       = Entry.objects.filter(user=request.user).count()
    today_count = Entry.objects.filter(user=request.user, created_at__gte=day_start, created_at__lt=day_end).count()
    streak      = calculate_streak(request.user)

    return render(request, 'index.html', {
        'entries':      entries,
        'streak':       streak,
        'total':        total,
        'today_count':  today_count,
        'q':            q,
        'mood_filter':  mood_filter,
        'date_filter':  date_filter,
    })


@login_required
@require_POST
def delete_entry(request, pk):
    Entry.objects.filter(pk=pk, user=request.user).delete()
    return redirect('index')


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
