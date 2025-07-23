from django.contrib import admin
from .models import Skill, LearningGoal, ProgressUpdate, Profile, Resource
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms


# Register your models here.
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'difficulty')
    list_filter = ('category', 'difficulty')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at',)

@admin.register(LearningGoal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('skill', 'target_date', 'progress')
    list_filter = ('target_date',)
    ordering = ('target_date',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'skill', 'approved', 'added_by')
    list_filter = ('approved',)
    readonly_fields = ('added_by',)
    fields = ('title', 'skill', 'link', 'approved', 'added_by')

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # Added_by is read-only after the object is created
        if obj:
            return self.readonly_fields + ('added_by',)
        return self.readonly_fields

admin.site.register(Profile)
admin.site.register(ProgressUpdate)

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        is_staff = self.cleaned_data.get('is_staff')
        is_superuser = self.cleaned_data.get('is_superuser')

        # If the user is not staff or superuser, prevent including them to admin groups
        admin_groups = Group.objects.filter(name__in=['SuperAdmin', 'StaffAdmin'])

        if not is_staff and not is_superuser:
            for group in groups:
                if group in admin_groups:
                    raise ValidationError("Only staff or superusers can be assigned to admin groups.")
        return groups


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)