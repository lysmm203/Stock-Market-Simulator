from django.forms import ModelForm, TextInput, DateInput, Select, NumberInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from .models import StockParameters, StockTicker
from datetime import datetime, timedelta

class RegistrationForm(UserCreationForm):
    """
    The registration form that is displayed in the Registration page.
    """
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
    """
    The login form that is displayed in the Login page.
    """
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

class StockMarketParametersForm(ModelForm):
    """
    The form for the stock market parameters that is displayed on the Stock Market Parameters page.
    """

    class Meta:
        today = datetime.today().date()
        start_date_max = str(today - timedelta(days=2))
        end_date_max = str(today - timedelta(days=1))

        model = StockParameters
        fields = '__all__'
        widgets = {
            'money': NumberInput(attrs={
                'class': 'form-control-lg form-input-padding',
                'placeholder': 'Enter the Amount of Money to be Used for Your Portfolio',
                'min': '1',
                'max': '1000000'
            }),

            'start_date': DateInput(attrs={
                'class': 'form-control-lg form-input-padding',
                'type': 'date',
                'min': '1985-09-30',
                'max': start_date_max
            }),

            'end_date': DateInput(attrs={
                'class': 'form-control-lg form-input-padding',
                'type': 'date',
                'min': '1985-10-01',
                'max': end_date_max
            }),

            'index': Select(attrs={
                'class': 'form-control-lg form-input-padding',
                'style': 'border-color: black;'
            })
        }
