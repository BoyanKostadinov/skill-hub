from django.contrib import admin
from .models import Skill, LearningGoal, ProgressUpdate, Profile, Resource


# Register your models here.
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'difficulty')
    list_filter = ('category', 'difficulty')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(LearningGoal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('skill', 'target_date', 'progress')
    list_filter = ('target_date',)
    ordering = ('target_date',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'skill', 'approved')
    list_filter = ('approved',)

admin.site.register(Profile)
admin.site.register(ProgressUpdate)