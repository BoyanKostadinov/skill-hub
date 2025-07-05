from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Prefetch

from tracker.forms import ProgressForm
from tracker.models import Skill, LearningGoal, ProgressUpdate, Resource


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        skills = Skill.objects.filter(owner=user).prefetch_related(
            Prefetch('learninggoal_set', queryset=LearningGoal.objects.all().order_by('target_date'))
        )
        context['skills'] = skills
        context['skill_count'] = skills.count()
        context['goal_count'] = LearningGoal.objects.filter(skill__owner=user).count()
        context['progress_count'] = ProgressUpdate.objects.filter(goal__skill__owner=user).count()

        return context

class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    fields = ['name', 'description', 'category', 'difficulty']
    template_name = 'tracker/skill_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class SkillDetailView(LoginRequiredMixin, DetailView):
    model = Skill
    template_name = 'tracker/skill_detail.html'

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = LearningGoal
    fields = ['skill', 'description', 'target_date']
    template_name = 'tracker/goal_form.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        initial = super().get_initial()
        skill_id = self.kwargs.get('skill_id')
        if skill_id:
            initial['skill'] = skill_id
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit skill choices to user's own skills
        form.fields['skill'].queryset = Skill.objects.filter(owner=self.request.user)
        return form

class ProgressCreateView(LoginRequiredMixin, CreateView):
    model = ProgressUpdate
    form_class = ProgressForm
    template_name = 'tracker/progress_form.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        initial = super().get_initial()
        goal_id = self.request.GET.get('goal_id')
        if goal_id:
            initial['goal'] = goal_id
        return initial

    def form_valid(self, form):
        goal_id = self.request.GET.get('goal_id')
        if goal_id:
            try:
                goal = LearningGoal.objects.get(id=goal_id, skill__owner=self.request.user)
                form.instance.goal = goal
            except LearningGoal.DoesNotExist:
                form.add_error(None, "Invalid goal.")
                return self.form_invalid(form)
        else:
            form.add_error(None, "Goal ID is required.")
            return self.form_invalid(form)

        # Save the form *after* assigning the goal
        response = super().form_valid(form)

        # Recalculate total progress for the goal
        total_progress = goal.progressupdate_set.aggregate(total=models.Sum('progress'))['total'] or 0
        goal.progress = min(total_progress, 100)
        goal.save()

        return response

class SkillListView(LoginRequiredMixin, ListView):
    model = Skill
    template_name = 'tracker/skill_list.html'
    context_object_name = 'skills'

    def get_queryset(self):
        return Skill.objects.filter(owner=self.request.user)

class SkillUpdateView(LoginRequiredMixin, UpdateView):
    model = Skill
    fields = ['name', 'description', 'category', 'difficulty']
    template_name = 'tracker/skill_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class SkillDeleteView(LoginRequiredMixin, DeleteView):
    model = Skill
    template_name = 'tracker/skill_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['profile'] = user.profile
        context['skills'] = Skill.objects.filter(owner=user)
        context['goals'] = LearningGoal.objects.filter(skill__owner=user)
        context['updates'] = ProgressUpdate.objects.filter(goal__skill__owner=user)
        context['resources'] = Resource.objects.filter(skill__owner=user)

        return context

class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningGoal
    fields = ['description', 'target_date', 'progress']
    template_name = 'tracker/goal_form.html'
    success_url = reverse_lazy('dashboard')
