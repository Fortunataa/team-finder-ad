from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic import CreateView, DetailView, UpdateView, \
    ListView, View
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.urls import reverse
import json

from .models import User, Skill, Project
from .forms import RegisterForm, LoginForm, ProfileEditForm, ChangePasswordForm


@method_decorator(require_http_methods(["GET", "POST"]), name='dispatch')
class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('projects:project_list')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('projects:project_list')


@method_decorator(require_http_methods(["GET", "POST"]), name='dispatch')
class LoginView(AuthLoginView):
    form_class = LoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('projects:project_list')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('projects:project_list')


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'users/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('users:user_detail',
                       kwargs={'user_id': self.request.user.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'users/change_password.html'

    def get(self, request):
        form = ChangePasswordForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:user_detail', user_id=request.user.id)
        return render(request, self.template_name, {'form': form})


class ParticipantsListView(ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    paginate_by = 12

    def get_queryset(self):
        queryset = User.objects.all()
        filter_type = self.request.GET.get('filter')

        if filter_type and self.request.user.is_authenticated:
            if filter_type == 'owners-of-favorite-projects':
                queryset = User.objects.filter(
                    owned_projects__favorites=self.request.user).distinct()
            elif filter_type == 'owners-of-participating-projects':
                queryset = User.objects.filter(
                    owned_projects__participants=self.request.user).distinct()
            elif filter_type == 'interested-in-my-projects':
                queryset = User.objects.filter(
                    favorite_projects__owner=self.request.user).distinct()
            elif filter_type == 'participants-of-my-projects':
                queryset = User.objects.filter(
                    participating_projects__owner=self.request.user).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_filter'] = self.request.GET.get('filter')
        return context
