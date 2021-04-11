import json

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
def get_csrf(request):
    response = JsonResponse({'info': 'CSRF cookie received.'})
    response['X-CSRFToken'] = get_token(request)
    print(response['X-CSRFToken'])
    return response


def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')


    user = authenticate(username=username, password=password)
    login(request, user)
    return JsonResponse({'info': 'Login successful.'})


def logout_view(request):
    logout(request)
    return JsonResponse({'info': 'Logout successful.'})


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
    else:
        return JsonResponse({'isAuthenticated': True})


def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
    else:
        return JsonResponse({'isAuthenticated': True})
