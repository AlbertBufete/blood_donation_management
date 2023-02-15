from django.shortcuts import render
from . import forms,models
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect

from blood import forms as bforms
from blood import models as bmodels
def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST,request.FILES)
        print(request_form.is_valid())
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.patient_name = donor.user.first_name + " " + donor.user.last_name
            blood_request.patient_age = donor.age
            blood_request.bloodgroup=donor.bloodgroup
            blood_request.request_by_donor=donor
            blood_request.save()
            return HttpResponseRedirect('request-history')
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
        'A1': bmodels.Stock.objects.get(bloodgroup="A+"),
        'A2': bmodels.Stock.objects.get(bloodgroup="A-"),
        'B1': bmodels.Stock.objects.get(bloodgroup="B+"),
        'B2': bmodels.Stock.objects.get(bloodgroup="B-"),
        'AB1': bmodels.Stock.objects.get(bloodgroup="AB+"),
        'AB2': bmodels.Stock.objects.get(bloodgroup="AB-"),
        'O1': bmodels.Stock.objects.get(bloodgroup="O+"),
        'O2': bmodels.Stock.objects.get(bloodgroup="O-"),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)


def donate_blood_view(request):
    donation_form=forms.DonationForm()
    if not("question1" in request.POST) and not("survey_answers" in request.session):
        return HttpResponseRedirect('donate-blood-survey')
    elif "question1" in request.POST:
        request.session['survey_answers'] = request.POST


    if request.method=='POST' and not("question1" in request.POST) and "survey_answers" in request.session:
        donation_form = forms.DonationForm(request.POST)
        print(donation_form.is_valid())
        if donation_form.is_valid():
            blood_donate=donation_form.save(commit=False)
            blood_donate.survey_answer = request.session['survey_answers']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_donate.bloodgroup= donor.bloodgroup
            blood_donate.donor=donor
            blood_donate.age = donor.age
            blood_donate.save()
            del request.session['survey_answers']
            return HttpResponseRedirect('donation-history')
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form})
def donate_blood_survey_view(request):
    return render(request,'donor/donate_blood_survey.html')

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})


def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':blood_request})
def donor_certificates_view(request):
    logs = ""
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations = models.BloodDonate.objects.all().filter(donor=donor)
    for donation in donations:
        if donation.status == "Approved":
            image = Image.open("static/image/certificate_template.png")
            draw = ImageDraw.Draw(image)
            idFont = ImageFont.truetype("static/fonts/jackit.ttf", 30)
            nameFont = ImageFont.truetype("static/fonts/jackit.ttf", 100)
            dateFont = ImageFont.truetype("static/fonts/jackit.ttf", 40)
            width = image.width
            height = image.height
            # generation of certificate
            # donor name
            donor_name = str(donation.donor.get_name())
            draw.text((width * .19, height * .48), donor_name.upper(), (0, 0, 0), nameFont)
            # certificate id
            certNumber = donation.id
            draw.text((width * .01, height * .97), "Certificate No. " + str(certNumber), (255, 0, 0), idFont)
            # date
            certDate = donation.date
            draw.text((width * .26, height * .66), certDate.strftime("%b %d %Y"), (0, 0, 0), dateFont)
            # blood type
            bloodType = donation.bloodgroup
            draw.text((width * .575, height * .66), bloodType, (0, 0, 0), dateFont)
            # units
            units = donation.unit
            draw.text((width * .75, height * .66), str(units), (0, 0, 0), dateFont)
            filename = donor_name + "_" + str(certNumber)
            filename = filename.replace(" ","_")
            imagedir = "static/image/" + filename + ".png"
            donation.certificate_location =  "image/"+ filename + ".png"
            image.save(imagedir)
    return render(request,'donor/donor_certificates.html',{'donations':donations,"logs":logs})
def donor_certificate_download(request,id):
    image = Image.open("static/image/certificate_template.png")
    draw = ImageDraw.Draw(image)
    idFont = ImageFont.truetype("static/fonts/jackit.ttf", 30)
    nameFont = ImageFont.truetype("static/fonts/jackit.ttf", 100)
    dateFont = ImageFont.truetype("static/fonts/jackit.ttf", 40)
    width = image.width
    height = image.height
    #generation of certificate
    donation= models.BloodDonate.objects.get(id=id)
    # donor name
    donor_name = str(donation.donor.get_name())
    draw.text((width * .19, height * .48), donor_name.upper(), (0, 0, 0), nameFont)
    # certificate id
    certNumber = donation.id
    draw.text((width * .01, height * .97), "Certificate No. " + str(certNumber), (255, 0, 0), idFont)
    # date
    certDate = donation.date
    draw.text((width * .26, height * .66), certDate.strftime("%b %d %Y"), (0, 0, 0), dateFont)
    # blood type
    bloodType = donation.bloodgroup
    draw.text((width * .575, height * .66), bloodType, (0, 0, 0), dateFont)
    # units
    units = donation.unit
    draw.text((width * .75, height * .66), str(units), (0, 0, 0), dateFont)
    filename = donor_name + "_" + certNumber
    imagedir = "static/image/" + filename
    image.save(imagedir)
    #return redirect("donor-certificates")
