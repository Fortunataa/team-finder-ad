import re
from xml.dom import ValidationErr

from django import forms

from projects.models import Project, Skill, User


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea',
                                                 'rows': 6}),
            'github_url': forms.URLInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url')

        if not github_url:
            return github_url

        github_pattern = r'^https?://(www\.)?github\.com/[\w\-\.]+/?$'

        if not re.match(github_pattern, github_url):
            raise ValidationErr(
                'Введите корректную ссылку на профиль GitHub.'
            )

        return github_url


class ProfileEditForm(forms.ModelForm):
    skills = forms.CharField(
        label='Навыки',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Введите навыки через запятую'
                }
            )
        )

    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'surname': forms.TextInput(attrs={'class': 'form-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input-file'}),
            'about': forms.Textarea(attrs={'class': 'form-textarea',
                                           'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        skills_input = self.cleaned_data.get('skills', '')
        if skills_input:
            skill_names = [
                name.strip()
                for name in skills_input.split(',')
                if name.strip()
                ]
            user.skills.clear()
            for skill_name in skill_names:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                user.skills.add(skill)
        else:
            user.skills.clear()

        return user

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url')

        if not github_url:
            return github_url

        github_pattern = r'^https?://(www\.)?github\.com/[\w\-\.]+/?$'

        if not re.match(github_pattern, github_url):
            raise ValidationErr(
                'Введите корректную ссылку на профиль GitHub.'
            )

        return github_url
