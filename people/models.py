from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Gamer(models.Model):
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[
                                 MinValueValidator(0), MaxValueValidator(0)])
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='gamer')
    friends = models.ManyToManyField(User, related_name='gamers')

    class Meta:
        ordering = ['-rating']
        indexes = [
            models.Index(fields=['-rating'])
        ]

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    country = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    age = models.IntegerField()
    date_birth = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='images', null=True, blank=True)


class FriendRequest(models.Model):
    user_from = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_from')
    user_to = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_to')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
