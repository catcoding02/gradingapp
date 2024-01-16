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
    user = request.user
    if not UserProfile.objects.get(user_id = user.id):
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
            user = request.user
            UserProfile.objects.get(user_id = user.id).delete()
            user_profile.save()
            request.session['github_access_token'] = form.cleaned_data['github_access_token']
            request.session['class_list'] = list_classrooms(request.session['github_access_token'])
            return redirect('members:class')
        else:
            # if form not valid despite there already being stuff posted to the form
            # it must mean they are good with what they've got and it's time for them to move on
            request.session['github_access_token'] = form.cleaned_data['github_access_token']
            request.session['class_list'] = list_classrooms(request.session['github_access_token'])
            return redirect('members:class')
    else:
        user = request.user
        current_profile_obj = UserProfile.objects.get(user_id=user.id)
        form = UserProfileForm(instance = current_profile_obj)
        context = {'current_user_form': form, 'okur': 'you are logged in but you have already filled out the user profile stuff! you can edit it tho if u want'}
        return HttpResponse(template.render(context, request))

