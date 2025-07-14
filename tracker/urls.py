from django.urls import path
from tracker.views import public_views, auth_views, private_views
from tracker.views.private_views import ProgressCreateView, SkillUpdateView, SkillDeleteView, ResourceCreateView, UserProfileEditView

urlpatterns = [
    path('', public_views.home_view, name='home'),
    path('about/', public_views.about_view, name='about'),

    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),

    path('dashboard/', private_views.DashboardView.as_view(), name='dashboard'),
    path('skills/', private_views.SkillListView.as_view(), name='skill-list'),

    path('skill/add/', private_views.SkillCreateView.as_view(), name='skill-add'),
    path('skill/<int:pk>/', private_views.SkillDetailView.as_view(), name='skill-detail'),
    path('skill/<int:pk>/edit/', SkillUpdateView.as_view(), name='skill-update'),
    path('progress/add/', ProgressCreateView.as_view(), name='progress-form'),
    path('skill/<int:pk>/delete/', SkillDeleteView.as_view(), name='skill-delete'),
    path('profile/', private_views.ProfileView.as_view(), name='profile'),
    path('goal/add/<int:skill_id>/', private_views.GoalCreateView.as_view(), name='goal-add'),
    path('goal/edit/<int:pk>/', private_views.GoalUpdateView.as_view(), name='goal-edit'),
    path('resources/add/', ResourceCreateView.as_view(), name='resource-add'),
    path('profile/edit/', UserProfileEditView.as_view(), name='edit-profile'),


]