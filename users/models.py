from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=100, verbose_name='Имя')
    surname = models.CharField(max_length=100, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', null=True,
                               blank=True, verbose_name='Аватар')
    about = models.TextField(blank=True, null=True, verbose_name='О себе')
    phone = models.CharField(max_length=20, blank=True, null=True,
                             verbose_name='Телефон')
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub')
    skills = models.ManyToManyField('Skill', related_name='users', blank=True,
                                    verbose_name='Навыки')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата регистрации')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.surname} {self.name}'


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True,
                            verbose_name='Название навыка')

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор проекта'
    )
    name = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(verbose_name='Описание проекта')
    github_url = models.URLField(blank=True, null=True,
                                 verbose_name='Ссылка на GitHub')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name='Статус'
    )
    skills = models.ManyToManyField(Skill,
                                    related_name='projects', blank=True,
                                    verbose_name='Необходимые навыки')
    participants = models.ManyToManyField(
        User,
        related_name='participating_projects',
        blank=True,
        verbose_name='Участники проекта'
    )
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_projects',
        blank=True,
        verbose_name='В избранном у'
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата публикации')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
