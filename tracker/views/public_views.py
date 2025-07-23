from django.shortcuts import render
from tracker.models import Skill

def home_view(request):
    return render(request, 'tracker/home.html')

def about_view(request):
    return render(request, 'tracker/about.html')
