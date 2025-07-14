from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    bio = models.TextField(
        null=True,
        blank=True,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to='avatars/',
    )

    is_approved = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.user.username

class Skill(models.Model):
    name = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    category = models.CharField(
        max_length=50,
    )

    difficulty = models.CharField(
        max_length=10,
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def is_complete(self):
        goals = self.learninggoal_set.all()
        return goals.exists() and all(goal.is_complete for goal in goals)

    def __str__(self):
            return self.name

class LearningGoal(models.Model):
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
    )

    description = models.TextField()

    target_date = models.DateField()

    progress = models.IntegerField(
        default=0
    )

    @property
    def is_complete(self):
        return self.progress >= 100

    def __str__(self):
        return f"{self.skill.name} Goal"

class ProgressUpdate(models.Model):
    goal = models.ForeignKey(
        LearningGoal,
        on_delete=models.CASCADE,
    )

    progress = models.IntegerField(
        default=0
    )

    update_text = models.TextField()

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Update for {self.goal.skill.name} on {self.date}"

class Resource(models.Model):
    title = models.CharField(
        max_length=100
    )

    link = models.URLField()

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
    )

    approved = models.BooleanField(
        default=False
    )

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title