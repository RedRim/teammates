from django import forms

from .models import Post, Game


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image']


class SearchForm(forms.Form):
    query = forms.CharField()


class GameSelectionForm(forms.Form):
    games = forms.ModelMultipleChoiceField(queryset=Game.objects.all(), widget=forms.CheckboxSelectMultiple)