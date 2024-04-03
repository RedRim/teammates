from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

    
class Room(models.Model):
    slug = models.SlugField(unique=True, db_index=True)
    user_1 = models.ForeignKey(User, related_name='user_1_chats', on_delete=models.CASCADE)
    user_2 = models.ForeignKey(User, related_name='user_2_chats', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.slug
    
    def get_absolute_url(self):
        return reverse('chat:private_chat_room', kwargs={'room_name': self.slug})
    
    def save(self, *args, **kwargs):
        if self.user_1.id < self.user_2.id:
            
            self.slug = f'{self.user_1.profile.slug}_{self.user_2.profile.slug}'
        else:
            self.slug = f'{self.user_2.profile.slug}_{self.user_1.profile.slug}'
        super().save(*args, **kwargs)

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} sent "{self.content}" in {self.room}'