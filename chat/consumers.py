import json
from django.utils import timezone
import pytz

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.shortcuts import get_object_or_404

from .models import Room, Message
from actions.models import Action

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def create_message(self, message):
        msg = Message.objects.create(room=self.room, user=self.user, content=message)
        if not self.room.is_active:
            self.room.is_active = True
            self.room.save()

    @database_sync_to_async
    def create_action(self, message):
        Action.objects.create(user=self.user, action=f'{self.user.username}: {self.room_name} -> {message}')

    
    @database_sync_to_async
    def get_room(self, room_name):
        return get_object_or_404(Room, slug=room_name)

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.room = await self.get_room(self.room_name)
        print(f'=== CONNECTED TO {self.room} ===')

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        irkutsk_timezone = pytz.timezone('Asia/Irkutsk')
        now = timezone.now()
        localized_time = now.astimezone(irkutsk_timezone)
        await self.create_message(message)
        await self.create_action(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': localized_time.strftime('%H:%M')
            }
        )


    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))