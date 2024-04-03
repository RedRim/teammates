from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import Post, FriendRequest, Profile, Game


User = get_user_model()


class CustomUserAdmin(UserAdmin):
    filter_horizontal = ('friends',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('friends',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('friends',)}),
    )


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'image')


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'created')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('slug',
                    'user',
                    'photo',
                    'country',
                    'city',
                    'age',
                    'date_birth',
                    'created',
                    'rating')
    
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'image')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Game, GameAdmin)
