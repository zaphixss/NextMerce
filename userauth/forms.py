from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': "block w-full rounded-xl border border-zinc-200 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline:none",
                'placeholder': 'email'
            }
        )
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': "block w-full rounded-xl border border-zinc-200 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline:none",
                'placeholder': 'username'
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': "block w-full rounded-xl border border-zinc-200 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline:none",
                'placeholder': 'password'
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': "block w-full rounded-xl border border-zinc-200 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline:none",
                'placeholder': 'confirm password'
            }
        )
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

class LoginForm(AuthenticationForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': "block w-full rounded-xl border border-zinc-200 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline:none",
                'placeholder': 'Email'
            }
        )
    )

    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': "block w-full rounded-xl border border-zinc-200 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline:none",
                'placeholder': 'username'
            }
        )
    )