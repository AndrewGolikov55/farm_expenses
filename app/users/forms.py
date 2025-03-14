from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Адрес эл. почты", required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Адрес эл. почты',
            'id': 'id_email'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # username
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
            'id': 'id_username',
        })
        # password1
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль',
            'id': 'id_password1',
        })
        # password2
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повтор пароля',
            'id': 'id_password2',
        })
