from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from gradingapp.forms import RegisterForm
from gradingapp.forms import GitHubAccessTokenForm
from home.views import list_classrooms
import requests
import json
from members.models import UserProfile

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
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home:home')
    else:
        form = RegisterForm()
    return render(request, 'authenticate/register_user.html', {'form': form})

def show_class_options(request):
    # if no changes had been made to user profile and user was directed right to class page, that means 
    # request.session['class_list'] = list_classrooms() was not done, nor was setting
    # request.session['github_access_token'] done
    user = request.user
    current_user = UserProfile.objects.get(user = user.id)
    request.session['github_access_token'] = current_user.github_access_token
    request.session['class_list'] = list_classrooms(request.session['github_access_token'])
    context = {'class_dict': request.session['class_list']}
    return render(request, 'members/templates/class.html', context = context)

def show_assignments(request, CLASS_ID):
    request.session['assignment_dict'] = list_assignments(ghat = request.session['github_access_token'], classroom_id = CLASS_ID)
    context = {'assignment_dict': request.session['assignment_dict']}
    return render(request, 'members/templates/assignments.html', context = context)
