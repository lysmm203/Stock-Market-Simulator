from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter Your Username',
            'class': 'form-control-lg form-input-padding'

        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter Your Password',
            'class': 'form-control-lg form-input-padding'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Enter Your Password Again',
            'class': 'form-control-lg form-input-padding'
        })

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter Your Username',
            'class': 'form-control-lg form-input-padding'

        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Enter Your Password',
            'class': 'form-control-lg form-input-padding'
        })

    class Meta:
        model = User
        fields = ['username', 'password']