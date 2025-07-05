from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from tracker.models import Skill, LearningGoal, ProgressUpdate


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'
        exclude = ('owner',)

class GoalForm(forms.ModelForm):
    class Meta:
        model = LearningGoal
        fields = '__all__'

class ProgressForm(forms.ModelForm):
    class Meta:
        model = ProgressUpdate
        fields = ['progress', 'update_text']

        widgets = {
            'goal': forms.HiddenInput(),  # This hides the goal field
        }

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput,
    )