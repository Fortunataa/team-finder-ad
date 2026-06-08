import re
from xml.dom import ValidationErr

from constants import USER_NAME_MAX_LENGTH, USER_SURNAME_MAX_LENGTH
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from projects.models import Skill

User = get_user_model()


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


class RegisterForm(UserCreationForm):
    name = forms.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input',
                                      'placeholder': 'Введите имя'})
    )
    surname = forms.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input',
                                      'placeholder': 'Введите фамилию'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input',
                                       'placeholder': 'Введите email'})
    )
    password1 = forms.CharField(
        label='Пароль',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-input',
                                          'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-input',
                                          'placeholder': 'Подтвердите пароль'})
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        if 'username' in self.fields:
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже существует.'
                )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        user.last_name = self.cleaned_data['surname']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input',
                                       'placeholder': 'Введите email'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input',
                                          'placeholder': 'Введите пароль'})
    )


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    new_password2 = forms.CharField(
        label='Подтвердите новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Неверный текущий пароль.')
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('Пароли не совпадают.')
        return new_password2

    def save(self):
        new_password = self.cleaned_data.get('new_password1')
        self.user.set_password(new_password)
        self.user.save()
