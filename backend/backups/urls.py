from django.urls import path
from backups import views

urlpatterns = [
        path('', views.BackupView.as_view(), name='api-backups'),
        path('<str:backup_id>/', views.BackupView.as_view(), name='api-backups-with-id'),
]
