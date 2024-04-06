from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.auth.forms import SetPasswordForm
from django.utils.text import slugify


from people.models import Profile


class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": _("Пароли не совпадают"),
    }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают.')
        elif len(cd['password2']) < 4:
            raise forms.ValidationError(
                'Пароль должен содержать минимум 4 символа.')
        return cd['password2']


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    error_messages = {
        'duplicate_username': _('Пользователь с таким именем уже сущесвтвует.'),
        'duplicate_email': _('Пользователь с таким email уже сущесвтвует.'),
        'password_mismatch': _('Пароли не совпадают'),
    }

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(self.error_messages['duplicate_email'])
        return data

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают.')
        elif len(cd['password2']) < 4:
            raise forms.ValidationError(
                'Пароль должен содержать минимум 4 символа.')
        return cd['password2']

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_username'])
        return data


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['country',
                  'city',
                  'date_birth',
                  'photo']
