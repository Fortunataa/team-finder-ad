import colorsys
from io import BytesIO
import random

from PIL import Image, ImageDraw, ImageFont
from constants import (
    CHOICES,
    PROJECT_NAME_MAX_LEN,
    PROJECT_STATUS_MAX_LEN,
    SKILL_NAME_MAX_LEN,
    USER_ABOUT_MAX_LEN,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LEN,
    USER_SURNAME_MAX_LENGTH,
)
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Обязательное и уникальное поле'
    )
    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        verbose_name='Имя'
    )
    surname = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LEN,
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='GitHub'
    )
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LEN,
        blank=True,
        verbose_name='О себе'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    is_staff = models.BooleanField(default=False, verbose_name='Администратор')

    skills = models.ManyToManyField(
        'Skill',
        related_name='users',
        blank=True,
        verbose_name='Навыки'
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата регистрации')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.surname} {self.name}'

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        if not self.name:
            return

        size = (200, 200)
        hue = random.random()
        saturation = random.uniform(0.3, 0.5)
        value = random.uniform(0.8, 0.95)
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        bg_color = tuple(int(c * 255) for c in rgb)

        image = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(image)
        letter = self.name[0].upper()

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            140
        )

        center_x = size[0] // 2
        center_y = size[1] // 2
        text_color = (50, 50, 50)
        draw.text((center_x, center_y), letter, fill=text_color, font=font,
                  anchor='mm')

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        self.avatar.save(f'avatar_{self.email}.png',
                         ContentFile(buffer.read()),
                         save=False)
        buffer.close()

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'pk': self.pk})


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
