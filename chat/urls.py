from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('private_room/<slug:room_name>/', views.private_chat_room, name='private_chat_room'),
]
