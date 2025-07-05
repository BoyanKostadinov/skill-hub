from django.shortcuts import render
from tracker.models import Skill

def home_view(request):
    return render(request, 'tracker/home.html')

def about_view(request):
    return render(request, 'tracker/about.html')

def public_skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'tracker/skill_list.html', {'skills': skills})