from django.urls import path

from . import views

app_name = 'people'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),
    path('messages/', views.messages, name='messages'),
    path('add_post/', views.add_post, name='add_post'),

    path('add_friend/<int:user_to_id>/', views.add_friend, name='add_friend'),
    path('cancel_adding_friend/<int:user_to_id>/', views.cancel_adding_friend, name='cancel_adding_friend'),
    path('find_friends/', views.FindFriendsView.as_view(), name='find_friends'),
    path('friends_requests/', views.FriendsRequestsList.as_view(), name='friends_requests'),
    path('action_request/',views.AcceptFriendResponseView.as_view(), name='action_request'),

    path('games/',views.GamesList.as_view(), name='games'),
    path('chosen_games/',views.chosen_games, name='chosen_games'),
    path('set_rating/',views.set_rating, name='set_rating'),

    path('<slug:slug>/', views.ProfileView.as_view(), name='profile'),
    path('friends/<int:user_id>', views.UserFriends.as_view(), name='user_friends'),

]
# path('add_post/', views.AddPostView.as_view(), name='add_post'),
