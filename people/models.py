from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model


class Profile(models.Model):
    slug = models.SlugField(unique=True, db_index=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(
        upload_to="photos/%Y/%m/%d/", default='photos/default_photo.jpeg')
    country = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    age = models.IntegerField(blank=True, null=True)
    date_birth = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.user.username)
        slug = base_slug
        i = 0
        while Profile.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{i}'
            i += 1
        if i:
            self.slug = f'{base_slug}_{i}'
        else:
            self.slug = base_slug
        print(self.slug)
        super().save(*args, **kwargs)

    def get_rounded_rating(self):
        return round(self.rating)

    def get_absolute_url(self):
        return reverse('people:profile', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.user.username}_profile'
    
    def calculate_age(self):
        if self.date_birth:
            today = date.today()
            birth_date = self.date_birth.date()
            self.age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(
        upload_to='blog_images/%Y/%m/%d/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

class FriendRequest(models.Model):
    user_from = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='requests_to', null=True)
    user_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='requests_from', null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    
class Game(models.Model):
    slug = models.SlugField(unique=True, db_index=True, null=True)
    title = models.CharField(max_length=30)
    users = models.ManyToManyField(get_user_model(), related_name='games', blank=True)
    image = models.ImageField(upload_to='games_images/%Y/%m/%d/')

    def __str__(self):
        return self.slug
    

class SetRating(models.Model):
    user_from = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rate_to', null=True)
    user_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rate_from', null=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])



user_model = get_user_model()
user_model.add_to_class('friends', models.ManyToManyField(
    'self', symmetrical=True, blank=True))
