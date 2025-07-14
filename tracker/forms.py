from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from tracker.models import Skill, LearningGoal, ProgressUpdate, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'
        exclude = ('owner',)

class GoalForm(forms.ModelForm):
    class Meta:
        model = LearningGoal
        fields = '__all__'

        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if len(bio) < 10:
            raise forms.ValidationError("Biography must be at least 10 characters long.")
        return bio