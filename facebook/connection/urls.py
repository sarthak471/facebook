from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_user),
    path("login/", views.login_user),
    path('search-users/', views.search_users, name='search-users'),
    path('send_request/<int:user_id>/', views.send_friend_request, name='send-friend-request'),
    path('accept_request/<int:user_id>/', views.accept_friend_request, name='accept-friend-request'),
    path('reject_request/<int:user_id>/', views.reject_friend_request, name='reject-friend-request'),
    path('friends/', views.list_friends, name='list-friends'),
    path('pending/', views.pending_request, name='pending-request')
]
