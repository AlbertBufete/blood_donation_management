from django import forms
from django.contrib.auth.models import User
from . import models


class PatientForm(forms.ModelForm):

    class Meta:
        model=models.Patient
        fields=['age','bloodgroup','disease','address','doctorname','mobile']
class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password','email']
        widgets = {
        'password': forms.PasswordInput()
        }

