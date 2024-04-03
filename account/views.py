from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views

from .forms import (
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm,
    CustomSetPasswordForm
)

from people.models import Profile
from actions.models import Action


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        username = user_form['username']
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Action.objects.create(user=new_user, action=f'{new_user.username} создал аккаунт')
            login(request, user_form.instance)
            Profile.objects.create(user=request.user)
            return redirect('people:home_page')

    else:
        user_form = UserRegistrationForm()

    context = {'title': 'Регистрация',
               'form': user_form}
    return render(request, 'account/register.html', context)


class ProfileUpdateView(UpdateView, LoginRequiredMixin):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'account/profile_update.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить профиль'
        if self.request.method == 'POST':
            context['user_form'] = UserUpdateForm(
                self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(
                instance=self.request.user)

        profile = self.request.user.profile
        form_values = {
            'username': self.request.user.username,
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'email': self.request.user.email,
            'photo': profile.photo, 
            'country': profile.country,
            'city': profile.city,
            'date_birth': profile.date_birth,
        }
        context |= form_values
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user = self.get_object()
                user.calculate_age()
                user_form.save()
                form.save()
                Action.objects.create(user=self.request.user, action=f'{self.request.user.username} изменил свой профиль')
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('people:profile', kwargs={'slug': self.object.slug})


class CustomPasswordResetConfirmView(views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm


# class RegisterUserView(CreateView):
#     model = User
#     form_class = UserRegistrationForm
#     template_name = 'account/register.html'
#     success_url = reverse_lazy('people:home_page')

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         login(self.request, form.instance)
#         Profile.objects.create(user=self.request.user)
#         return response

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = self.get_form()
#         context['title'] = 'Регистрация'
#         return context
