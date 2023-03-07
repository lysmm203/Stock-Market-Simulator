from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    #Use the user creation form

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(ModelForm):
    pass