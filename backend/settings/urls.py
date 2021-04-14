from django.urls import path
from settings import views

urlpatterns = [
        path('', views.SettingsView.as_view(), name='settings'),
]
