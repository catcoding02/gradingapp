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
    try:
        user_profile_test = UserProfile.objects.get(user = request.user.id)
    except UserProfile.DoesNotExist:
        user_profile_test = None
    # if no existing user profile info and request not post, which covers if it's a person's
    # first time submitting the form and they have yet to save a profile
    if not user_profile_test and not request.method == 'POST':
        form = UserProfileForm()
        context = {
                'user_profile_form': form,
                'no_profile_logged_in': 'You are currently logged in. You need to submit some user information before you proceed. Please provide information for ALL fields, and then press submit.'
            }
        return HttpResponse(template.render(context, request))
    # if new changes have been posted. this applies to users with an existing profile
    # or users who have just created their profile
    elif request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user = request.user
            # if user_profile_test is true, this handles case where there was an existing UserProfile
            # for this user and it needs to be deleted and then updated w/ new info
            # if this is user's first UserProfile, user_profile_test will return
            # false and this code is skipped over since no records need to be 
            # deleted before updating
            if user_profile_test:
                if not form.cleaned_data['json_file']:
                    json_file = user_profile_test.json_file
                    UserProfile.objects.get(user_id = user.id).delete()
                    user_profile.json_file = json_file
                    print("no json changes made it happen")
                elif form.cleaned_data['json_file']:
                    UserProfile.objects.get(user_id = user.id).delete()
            user_profile.save()
            return redirect('members:class')
        # after user has pressed submit button, but did not change anything
        else:       
            form = UserProfileForm()
            context = {'form': form, 'error': 'An error has occurred with the form submission. Make sure all fields have been filled in, or contact site admins for more help.'}
            return HttpResponse(template.render(context, request))
    else:
        # if user has profile and the info is there to post, no changes made yet
        user = request.user
        current_profile_obj = UserProfile.objects.get(user_id=user.id)
        form = UserProfileForm(instance = current_profile_obj)
        current_profile_obj.save()
        context = {'current_user_form': form, 'with_profile_logged_in': 'You are currently logged in. Your user profile information is displayed below. You can change it, or proceed to the next page.'}
        return HttpResponse(template.render(context, request))

