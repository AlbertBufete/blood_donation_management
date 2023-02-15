from django.shortcuts import render,redirect,reverse
from . import forms,models
import xlwt
import xlrd
import os
from django.conf import settings as django_settings
from Utils import queryset_to_workbook
from datetime import datetime,time
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import auth
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
import logging
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#The mail addresses and password
sender_address = 'redcross.help.portal@gmail.com'
sender_pass = 'ljnanvxmokehqfjs'
def home_view(request):
    x=models.Stock.objects.all()
    if len(x)==0:
        blood1=models.Stock()
        blood1.bloodgroup="A+"
        blood1.save()

        blood2=models.Stock()
        blood2.bloodgroup="A-"
        blood2.save()

        blood3=models.Stock()
        blood3.bloodgroup="B+"
        blood3.save()

        blood4=models.Stock()
        blood4.bloodgroup="B-"
        blood4.save()

        blood5=models.Stock()
        blood5.bloodgroup="AB+"
        blood5.save()

        blood6=models.Stock()
        blood6.bloodgroup="AB-"
        blood6.save()

        blood7=models.Stock()
        blood7.bloodgroup="O+"
        blood7.save()

        blood8=models.Stock()
        blood8.bloodgroup="O-"
        blood8.save()

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    announcements = models.Announcement.objects.all().order_by('-id')[:5]
    make_request = False

    if 'make_request' in request.session:
        print("the make request " + str(request.session['make_request']))
        make_request = request.session['make_request']
        del request.session['make_request']
    return render(request,'blood/index.html',{"announcement":announcements,"make_request":make_request})
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
def upload_announcement(request):
    if request.method == 'POST':
        request_form = forms.AnnouncementForm(request.POST)
        if request_form.is_valid():
            print("redirec")
            announcement_request = request_form.save(commit=False)
            announcement_request.save()
            request.session['announcement_upload'] = True
            return HttpResponseRedirect('/admin-announcement')
        request.session['announcement_upload'] = False
        return HttpResponseRedirect('/admin-announcement')

    return render(request, 'blood/admin_announcement.html')

def delete_announcement(request,pk):
    announcement = models.Announcement.objects.get(id=pk)
    announcement.delete()
    request.session['announcement_delete'] = True
    return HttpResponseRedirect('/admin-announcement')
def update_announcement_view(request,pk):
    announcement = models.Announcement.objects.get(id=pk)
    announcement_form = forms.AnnouncementForm()
    mydict = {'announcement_form': announcement_form,'announcement':announcement}
    if request.method == 'POST':
        announcement_form = forms.AnnouncementForm(request.POST,instance=announcement)
        if announcement_form.is_valid():
            announcement_form.save()
            request.method = 'GET'
            request.session['announcement_save'] = True
            return HttpResponseRedirect('../admin-announcement')
        request.session['announcement_save'] = False
        return HttpResponseRedirect('admin-announcement')
    return render(request, 'blood/update_announcement.html', context=mydict)
def admin_announcement(request):
    announcement_save = False
    announcement_upload = False
    announcement_delete = False
    if 'announcement_save' in request.session:
        announcement_save = request.session['announcement_save']
        del request.session['announcement_save']
    if 'announcement_upload' in request.session:
        announcement_upload = request.session['announcement_upload']
        del request.session['announcement_upload']
    if 'announcement_delete' in request.session:
        announcement_delete = request.session['announcement_delete']
        del request.session['announcement_delete']
    announcements = models.Announcement.objects.all().order_by('-id')[:5]
    return render(request, 'blood/admin_announcement_list.html', {"announcements": announcements,'announcement_save':announcement_save,'announcement_upload':announcement_upload,'announcement_delete':announcement_delete})


def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if is_donor(request.user):
        return redirect('donor/donor-dashboard')

    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='adminlogin')
def admin_statistics_view(request):
    totalunit=models.Stock.objects.aggregate(Sum('unit'))
    totalA1 = 0
    totalA2 = 0
    totalB1 = 0
    totalB2 = 0
    totalO1 = 0
    totalO2 = 0
    totalAB1 = 0
    totalAB2 = 0

    totalDonors = dmodels.Donor.objects.all().count()
    consoleLog = ""
    for i in dmodels.Donor.objects.all():
        if i.get_blood_group == "A+":
            totalA1+=1
        if i.get_blood_group == "A-":
            totalA2+=1
        if i.get_blood_group == "B+":
            totalB1+=1
        if i.get_blood_group == "B-":
            totalB2+=1
        if i.get_blood_group == "O+":
            totalO1+=1
        if i.get_blood_group == "O-":
            totalO2+=1
        if i.get_blood_group == "AB+":
            totalAB1+=1
        if i.get_blood_group == "AB-":
            totalAB2+=1


    dict={
        'A1':models.Stock.objects.all().filter(bloodgroup="A+"),
        'A2':models.Stock.objects.all().filter(bloodgroup="A-"),
        'B1':models.Stock.objects.all().filter(bloodgroup="B+"),
        'B2':models.Stock.objects.all().filter(bloodgroup="B-"),
        'AB1':models.Stock.objects.all().filter(bloodgroup="AB+"),
        'AB2':models.Stock.objects.all().filter(bloodgroup="AB-"),
        'O1':models.Stock.objects.all().filter(bloodgroup="O+"),
        'O2':models.Stock.objects.all().filter(bloodgroup="O-"),
        'A1ratio': totalA1 / totalDonors * 100 if totalA1 else 0,
        'A2ratio': totalA2 / totalDonors * 100 if totalA2 else 0,
        'B1ratio': totalB1 / totalDonors * 100 if totalB1 else 0,
        'B2ratio': totalB2 /totalDonors * 100 if totalB2 else 0,
        'O1ratio': totalO1 / totalDonors * 100 if totalO1 else 0,
        'O2ratio': totalO2 / totalDonors * 100 if totalO2 else 0,
        'AB1ratio': totalAB1 / totalDonors * 100 if totalAB1 else 0,
        'AB2ratio': totalAB2 / totalDonors * 100 if totalAB2 else 0,

        'totaldonors':dmodels.Donor.objects.all().count(),
        'totalbloodunit':totalunit['unit__sum'],
        'totalrequest':models.BloodRequest.objects.all().count(),
        'totalapprovedrequest':models.BloodRequest.objects.all().filter(status='Approved').count(),
        'consoleLog': consoleLog
    }
    return render(request,'blood/admin_statistics.html',context=dict)
def admin_dashboard_view(request):
    totalunit=models.Stock.objects.aggregate(Sum('unit'))
    approvedBloodDonatesToday = len(dmodels.BloodDonate.objects.filter(date=datetime.today(),status="Approved"))
    pendingBloodDonatesToday = len(dmodels.BloodDonate.objects.filter(date=datetime.today(),status="Pending"))
    rejectedBloodDonatesToday = len(dmodels.BloodDonate.objects.filter(date=datetime.today(),status="Rejected"))
    approvedBloodRequestsToday = len(models.BloodRequest.objects.filter(date=datetime.today(), status="Approved"))
    pendingBloodRequestsToday = len(models.BloodRequest.objects.filter(date=datetime.today(), status="Pending"))
    rejectedBloodRequestsToday = len(models.BloodRequest.objects.filter(date=datetime.today(), status="Rejected"))
    columns = [
        "donor"
    ]
    dailyReport = xlwt.Workbook()
    reportFileName = datetime.now().strftime("%Y%m%d") + ".xls"
    dailyReportSheet = dailyReport.add_sheet("Daily Report",cell_overwrite_ok=True)
    HEADER_SYTLE = xlwt.easyxf('font:bold on')
    dailyReportSheet.col(0).width = 7000
    dailyReportSheet.col(1).width = 7000
    dailyReportSheet.col(2).width = 7500
    dailyReportSheet.col(3).width = 7000
    dailyReportSheet.col(4).width = 7000
    dailyReportSheet.col(5).width = 7000
    #dailyReportSheet.write(0,0,"Approved Blood Donates",HEADER_SYTLE)
    dailyReportSheet.write(0,0,"Blood Requests",HEADER_SYTLE)
    dailyReportSheet.write(1,0,"Date",HEADER_SYTLE)
    dailyReportSheet.write(1,1,"Name",HEADER_SYTLE)
    dailyReportSheet.write(1,2,"Reason",HEADER_SYTLE)
    dailyReportSheet.write(1,3,"Type of Request Blood",HEADER_SYTLE)
    dailyReportSheet.write(1,4,"Unit",HEADER_SYTLE)
    dailyReportSheet.write(1,5,"Status",HEADER_SYTLE)
    blood_request_line = 2
    for blood_request in models.BloodRequest.objects.filter(Q(date=datetime.today()) & (Q(status="Rejected") | Q(status="Approved")) ):
        dailyReportSheet.write(blood_request_line, 0, blood_request.date.strftime("%m/%d/%y"))
        dailyReportSheet.write(blood_request_line, 1, blood_request.patient_name)
        dailyReportSheet.write(blood_request_line, 2, blood_request.reason)
        dailyReportSheet.write(blood_request_line, 3, blood_request.bloodgroup)
        dailyReportSheet.write(blood_request_line, 4, str(blood_request.unit) + "ml")
        dailyReportSheet.write(blood_request_line, 5, blood_request.status)
        blood_request_line+=1
    dailyReportSheet.write(blood_request_line, 0, "Blood Requests", HEADER_SYTLE)
    blood_request_line+=1
    dailyReportSheet.write(blood_request_line, 0, "Date", HEADER_SYTLE)
    dailyReportSheet.write(blood_request_line, 1, "Name", HEADER_SYTLE)
    dailyReportSheet.write(blood_request_line, 2, "Blood Type", HEADER_SYTLE)
    dailyReportSheet.write(blood_request_line, 3, "Unit", HEADER_SYTLE)
    dailyReportSheet.write(blood_request_line, 4, "Status", HEADER_SYTLE)
    blood_request_line+=1
    for blood_donate in dmodels.BloodDonate.objects.filter(Q(date=datetime.today()) & (Q(status="Rejected") | Q(status="Approved")) ):
        dailyReportSheet.write(blood_request_line, 0, blood_donate.date.strftime("%m/%d/%y"))
        dailyReportSheet.write(blood_request_line, 1, blood_donate.donor.user.first_name + " " + blood_donate.donor.user.first_name)
        dailyReportSheet.write(blood_request_line, 2, blood_donate.bloodgroup)
        dailyReportSheet.write(blood_request_line, 3, str(blood_donate.unit) + "ml")
        dailyReportSheet.write(blood_request_line, 4, blood_donate.status)
        blood_request_line+=1
    reportPath = "./static/reports/" + reportFileName
    dailyReport.save(reportPath)

    dict={
        'reportFileName':reportFileName,
        'approvedBloodDonatesToday':approvedBloodDonatesToday,
        'pendingBloodDonatesToday':pendingBloodDonatesToday,
        'rejectedBloodDonatesToday':rejectedBloodDonatesToday,
        'approvedBloodRequestsToday': approvedBloodRequestsToday,
        'pendingBloodRequestsToday': pendingBloodRequestsToday,
        'rejectedBloodRequestsToday': rejectedBloodRequestsToday,
        'A1':models.Stock.objects.get(bloodgroup="A+"),
        'A2':models.Stock.objects.get(bloodgroup="A-"),
        'B1':models.Stock.objects.get(bloodgroup="B+"),
        'B2':models.Stock.objects.get(bloodgroup="B-"),
        'AB1':models.Stock.objects.get(bloodgroup="AB+"),
        'AB2':models.Stock.objects.get(bloodgroup="AB-"),
        'O1':models.Stock.objects.get(bloodgroup="O+"),
        'O2':models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors':dmodels.Donor.objects.all().count(),
        'totalbloodunit':totalunit['unit__sum'],
        'totalrequest':models.BloodRequest.objects.all().count(),
        'totalapprovedrequest':models.BloodRequest.objects.all().filter(status='Approved').count()
    }
    return render(request,'blood/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_blood_view(request):
    dict={
        'bloodForm':forms.BloodForm(),
        'A1':models.Stock.objects.get(bloodgroup="A+"),
        'A2':models.Stock.objects.get(bloodgroup="A-"),
        'B1':models.Stock.objects.get(bloodgroup="B+"),
        'B2':models.Stock.objects.get(bloodgroup="B-"),
        'AB1':models.Stock.objects.get(bloodgroup="AB+"),
        'AB2':models.Stock.objects.get(bloodgroup="AB-"),
        'O1':models.Stock.objects.get(bloodgroup="O+"),
        'O2':models.Stock.objects.get(bloodgroup="O-"),
    }
    if request.method=='POST':
        bloodForm=forms.BloodForm(request.POST)
        if bloodForm.is_valid() :
            bloodgroup=bloodForm.cleaned_data['bloodgroup']
            stock=models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit=bloodForm.cleaned_data['unit']
            stock.save()
        return HttpResponseRedirect('admin-blood')
    return render(request,'blood/admin_blood.html',context=dict)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    donors=dmodels.Donor.objects.all()
    return render(request,'blood/admin_donor.html',{'donors':donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(request.FILES,instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect('/admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    patients=pmodels.Patient.objects.all()
    return render(request,'blood/admin_patient.html',{'patients':patients})


@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    patientForm=pforms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    bloodRequests=models.BloodRequest.objects.all().filter(status='Pending')
    for bloodRequest in bloodRequests:
        if(bloodRequest.request_by_patient_id != None):
            patient = pmodels.Patient.objects.get(id=bloodRequest.request_by_patient_id)
            bloodRequest.mobile = patient.mobile
        else:
            donor = dmodels.Donor.objects.get(id=bloodRequest.request_by_donor_id)
            bloodRequest.mobile = donor.mobile

    app_url = settings.APP_URL
    return render(request,'blood/admin_request.html',context={'app_url':app_url,'requests':bloodRequests})

@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests=models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request,'blood/admin_request_history.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_donation_view(request):
    blood_test_upload = False
    donations=dmodels.BloodDonate.objects.all()
    if 'blood_test_upload' in request.session:
        blood_test_upload = request.session['blood_test_upload']
        del request.session['blood_test_upload']
    return render(request,'blood/admin_donation.html',context={'donations':donations,'blood_test_upload':blood_test_upload})

def sendEmail(receiver_address,subject,mail_content):
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')
@login_required(login_url='adminlogin')
def update_approve_status_view(request,pk,units):
    # Setup the MIME
    req=models.BloodRequest.objects.get(id=pk)
    receiver_address = ""
    if(req.request_by_patient != None):
        receiver_address = req.request_by_patient.user.email
    else:
        receiver_address = req.request_by_donor.user.email
    message=None
    bloodgroup=req.bloodgroup
    unit=units
    stock=models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit=stock.unit-unit
        stock.save()
        req.unit_approved = units
        req.status="Approved"
        sendEmail(receiver_address, "Blood request approved","We are able to donate " + str(units) + " units")

    else:
        message="Stock Doest Not Have Enough Blood To Approve This Request, Only "+str(stock.unit)+" Unit Available"
    req.save()

    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

@login_required(login_url='adminlogin')
def update_reject_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    req.status="Rejected"
    req.save()
    receiver_address = ""
    if (req.request_by_patient != None):
        receiver_address = req.request_by_patient.user.email
        print("theemail" + receiver_address)

    else:
        receiver_address = req.request_by_donor.user.email
        print("theemail" + receiver_address)

    print("theemail" + receiver_address)
    sendEmail(receiver_address, "Blood request rejected", "We are not able to approve your blood request")
    return HttpResponseRedirect('/admin-request')

@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    stock=models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit=100
    print("the units " + str(stock.unit))
    stock.save()

    donation.status='Approved'
    donation.save()
    return HttpResponseRedirect('/admin-donation')
def blood_test(request,pk):
    blood_test_form = forms.BloodTestForm()
    bloodTest = models.BloodTest.objects.filter(bloodDonate_id=pk)
    if request.method == 'POST':
        request_form = forms.BloodTestForm(request.POST)
        if(len(bloodTest) > 0):
            bloodTest = models.BloodTest.objects.get(bloodDonate_id=pk)
            request_form = forms.BloodTestForm(request.POST,instance=bloodTest)
        if request_form.is_valid():
            announcement_request = request_form.save(commit=False)

            announcement_request.bloodDonate_id = pk
            approve = True
            for var,val in announcement_request.__dict__.items():
                if(type(val) == bool):
                    if(val):
                        approve = False
            if approve:
                donation = dmodels.BloodDonate.objects.get(id=pk)
                donation_blood_group = donation.bloodgroup
                donation_blood_unit = donation.unit
                stock = models.Stock.objects.get(bloodgroup=donation_blood_group)
                print("stock unit " + str(stock.unit) + " donation unit " + str(donation_blood_unit))
                stock.unit = stock.unit + donation_blood_unit
                stock.save()
                donation.status = 'Approved'
                donation.save()
            else:
                donation = dmodels.BloodDonate.objects.get(id=pk)
                donation.status = 'Rejected'
                donation.save()
            announcement_request.save()
            request.session['blood_test_upload'] = True
            return HttpResponseRedirect('/admin-donation')
        request.session['blood_test_upload'] = False
        return HttpResponseRedirect('/admin-donation')
    bloodDonation = dmodels.BloodDonate.objects.get(id=pk)
    survey_answers = []
    for k,v in bloodDonation.survey_answer.items():
        if(k != "csrfmiddlewaretoken"):
            survey_answers.append({"key": k, "value": v})
    return render(request, 'blood/admin_blood_test.html',context={'blood_test_form':blood_test_form,'survey_answers':survey_answers})

@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.status='Rejected'
    donation.save()
    return HttpResponseRedirect('/admin-donation')
