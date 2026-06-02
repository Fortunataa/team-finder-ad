from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(),
         name='project_list'),
    path('favorites/', views.FavoriteProjectsView.as_view(),
         name='favorite_projects'),
    path('create-project/', views.ProjectCreateView.as_view(),
         name='project_create'),
    path('<int:project_id>/edit/', views.ProjectEditView.as_view(),
         name='project_edit'),
    path('<int:project_id>/', views.ProjectDetailView.as_view(),
         name='project_detail'),
    path('api/skills/', views.SkillSearchView.as_view(), name='skill_search'),
    path('api/<int:project_id>/skills/add/', views.SkillAddView.as_view(),
         name='skill_add'),
    path('api/<int:project_id>/skills/<int:skill_id>/remove/',
         views.SkillRemoveView.as_view(), name='skill_remove'),
    path('api/participate/<int:project_id>/', views.ParticipateView.as_view(),
         name='participate'),
    path('api/complete/<int:project_id>/', views.CompleteProjectView.as_view(),
         name='complete_project'),
    path('api/favorite/<int:project_id>/', views.ToggleFavoriteView.as_view(),
         name='toggle_favorite'),
]
