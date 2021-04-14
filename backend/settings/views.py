import json
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse, JsonResponse
from settings.models import GlobalParameter

class SettingsView(View):

    def get(self, request, **kwargs):
        """
        Returns all global settings as a JSON dictionary.
        """
        params = GlobalParameter.get_all_global_parameters()
        return JsonResponse({'settings': params})


    def post(self, request, **kwargs):
        """
        Gets arbitrary amount of keys from the user and saves the to the DB.
        """
        data = json.loads(request.body)
        print(data)
        params = data['settings']
        for key, value in params.items():
            GlobalParameter.save_parameter(key, value)
        return HttpResponse(status=200)
        
