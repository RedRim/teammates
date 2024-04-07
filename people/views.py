import json


from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


from .models import Profile, Post, FriendRequest, Game, SetRating
from .forms import AddPostForm, SearchForm, GameSelectionForm
from chat.models import Room
from actions.models import Action


class HomePageView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'people/index.html'

    def get_queryset(self):
        qs = None
        if self.request.user.is_authenticated:
            qs = Post.objects.filter(user__in=self.request.user.friends.all())
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        if self.request.user.is_authenticated:
            context['posts'] = self.get_queryset()
            context['friends'] = self.request.user.friends.all()
        return context


class UserFriends(ListView):
    template_name = 'people/user_friends.html'
    context_object_name = 'friends'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = User.objects.get(pk=user_id)
        return user.friends.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        self.user = User.objects.get(pk=user_id)
        friends = self.user.friends.all()
        context['user'] = self.user
        context['friends'] = friends
        return context


class ProfileView(DetailView, LoginRequiredMixin):
    model = Profile
    template_name = 'people/profile.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object().user
        posts = Post.objects.filter(user=user)
        me = self.request.user

        if me != user:
            if me.pk < user.pk:
                try:
                    room = Room.objects.get(user_1=me.pk, user_2=user.pk)
                except ObjectDoesNotExist:
                    room = Room(user_1=me, user_2=user)
                    room.save()
            else:
                try:
                    room = Room.objects.get(user_1=user, user_2=me)
                except ObjectDoesNotExist:
                    room = Room(user_1=user, user_2=me)
                    room.save()
            context['room'] = room
            Action.objects.create(user=self.request.user, action=f'{self.request.user.username} зашел в профиль к {user.username}')
        else:
            Action.objects.create(user=self.request.user, action=f'{self.request.user.username} зашел в свой профиль')

        if FriendRequest.objects.filter(user_to=user, user_from=me).exists():
            context['friend_button'] = 'Processing'
        elif me in user.friends.all():
            context['friend_button'] = 'Among_friends'
        else:
            context['friend_button'] = 'Add_to_friends'

        context['title'] = 'Профиль'
        context['user'] = user
        context['posts'] = posts
        context['games'] = user.games.all()
        return context


def add_post(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            form.save()
            Action.objects.create(user=request.user, action=f'{request.user.username} написал пост')
            return redirect(reverse('people:profile', kwargs={'slug': request.user.profile.slug}))
    else:
        form = AddPostForm()
    return render(request, 'people/add_post.html', {'form': form})


class FindFriendsView(ListView):
    model = User
    template_name = 'people/find_friends.html'
    form_class = SearchForm

    def get_queryset(self):
        user_friends = self.request.user.friends.all()
        object_list = User.objects.exclude(username=self.request.user.username)
        self.search_query = self.request.GET.get('query')
        if 'query' in self.request.GET:
            object_list = object_list.annotate(
                similarity=TrigramSimilarity('username', self.search_query)
            ).filter(similarity__gt=0.1).order_by('-similarity')
        else:
            object_list = object_list.exclude(id__in=user_friends)
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['users'] = self.get_queryset()
        context['form'] = self.form_class()
        context['query'] = self.search_query
        return context
    

def add_friend(request, user_to_id):
    user_from = request.user
    user_to = get_object_or_404(User, id=user_to_id)
    if not FriendRequest.objects.filter(user_from=user_from, user_to=user_to).exists():
        FriendRequest.objects.create(user_from=user_from, user_to=user_to)
        Action.objects.create(user=request.user, action=f'{request.user.username} отправил запрос в друзья {user_to.username}')
    return redirect(reverse('people:profile', kwargs={'slug': user_to.profile.slug}))


def cancel_adding_friend(request, user_to_id):
    user_from = request.user
    user_to = get_object_or_404(User, id=user_to_id)
    if FriendRequest.objects.filter(user_from=user_from, user_to=user_to).exists():
        FriendRequest.objects.get(user_from=user_from, user_to=user_to).delete()
    return redirect(reverse('people:profile', kwargs={'slug': user_to.profile.slug}))


class FriendsRequestsList(ListView):
    model = FriendRequest
    template_name = 'people/friends_requests_list.html'

    def get_queryset(self):
        qs = FriendRequest.objects.filter(user_to=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['people_requests'] = self.get_queryset()
        return context


class AcceptFriendResponseView(View):
    def post(self, request):
        user_from_id = request.POST.get('user_from_id')
        action = request.POST.get('action')
        if action and user_from_id:
            try:
                user_from = User.objects.get(pk=user_from_id)
                user_to = request.user
                if action == 'accept':
                    user_to.friends.add(user_from)
                FriendRequest.objects.filter(
                    user_from=user_from, user_to=user_to).delete()
                Action.objects.create(user=self.request.user, action=f'{self.request.user.username} добавил в друзья {user_from.username}')
                return JsonResponse({'status': 'ok'})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error'})
        return JsonResponse({'status': 'error'})


# class AddPostView(LoginRequiredMixin, CreateView):
#     user_form = AddPostForm
#     template_name = 'people/add_post.html'
#     success_url = 'people:profile'
#     fields = ['text', 'image']

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         Post.objects.create(user=self.request.user)
#         Action.objects.create(user=self.request.user, action=f'{self.request.user.username} написал пост')


class GamesList(ListView):
    model = Game
    template_name = 'people/games.html'

# class AddGameView(UpdateView):
#     model = User
#     form_class = GameSelectionForm
#     template_name = 'people/games.html'
#     pk_url_kwarg = 'user_id'

#     def form_valid(self, form):
#         games = form.cleaned_data['games']
#         for game in games:
#             game.users.add(self.request.user)
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy('people:profile', kwargs={'slug': self.request.user.profile.slug})


def chosen_games(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_games = data.get('games', [])
        user = request.user
        user.games.clear()
        for game_slug in selected_games:
            game = get_object_or_404(Game, slug=game_slug)
            user.games.add(game)
        Action.objects.create(user=request.user, action=f'{request.user.username} изменил список игр')
        return JsonResponse({'message': 'Данные о выбранных играх успешно получены'}, status=200)
    else:
        return JsonResponse({'error': 'Неправильный метод запроса'}, status=400)

    

def set_rating(request):
    if request.method == 'POST': 
        data = json.loads(request.body)
        rating_from = int(data.get('rating', None))
        user_to_id = int(data.get('user_id', None))
        user_to = get_object_or_404(User, pk=user_to_id)
        user_from = request.user
        Action.objects.create(user=request.user, action=f'{request.user.username} поставил {rating_from} для {user_to.username}')
        if not SetRating.objects.filter(user_from=user_from, user_to=user_to).exists():
            SetRating.objects.create(user_from=user_from, user_to=user_to, rating=rating_from)
            rating_count = SetRating.objects.filter(user_to=user_to).count()
            if rating_count == 0 or user_to.profile.rating == 0.00:
                new_rating = rating_from
            else:  
                new_rating = (user_to.profile.rating * rating_count + rating_from) / (rating_count + 1)
            user_to.profile.rating = new_rating
            user_to.profile.save()
        else:
            pass
        return JsonResponse({'message': 'Данные о рейтинге успешно получены'}, status=200)
    else:
        return JsonResponse({'error': 'Неправильный метод запроса'}, status=400)
    