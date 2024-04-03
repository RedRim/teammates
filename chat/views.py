import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Room
from people.models import Profile
from actions.models import Action

@login_required
def private_chat_room(request, room_name):
    usernames = room_name.split('_')
    if request.user.username == usernames[0]:
        friend_username = usernames[1]
    else:
        friend_username = usernames[0]
    print(f'====={friend_username}=====')
    friend_profile = Profile.objects.get(slug=friend_username)
        
    friend = friend_profile.user
    if not (request.user.username.lower() in room_name.lower()):
        return HttpResponseForbidden()

    room = Room.objects.get(slug=room_name)
    other_rooms = Room.objects.filter(Q(user_1 = request.user) | Q(user_2=request.user)).filter(is_active=True)
    messages = room.messages.all()
    context = {'friend': friend,
               'room': room,
               'user_chats': other_rooms,
               'messages': messages}
    return render(request, 'chat/private_room.html', context=context)
