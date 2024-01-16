from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.template import loader
from members.models import UserProfile
from gradingapp.forms import GitHubAccessTokenForm,UserProfileForm
import debug_toolbar
import requests
import json

def list_classrooms(ghat):
        headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {ghat}',
    'X-GitHub-Api-Version': '2022-11-28',
}
        response_classrooms = requests.get('https://api.github.com/classrooms', headers=headers)
        response_classrooms = json.loads(response_classrooms.text)
        classrooms_dict = {}
        for i in response_classrooms:
            classrooms_dict[i['name']] = i['id']
        return classrooms_dict

# Create your views here.

def welcome_home(request):
    template = loader.get_template('home.html')
    # if user is authenticated, collect variables to use for token
    # and then run the function to get classrooms. else user not
    # authenticated, home.html would still render with empty
    # context which shouldn't be a problem since we aren't
    # asking to display any context in that case anyways
    # getting form
    if not UserProfile.objects.filter(user = request.user):
        form = UserProfileForm()
        context = {
                'user_profile_form': form
            }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            # deletes current instance and replaces with new one
            UserProfile.objects.filter(user = request.user).delete()
            user_profile.save()
            request.session['github_access_token'] = form.cleaned_data['github_access_token']
            request.session['class_list'] = list_classrooms(request.session['github_access_token'])
            return redirect('members:class')
        else:
            form = UserProfileForm()
            context = {
            'user_profile_form': form
        }
            return redirect('https://weather.com')
    else:
        current_profile_obj = UserProfile.objects.get(user = request.user)
        form = UserProfileForm(instance = current_profile_obj)
        context = {'current_user_form': form, 'okur': 'you are logged in but you have already filled out the user profile stuff! you can edit it tho if u want'}
        return HttpResponse(template.render(context, request))

