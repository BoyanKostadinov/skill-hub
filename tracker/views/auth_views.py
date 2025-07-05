from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from tracker.forms import RegisterForm, LoginForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from tracker.models import Profile


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        user = authenticate(
            username = form.data['username'],
            password = form.data['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

