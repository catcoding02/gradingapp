from django.shortcuts import render, redirect
import requests
import json
from django.views.generic.edit import FormView
from gradingapp.forms import AccAssignmentsForm
from members.models import Student,GradingConfig,UserProfile
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# helper funcs

def list_acc_assignments(ghat, ASSIGNMENT_ID):
    headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {ghat}',
    'X-GitHub-Api-Version': '2022-11-28',
}
    response_accepted = requests.get(f'https://api.github.com/assignments/{ASSIGNMENT_ID}/accepted_assignments', headers=headers)
    response_accepted = json.loads(response_accepted.text)
    dict = {}
    for i in response_accepted:
        if len(i['students']) > 1:
            length = len(i['students'])
            dict_key = []
            for x in range(0, length):
                dict_key.append(i['students'][x]['login'])
            dict_key_str = "| "
            for name in dict_key:
                dict_key_str += name + " | "
            dict[dict_key_str] = i['repository']['full_name']
        if len(i['students']) == 1:
            dict[i['students'][0]['login']] = i['repository']['full_name']
    return dict

def get_grading_config_objects():
    grading_config = GradingConfig.objects.all()
    grading_config_dict = {}
    for entry in grading_config:
        grading_config_dict[entry.standard] = [entry.points, entry.row]
    return grading_config_dict

def run_the_grader(ghat, request):
    def google_sheets_setup(request):
        """
        Run Google Sheets set-up
        """
        user = request.user
        current_user = UserProfile.objects.get(user = user.id)
        json_file = current_user.json_file
        with open(json_file) as json_file:
            unloaded_json = json.loads(json_file)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(unloaded_json,
                                                                       scopes)
        client = gspread.authorize(credentials)  # authenticates  the JSON key with gspread
        sheet = client.open("SDS192 Gradebooks")
        return sheet
    def get_contributors(ghat, repository_list):
        """
        Gets contribitors to GitHub repository. Should return one student if lab, or all students 
        in a team if this is a mini-project
        """
        headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {ghat}',
    'X-GitHub-Api-Version': '2022-11-28',
}

    def transfer_comments():
        """
        Transfers GitHub grades and comments to Google Sheets gradebook
        """
        pass
# Create your views here.

def show_acc_assignments(request, ASSIGNMENT_ID):
    if request.method == "POST":
        form = AccAssignmentsForm(request.POST)
        if form.is_valid():
            obj = Student()
            if request.POST.getlist('student'):
                request.session['grading_list'] = request.POST.getlist('student')
                request.session['grading_config_dict'] = get_grading_config_objects()
                # run run_the_grader() function here to do the grading stuff. Then redirect to some
                # process successful or process failed page instead of accepted assignments html.
            return render(request, 'class/templates/accepted_assignments.html')
        else:
            form = AccAssignmentsForm()
            context = {
            'form': form
        }
            request.session['accepted_assignments_dict'] = list_acc_assignments(ghat = request.session['github_access_token'], ASSIGNMENT_ID = ASSIGNMENT_ID)
            context = {'accepted_assignments': request.session['accepted_assignments_dict']}
            return render(request, 'class/templates/accepted_assignments.html', context = context)

    else:
        request.session['grading_config_dict'] = get_grading_config_objects()
        form = AccAssignmentsForm()
        context = {
        'form': form
    }
        request.session['accepted_assignments_dict'] = list_acc_assignments(ghat = request.session['github_access_token'], ASSIGNMENT_ID = ASSIGNMENT_ID)
        context = {'accepted_assignments': request.session['accepted_assignments_dict']}
        return render(request, 'class/templates/accepted_assignments.html', context = context)

def grade_acc_assignments(request):
    pass


def formset_view(request, ASSIGNMENT_ID):
    formset = modelformset_factory(GradingConfig, fields = ('standard', 'points', 'row'), extra = 10)
    if request.method == "POST":
        form = formset(request.POST)
        form.save()
        next = request.POST.get('next')
        return HttpResponseRedirect(next)
    else:
        redirect('https://weather.com')
    form = formset()
    return render(request, 'class/templates/formset.html', {'formset':form, 'assignment_id': ASSIGNMENT_ID})
