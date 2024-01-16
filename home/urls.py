from django.urls import path 
from . import views
from members.views import register_user

app_name = 'home'

urlpatterns = [
    # because we have path('playground/') in our 'gradingapp urls.py' document, we don't
    # need the playground/ before 'hello' here since we've already specified this route
    path(route = 'home/', view = views.welcome_home, name = "home"),
]