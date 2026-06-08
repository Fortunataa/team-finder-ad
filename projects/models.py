from constants import (
    CHOICES,
    PROJECT_NAME_MAX_LEN,
    PROJECT_STATUS_MAX_LEN,
    SKILL_NAME_MAX_LEN,
)
from django.contrib.auth.models import User
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LEN, unique=True,
                            verbose_name='Название навыка')

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Project(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор проекта'
    )
    name = models.CharField(max_length=PROJECT_NAME_MAX_LEN,
                            verbose_name='Название проекта')
    description = models.TextField(verbose_name='Описание проекта')
    github_url = models.URLField(blank=True, null=True,
                                 verbose_name='Ссылка на GitHub')
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LEN,
        choices=CHOICES,
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
