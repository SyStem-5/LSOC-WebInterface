from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy

from django.contrib.auth.models import User
from project01.models import LSOCProfile


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""

    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))

    password = forms.CharField(label=ugettext_lazy("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'Password'}))


class AccoutManagementForm(UserCreationForm):
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    email = forms.CharField(max_length=254,
                               widget=forms.EmailInput({
                                   'class': 'form-control',
                                   'placeholder': 'E-mail address'}))
    password1 = forms.CharField(label=ugettext_lazy("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'Password'}))
    password2 = forms.CharField(label=ugettext_lazy("Confirm Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'Confirm Password'}))
    lsoc_permissions = forms.CharField(widget=forms.TextInput({
                                      'class': 'form-control',
                                      'value': '{}',
                                      'readonly':'readonly'
                                      }))
    description = forms.CharField(max_length=100,
                                  widget=forms.TextInput({
                                      'class': 'form-control',
                                      'placeholder': 'Living room device.'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'lsoc_permissions', 'description',)

class AccountEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'email',
        )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = LSOCProfile
        fields = (
            'lsoc_permissions',
            'description'
        )

class MQTTConfigurationForm(forms.Form):

    #ip = forms.GenericIPAddressField(widget=forms.TextInput({
    #    'class': 'form-control',
    #    'type': 'text',
    #}))

    ip = forms.CharField(max_length=500, required=True,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'ex. 127.0.0.1'
                                   }))

    port = forms.IntegerField(max_value=65535,
                              widget=forms.NumberInput({
                                  'class': 'form-control',
                                  'placeholder': 'ex. 1883'
                              }))

    username = forms.CharField(max_length=100, required=False,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   }))

    password = forms.CharField(max_length=250, required=False,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   }))
