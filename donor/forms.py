from django import forms
from django.contrib.auth.models import User
from . import models


class DonorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password','email']
        widgets = {
        'password': forms.PasswordInput()
        }

class DonorForm(forms.ModelForm):
    class Meta:
        model=models.Donor
        fields=['bloodgroup','address','mobile','profile_pic','age']

class DonationForm(forms.ModelForm):
    class Meta:
        model=models.BloodDonate
        fields=['disease','unit']
