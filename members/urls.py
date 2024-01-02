from django.urls import path
from . import views


urlpatterns = [
    path(route = 'login_user/', view = views.login_user, name = "login"),
]