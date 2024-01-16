from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path(route = 'login_user/', view = views.login_user, name = "login"),
    path(route = 'logout_user/', view = views.logout_user, name = "logout"),
    path(route = 'register_user/', view = views.register_user, name = "register_user"),
    path(route = 'class/', view = views.show_class_options, name = "class"),
    path(route = '<str:CLASS_ID>/', view = views.show_assignments, name = "CLASS_ID"),
]