from dkango.urls import path, include
from . import views

urlpattherns=[
    path('', views.home, name = 'home'),
]