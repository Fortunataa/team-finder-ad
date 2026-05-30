from django import forms
from users.models import Project, Skill


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Название проекта'
        self.fields['description'].label = 'Описание проекта'
        self.fields['github_url'].label = 'Ссылка на GitHub (необязательно)'
        self.fields['status'].label = 'Статус'
        self.fields['name'].required = True
        self.fields['description'].required = True
