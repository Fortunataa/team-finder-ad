import colorsys
from io import BytesIO
import random

from PIL import Image, ImageDraw, ImageFont
from constants import (
    AVATAR_FONT_PATH,
    AVATAR_FONT_RATIO,
    AVATAR_SATURATION_MAX,
    AVATAR_SATURATION_MIN,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    AVATAR_VALUE_MAX,
    AVATAR_VALUE_MIN,
    USER_ABOUT_MAX_LEN,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LEN,
    USER_SURNAME_MAX_LENGTH,
)
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse

from users.managers import UserManager


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

        size = (AVATAR_SIZE, AVATAR_SIZE)
        hue = random.random()
        saturation = random.uniform(AVATAR_SATURATION_MIN,
                                    AVATAR_SATURATION_MAX)
        value = random.uniform(AVATAR_VALUE_MIN, AVATAR_VALUE_MAX)
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        bg_color = tuple(int(c * 255) for c in rgb)

        image = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(image)
        letter = self.name[0].upper()

        font_size = int(AVATAR_SIZE * AVATAR_FONT_RATIO)
        font = ImageFont.truetype(AVATAR_FONT_PATH, font_size)

        center_x = size[0] // 2
        center_y = size[1] // 2
        draw.text((center_x, center_y), letter, fill=AVATAR_TEXT_COLOR,
                  font=font, anchor='mm')

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        self.avatar.save(f'avatar_{self.email}.png', ContentFile(buffer.read()), save=False)
        buffer.close()

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'pk': self.pk})
