from django.urls import path
from . import views

app_name = 'class'

urlpatterns = [
    path(route = '<str:ASSIGNMENT_ID>/', view = views.show_acc_assignments, name = "ASSIGNMENT_ID"),
    path(route = '<str:ASSIGNMENT_ID>/formset/', view = views.formset_view, name = 'FORMSET'),
]