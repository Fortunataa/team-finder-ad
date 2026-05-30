from django.contrib import admin
from .models import User, Skill, Project


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'email', 'created_at')
    search_fields = ('name', 'surname', 'email')
    filter_horizontal = ()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__name', 'owner__surname')
    filter_horizontal = ('skills', 'participants', 'favorites')
