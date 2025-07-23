from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Prefetch
from django import forms
from collections import defaultdict

from tracker.forms import ProgressForm, ProfileForm
from tracker.models import Skill, LearningGoal, ProgressUpdate, Resource, Profile


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
    fields = ['skill', 'name', 'description', 'target_date']
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
        form.fields['target_date'].widget = forms.DateInput(attrs={'type': 'date'})
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

        # The form is assigning after the goal
        response = super().form_valid(form)

        # Total progress is recalculated for the goal
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

class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningGoal
    template_name = 'tracker/goal_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        skills = Skill.objects.filter(owner=user)
        goals = LearningGoal.objects.filter(skill__in=skills)
        updates = ProgressUpdate.objects.filter(goal__in=goals).select_related('goal', 'goal__skill')

        temp_grouped = defaultdict(lambda: defaultdict(list))
        for update in updates:
            temp_grouped[update.goal.skill.id][update.goal.id].append(update)

        # Convert to regular dict of dicts
        grouped_updates = {
            skill_id: dict(goals)
            for skill_id, goals in temp_grouped.items()
        }

        resource_groups = defaultdict(list)
        skill_map = {}
        for skill in skills:
            skill_map[skill.id] = skill

            resources = Resource.objects.filter(skill=skill, approved=True)
            if resources.exists():
                resource_groups[skill.id] = list(resources)


        resource_groups = dict(resource_groups)

        context.update({
            'profile': user.profile,
            'skills': skills,
            'goals': goals,
            'updates': updates,
            'grouped_updates': grouped_updates,
            'goal_map': {goal.id: goal for goal in goals},
            'resources': resource_groups,
            'skill_map': skill_map,
        })

        return context

class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningGoal
    fields = ['name', 'description', 'target_date', 'progress']
    template_name = 'tracker/goal_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        # This ensures users can only edit their own goals
        return LearningGoal.objects.filter(skill__owner=self.request.user)

class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = Resource
    fields = ['skill', 'title', 'link']
    template_name = 'tracker/resource_form.html'
    success_url = reverse_lazy('dashboard')  # or redirect to profile or skill detail

    def form_valid(self, form):
        form.instance.added_by = self.request.user  # Track who added the resource
        # By default, approved is set to False. The admin will approve it.
        form.instance.approved = False
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['skill'].queryset = Skill.objects.filter(owner=self.request.user)
        return form


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'tracker/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        form.instance.is_approved = False
        return super().form_valid(form)