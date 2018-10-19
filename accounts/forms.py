from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import MyUser


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    bio = forms.CharField(widget=forms.HiddenInput(), required=False, max_length=400)

    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
