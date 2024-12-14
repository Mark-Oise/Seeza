from django import forms
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    name = forms.CharField(max_length=256, label='Name')

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(max_length=256, label='Name')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user
