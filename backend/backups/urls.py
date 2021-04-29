from django.urls import path
from backups import views

urlpatterns = [
        path('', views.BackupView.as_view(), name='api-backups'),
        path('backup/<str:backup_id>/', views.BackupView.as_view()),
        path('status/', views.StatusView.as_view()),
        path('edit/<str:backup_id>/', views.BackupView.as_view(), name='api-backups-with-id'),
        path('run/<str:backup_id>/', views.BackupRunnerView.as_view()),
        path('delete/<str:backup_id>/', views.DeleteView.as_view()),
        path('logs/<str:backup_id>/', views.LogsView.as_view()),
        path('files/<str:backup_id>/', views.FilesView.as_view()),
        path('restore/<str:backup_id>/', views.RestoreFilesView.as_view()),
        path('restore/files/<str:backup_id>/', views.RestoreFilesView.as_view()),
]
