from http import HTTPStatus
import json

from constants import (
    MAX_SKILLS_SEARCH_RESULTS,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    PROJECTS_PAGINATE_BY,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from projects.models import Project, Skill

from .forms import ProjectForm


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = PROJECTS_PAGINATE_BY

    def get_queryset(self):
        queryset = (Project.objects
                    .filter(status=PROJECT_STATUS_OPEN)
                    .select_related('skills', 'participants', 'favorites',
                                    'owner'))
        skill_filter = self.request.GET.get('skill')
        if skill_filter:
            queryset = queryset.filter(skills__name=skill_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = sorted(
            Skill.objects
            .values_list('name', flat=True)
            .distinct()
            )
        context['active_skill'] = self.request.GET.get('skill')
        return context


class FavoriteProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'
    paginate_by = PROJECTS_PAGINATE_BY

    def get_queryset(self):
        return self.request.user.favorite_projects.all()


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = (
            self.request.user.is_authenticated and
            self.request.user.id == self.object.owner.id
            )
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:project_detail',
                       kwargs={'project_id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'
    pk_url_kwarg = 'project_id'

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('projects:project_detail',
                       kwargs={'project_id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


@method_decorator(require_http_methods(["GET"]), name='dispatch')
class SkillSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse([])
        skills = list(
            Skill.objects
            .filter(name__icontains=query)[:MAX_SKILLS_SEARCH_RESULTS]
            .values('id', 'name'))
        return JsonResponse(skills, safe=False)


@method_decorator(require_http_methods(["POST"]), name='dispatch')
class SkillAddView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if request.user.id != project.owner.id:
            return JsonResponse(
                {'error': 'Только владелец может управлять навыками'},
                status=HTTPStatus.FORBIDDEN
            )

        data = json.loads(request.body)
        skill_id = data.get('skill_id')
        skill_name = data.get('name')

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
        elif skill_name:
            skill_name = skill_name.strip()
            if not skill_name:
                return JsonResponse(
                    {'error': 'Название навыка не указано'},
                    status=HTTPStatus.BAD_REQUEST
                )
            skill, _ = Skill.objects.get_or_create(name=skill_name)
        else:
            return JsonResponse(
                {'error': 'Не указан skill_id или name'},
                status=HTTPStatus.BAD_REQUEST
            )
        project.skills.add(skill)

        return JsonResponse({'id': skill.id, 'name': skill.name})


@method_decorator(require_http_methods(["POST"]), name='dispatch')
class SkillRemoveView(LoginRequiredMixin, View):
    def post(self, request, project_id, skill_id):
        project = get_object_or_404(Project, id=project_id)

        if request.user.id != project.owner.id:
            return JsonResponse(
                {'error': 'Только владелец может управлять навыками'},
                status=HTTPStatus.FORBIDDEN
            )

        skill = get_object_or_404(Skill, id=skill_id)
        project.skills.remove(skill)

        return JsonResponse({'success': True})


class ParticipateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.participants.filter(id=request.user.id).exists():
            project.participants.remove(request.user)
            action = 'removed'
        else:
            project.participants.add(request.user)
            action = 'added'

        return JsonResponse({
            'action': action,
            'participants_count': project.participants.count()
        })


class CompleteProjectView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if request.user.id != project.owner.id:
            return JsonResponse(
                {'error': 'Только владелец может завершить проект'},
                status=HTTPStatus.FORBIDDEN
            )

        project.status = PROJECT_STATUS_CLOSED
        project.save()

        return JsonResponse({'success': True, 'status': PROJECT_STATUS_CLOSED})


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        is_in_favorites = project.favorites.filter(id=request.user.id).exists()
        is_favorite = not is_in_favorites

        if is_favorite:
            project.favorites.add(request.user)
        else:
            project.favorites.remove(request.user)

        return JsonResponse({'is_favorite': is_favorite})
