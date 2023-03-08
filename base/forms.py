from django.forms import ModelForm, TextInput, DateInput, Select
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from .models import StockParameters

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


class StockMarketParametersForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['money'].widget.attrs.update({
    #         'placeholder': 'Amount of Money for Your Portfolio',
    #         'class': 'form-control-lg form-input-padding'
    #     })
    #     self.fields['start_date'].widget.attrs.update({
    #         'placeholder': 'Start Date of the Simulation ',
    #         'class': 'form-control-lg form-input-padding'
    #     })
    #     self.fields['end_date'].widget.attrs.update({
    #         'placeholder': 'End Date of the Simulation',
    #         'class': 'form-control-lg form-input-padding'
    #     })
    #     self.fields['index'].widget.attrs.update({
    #         'class': 'form-control-lg form-input-padding'
    #     })

    class Meta:
        model = StockParameters
        fields = '__all__'
        widgets = {
            'money': TextInput(attrs={
                'class': 'form-control-lg form-input-padding',
                'placeholder': 'Enter the Amount of Money to be Used for Your Portfolio'
            }),

            'start_date': DateInput(attrs={
                'class': 'form-control-lg form-input-padding',
                'type': 'date'
            }),

            'end_date': DateInput(attrs={
                'class': 'form-control-lg form-input-padding',
                'type': 'date'
            }),

            'index': Select(attrs={
                'class': 'form-control-lg form-input-padding',
                'style': 'border-color: black;'
            })
        }
