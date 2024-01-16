from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from gradingapp.forms import RegisterForm
from gradingapp.forms import GitHubAccessTokenForm
from home.views import list_classrooms
import requests
import json

# funcs

def list_assignments(ghat, classroom_id):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {ghat}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    response_assignments = requests.get(f'https://api.github.com/classrooms/{classroom_id}/assignments',
                                        headers=headers)
    response_assignments = json.loads(response_assignments.text)
    assignments_dict = {}
    for i in response_assignments:
        assignments_dict[i['title']] = i['id']
    return assignments_dict


# Create your views here.

def login_user(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        username = request.POST['username']
        github_access_token = request.POST['github_access_token']
        user = authenticate(username=username, password=github_access_token)
        if user is not None:
            login(request, user)
            if 'name' in request.session:
                del request.session['name']
            if 'ghat' in request.session:
                del request.session['github_access_token']
            request.session['name'] = username
            request.session['github_access_token'] = github_access_token
            return redirect('home:home')
        else:
            messages.success(request, "There was an error logging in. Try again.")
            return redirect('members:login')
    else:
        return render(request, 'authenticate/login.html', {})

def logout_user(request):
    messages.success(request, "You have successfully logged out.")
    logout(request)
    return render(request, 'home/templates/home.html', {})

def register_user(request):
    if request.POST == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            github_access_token = form.cleaned_data['password1']
        # add if validating ghat
            user = authenticate(username=username, password=github_access_token)
            login(request, user)
            if 'name' in request.session:
                del request.session['name']
            if 'ghat' in request.session:
                del request.session['github_access_token']
            request.session['name'] = username
            request.session['github_access_token'] = github_access_token
            messages.success(request, "Registration successful!")
            return redirect('home:home')
    else:
        form = RegisterForm()
        messages.success(request, "Registration error. Please try again.")
    return render(request, 'authenticate/register_user.html', {'form': form})

def show_class_options(request):
    context = {'class_dict': request.session['class_list']}
    return render(request, 'members/templates/class.html', context = context)

def show_assignments(request, CLASS_ID):
    request.session['assignment_dict'] = list_assignments(ghat = request.session['github_access_token'], classroom_id = CLASS_ID)
    context = {'assignment_dict': request.session['assignment_dict']}
    return render(request, 'members/templates/assignments.html', context = context)
