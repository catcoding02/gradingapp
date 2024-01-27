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
from github import Github,Auth
import github
import re

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
            dict_key_str = ""
            for index,name in enumerate(dict_key):
                if index + 1 < length:
                    dict_key_str += name + "|"
                else:
                    dict_key_str += name
            dict[dict_key_str] = i['repository']['full_name']
        if len(i['students']) == 1:
            dict[i['students'][0]['login']] = i['repository']['full_name']
    return dict

def get_grading_config_objects():
    # filtering for ones that are not null only in case that user has deleted some of the
    # previously stored SPRs and left them blank
    grading_config = GradingConfig.objects.filter(standard__isnull=False, points__isnull=False, row__isnull=False)
    grading_config_dict = {}
    for entry in grading_config:
        grading_config_dict[entry.standard] = [entry.points, entry.row]
    return grading_config_dict

def google_sheets_setup(request):
        """
        Run Google Sheets set-up
        """
        user = request.user
        current_user = UserProfile.objects.get(user = user.id)
        opened_json_file = current_user.json_file.open('r')
        # returns json file as dictionary
        unloaded_json = json.load(opened_json_file)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(unloaded_json,
                                                                    scopes)
        client = gspread.authorize(credentials)  # authenticates  the JSON key with gspread
        sheet_name = current_user.google_sheet_name
        sheet = client.open(sheet_name)
        return sheet

def get_contributors(request):
    """
    Gets contribitors to GitHub repository. Should return one student if lab, or all students 
    in a team if this is a mini-project
    :Returns: dict: key is repository name, values are student contributors
    """
    dict = request.session['accepted_assignments_dict']
    contrib_dict = {}
    contrib_list_all = []
    for i in list(dict.keys()):
        contrib_as_list = list(i.split("|"))
        contrib_list_all.append(contrib_as_list)
    for index,repo in enumerate(list(dict.values())):
        contrib_dict[repo] = contrib_list_all[index]
    print(contrib_dict)
    return contrib_dict

def run_the_grader(request):

    def google_sheets_setup(request):
        """
        Run Google Sheets set-up. See above. Tried and tested!
        """
        user = request.user
        current_user = UserProfile.objects.get(user = user.id)
        opened_json_file = current_user.json_file.open('r')
        # returns json file as dictionary
        unloaded_json = json.load(opened_json_file)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(unloaded_json,
                                                                    scopes)
        client = gspread.authorize(credentials)  # authenticates  the JSON key with gspread
        sheet_name = current_user.google_sheet_name
        sheet = client.open(sheet_name)
        return sheet
    def get_contributors(request):
        """
        Gets contribitors to GitHub repository. Should return one student if lab, or all students 
        in a team if this is a mini-project
        :Returns: dict: key is repository name, values are student contributors
        """
        dict = request.session['accepted_assignments_dict']
        contrib_dict = {}
        contrib_list_all = []
        for i in list(dict.keys()):
            contrib_as_list = list(i.split("|"))
            contrib_list_all.append(contrib_as_list)
        for index,repo in enumerate(list(dict.values())):
            contrib_dict[repo] = contrib_list_all[index]
        print(contrib_dict)
        return contrib_dict
    def transfer_comments(request, sheet, contrib_dict):
        """
        Transfers GitHub grades and comments to Google Sheets gradebook
        :params:
        sheet: return from google_sheets_setup()
        contrib_dict: return from get_contributors()
        """
        
        def to_input(comments, worksheet, grading_config_dict):
            """
            Handles cases where student has a commit and has a comment. Handles comments that deduct
            standard points as well as a comment that indicates 100% successful completion
            :params:
            comments: comment object from .get_pulls_comments()
            worksheet: lab_sheet from above
            """
            for comment in comments: 
                if "Complete: " in comment.body:
                     for standard in list(grading_config_dict.keys()):
                        points = float(grading_config_dict[f'{standard}'][0])
                        row = float(grading_config_dict[f'{standard}'][1])
                        worksheet.update_acell(f'F{row}', f'{points}')
                else:
                    for standard in list(grading_config_dict.keys()):
                        if standard in comment.body:
                            # handle points
                            points = re.search(f"{standard}: \d+\.\d+", comment.body).group(0)
                            points = re.search("\d+\.\d+", points).group(0)
                            points = float(points)
                            row = float(grading_config_dict[f'{standard}'][1])
                            # handle comment
                            standard_comment_start = comment.body.find(f'{standard}: ')
                            standard_comment_end = comment.body.find("\n", standard_comment_start)
                            standard_comment = comment.body[standard_comment_start:standard_comment_end]
                            print(standard_comment)
                            worksheet.update_acell(f'F{row}', f'{points}')
                            worksheet.update_acell(f'G{row}', standard_comment)
                            # once comment with standard has been found, final points have been deduced
                            # and move to next standard
                            break
                        else:
                            print("continue")
                            continue

        # run transfer_comments main stuff
        ghat = request.session['github_access_token']
        contrib_dict_keys = list(contrib_dict.keys())
        contrib_dict_values = list(contrib_dict.values())
        for index,repo in enumerate(contrib_dict_keys):
            # get repo
            assignment_repo = Github(auth=github.Auth.Token(f'{ghat}')).get_repo(repo)
            # get corresponding student list for repo
            student_list = contrib_dict_values[index]
            # get comments from repo
            comments = assignment_repo.get_pulls_comments()
            # publish grades
            for student in student_list:
                # find student worksheet in Google Sheets
                lab_sheet = sheet.worksheet(student)
                if comments.totalCount > 0:
                    to_input(comments = comments, worksheet = lab_sheet, grading_config_dict = request.session['grading_config_dict'])
                else:
                    # no commit, break and go to next student
                    print(f"No commit for {student}!")
                    continue

    # run run_the_grader main stuff
    sheet = google_sheets_setup(request = request)
    all_contrib = get_contributors(request = request)
    filtered_contrib = {select: all_contrib[select] for select in request.session['grading_list']}
    transfer_comments(request = request, sheet = sheet, contrib_dict = filtered_contrib)
            
# Create your views here.

def show_acc_assignments(request, ASSIGNMENT_ID):
    if request.method == "POST":
        form = AccAssignmentsForm(request.POST)
        if form.is_valid():
            if request.POST.getlist('student'):
                request.session['grading_list'] = request.POST.getlist('student')
                request.session['grading_config_dict'] = get_grading_config_objects()
                # func testing
                google_sheets_setup(request)
                # gets dict for ALL assignments
                all_contrib = get_contributors(request)
                # filters for selected assignments
                filtered_contrib = {select: all_contrib[select] for select in request.session['grading_list']}
                # run run_the_grader() function here to do the grading stuff. Then redirect to some
                # process successful or process failed page instead of accepted assignments html.
                try:
                    run_the_grader(request)
                    context = {'process_done': 'Process Done!'}
                except Exception as error:
                    print(type(error).__name__)
                    context = {'process_failed': 'Process Failed!'}
            return render(request, 'class/templates/process.html', context)
        else:
            form = AccAssignmentsForm()
            context = {
            'form': form
        }
            request.session['accepted_assignments_dict'] = list_acc_assignments(ghat = request.session['github_access_token'], ASSIGNMENT_ID = ASSIGNMENT_ID)
            context = {'accepted_assignments': request.session['accepted_assignments_dict']}
            google_sheets_setup(request = request)
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
