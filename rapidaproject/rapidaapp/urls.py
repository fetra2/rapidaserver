from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),#normaly to home page
    path('login/', views.login_form, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('users/', views.list_users, name='users'),
    path('users/new', views.new_users, name='new_users'),
    path('users/<int:id>', views.edit_form_users, name='edit_form_users'),
    path('check_auth', views.check_auth, name='check_auth'),
    path('search/', views.search_form, name='search_form'),
    path('find/', views.find, name='find'),
    path('event/', views.add_event, name="event"),
    path('event/ajax_find/', views.ajax_find, name='ajax_find'),
    path('event/ajax_add/', views.ajax_add, name='ajax_add'),

]