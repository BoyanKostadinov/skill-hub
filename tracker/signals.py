from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

@receiver(post_migrate)
def create_admin_groups(sender, **kwargs):
    # Define groups and the permissions you want to assign
    superadmin_group, _ = Group.objects.get_or_create(name='SuperAdmin')
    staffadmin_group, _ = Group.objects.get_or_create(name='StaffAdmin')

    # Give SuperAdmin full permissions to all models
    for model in apps.get_models():
        ct = ContentType.objects.get_for_model(model)
        perms = Permission.objects.filter(content_type=ct)
        superadmin_group.permissions.add(*perms)

    # StaffAdmin limited permissions (example: can add/view/change Skill and LearningGoal, but not delete or manage users)
    allowed_models = ['skill', 'learninggoal', 'progressupdate']
    allowed_actions = ['add', 'change', 'view']

    for model_name in allowed_models:
        model = apps.get_model('tracker', model_name)
        ct = ContentType.objects.get_for_model(model)
        for action in allowed_actions:
            try:
                perm = Permission.objects.get(content_type=ct, codename=f'{action}_{model_name}')
                staffadmin_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass


from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

User = get_user_model()

@receiver(post_save, sender=User)
def assign_admin_group(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            group = Group.objects.get(name='SuperAdmin')
            instance.groups.add(group)
        elif instance.is_staff:
            group = Group.objects.get(name='StaffAdmin')
            instance.groups.add(group)
