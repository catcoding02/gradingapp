from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.forms.utils import ErrorList
from django.forms import formset_factory
from django.contrib.auth.forms import UserCreationForm
from members.models import Class,Student,UserProfile,ExtraComments
import requests
import json
 
 # creating list_classrooms

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
        classroom_list = list(classrooms_dict.keys())
        classroom_list_dropdown = []
        for i in classroom_list:
            tuple = (f'{i}', f'{i}')
            classroom_list_dropdown.append(tuple)
        return classroom_list_dropdown

# creating a form 
class GitHubAccessTokenForm(forms.ModelForm):
    class Meta:
         model=Class
         fields = '__all__'

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Password Confirmation'
        self.fields['username'].label = 'Username'
        self.fields['password2'].help_text = "Enter the same Password as before, for verification."

     
class AccAssignmentsForm(forms.Form):
     student = forms.BooleanField()
     class Meta:
          model = Student
          fields = '__all__'

class ExtraCommentsForm(forms.ModelForm):
     class Meta:
          model=ExtraComments
          fields = '__all__'

class UserProfileForm(forms.ModelForm):
     class Meta:
          model=UserProfile
          fields = ['json_file', 'github_access_token', 'google_sheet_name']