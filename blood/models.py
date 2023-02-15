from django.db import models
from patient import models as pmodels
from donor import models as dmodels
class Stock(models.Model):
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.bloodgroup
class BloodTest(models.Model):
    bloodDonate =models.ForeignKey(dmodels.BloodDonate,on_delete=models.CASCADE)
    hepaB = models.BooleanField()
    hepaC = models.BooleanField()
    hiv1 = models.BooleanField()
    hiv2 = models.BooleanField()
    htlv1 = models.BooleanField()
    htlv2 = models.BooleanField()
    syphilis = models.BooleanField()
    westNile = models.BooleanField()
    trypanosomaC = models.BooleanField()
    babesia = models.BooleanField()


class Announcement(models.Model):
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=1000)
    date=models.DateField(auto_now=True)
class BloodRequest(models.Model):
    request_by_patient=models.ForeignKey(pmodels.Patient,null=True,on_delete=models.CASCADE)
    proof= models.ImageField(upload_to='proof/',null=True,blank=True)
    proof2= models.ImageField(upload_to='proof/',null=True,blank=True)
    proof3= models.ImageField(upload_to='proof/',null=True,blank=True)

    request_by_donor=models.ForeignKey(dmodels.Donor,null=True,on_delete=models.CASCADE)
    patient_name=models.CharField(max_length=30)
    patient_age=models.PositiveIntegerField()
    reason=models.CharField(max_length=500)
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    unit_approved=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20,default="Pending")
    date=models.DateField(auto_now=True)
    def __str__(self):
        return self.bloodgroup

