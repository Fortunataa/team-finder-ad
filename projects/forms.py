import re
from xml.dom import ValidationErr

from django import forms

from projects.models import Project


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
