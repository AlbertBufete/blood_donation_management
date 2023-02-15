from django import forms

from . import models

class BloodForm(forms.ModelForm):
    class Meta:
        model=models.Stock
        fields=['bloodgroup','unit']
class BloodTestForm(forms.ModelForm):
    class Meta:
        model=models.BloodTest
        fields=['hepaB','hepaC','hiv1','hiv2','htlv1','htlv2','syphilis','westNile','trypanosomaC','babesia']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model=models.Announcement
        fields=['title','body']
class RequestForm(forms.ModelForm):
    class Meta:
        model=models.BloodRequest
        fields=['reason','unit','proof','proof2','proof3']
