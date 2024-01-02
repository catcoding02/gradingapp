from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.template import loader
import debug_toolbar
import requests
import json

# Create your views here.

def welcome_home(request):
    template = loader.get_template('home.html')
    def list_assignments(token = 1, classroom_id = 2):
        headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'Bearer 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',
    'X-GitHub-Api-Version': '2022-11-28',
}
        classroom_id = 187239

        response = requests.get(f'https://api.github.com/classrooms/{classroom_id}/assignments', headers=headers)
        response = json.loads(response.text)
        assignment_list = []
        for i in response:
            assignment_list.append(i['title'])
        return assignment_list
    
    assignment_list = list_assignments()
    context = {
        'list': ['cat', 'dog', 'rat'],
        'response': assignment_list
    }
    
    return HttpResponse(template.render(context, request))


