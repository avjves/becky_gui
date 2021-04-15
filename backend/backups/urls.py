from django.urls import path
from backups import views

urlpatterns = [
        path('', views.BackupView.as_view(), name='api-backups'),
        path('edit/<str:backup_id>/', views.BackupView.as_view(), name='api-backups-with-id'),
        path('run/<str:backup_id>/', views.BackupRunnerView.as_view()),
        path('logs/<str:backup_id>/', views.LogsView.as_view()),
        path('files/<str:backup_id>/', views.FilesView.as_view()),
]
