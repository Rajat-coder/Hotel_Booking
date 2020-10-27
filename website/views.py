from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import logout
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
# Create your views here.
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView

from .forms import signupform, LoginForm, BookingForm, UserForm, ProfileForm, ContactForm
from .models import Roomcategory, Roomcategorydetails, Booking, register_table
from .token_generator import account_activation_token


def start(request):

    return render(request, "startbase.html")

def index(request):
    context = {}
    check = register_table.objects.filter(user__id=request.user.id)
    if len(check) > 0:
        data = register_table.objects.get(user__id=request.user.id)
        context["data"] = data

        if "image" in request.FILES:
            img = request.FILES["image"]
            data.profile_pic = img
            data.save()

    return render(request, "index.html",context)

def final(request):

    return render(request, "final.html")

class mysignup(SuccessMessageMixin,CreateView):
    form_class = signupform
    template_name = 'signup.html'
    success_message = "Your account has been created successfully .Please activiate your account with your email id."
    success_url = reverse_lazy('signpage')

    def dispatch(self, *args, **kwargs):
        return super(mysignup,self).dispatch(*args, **kwargs)

@login_required
def mybooking(request, detailid):
    roomcategoryobj = Roomcategory.objects.get(id=request.session["catid"])
    roomcategorydetailsobj = Roomcategorydetails.objects.get(id=detailid)
    image = roomcategoryobj.Image
    catname = roomcategoryobj.categoryname
    roomoptions = roomcategorydetailsobj.roomoption
    price = roomcategorydetailsobj.roomprice
    details = {"image":image, "catname" :catname, "roomoptions":roomoptions, "price":price}
    formobj = BookingForm(request.POST or None)
    if request.method == "POST":
        if formobj.is_valid():
            data = formobj.save(commit=False)
            categoryid = request.session["catid"]

            case_1 = Booking.objects.filter(roomcategoryid=categoryid, checkindate__lte=data.checkindate,
                                            checkoutdate__gte=data.checkindate).exists()

            # case 2: a room is booked before the requested check_out date and check_out date is after requested
            # check_out date
            case_2 = Booking.objects.filter(roomcategoryid=categoryid, checkindate__lte=data.checkoutdate,
                                            checkoutdate__gte=data.checkoutdate).exists()

            case_3 = Booking.objects.filter(roomcategoryid=categoryid, checkindate__gte=data.checkindate,
                                            checkoutdate__lte=data.checkoutdate).exists()

            # if either of these is true, abort and render the error
            if case_1 or case_2 or case_3:
                count1 = Booking.objects.filter(roomcategoryid=categoryid, checkindate__lte=data.checkindate,
                                            checkoutdate__gte=data.checkindate).count()
                count2 = Booking.objects.filter(roomcategoryid=categoryid, checkindate__lte=data.checkoutdate,
                                            checkoutdate__gte=data.checkoutdate).count()
                count3 = Booking.objects.filter(roomcategoryid=categoryid, checkindate__gte=data.checkindate,
                                            checkoutdate__lte=data.checkoutdate).count()

                totalcount = 0
                if count1 > 0:
                    totalcount += count1
                elif count2 > 0:
                    totalcount += count2
                elif count3 > 0:
                    totalcount += count3

                if totalcount == roomcategoryobj.roomavailable:
                    messages.error(request, 'Selected Dates are not available')
                    return render(request, "booking.html", {"form": formobj})

            data.userid = User(id=request.session["userid"])
            data.roomcategoryid = roomcategoryobj
            data.roomdetailid = Roomcategorydetails(id=detailid)
            checkindate = data.checkindate
            checkoutdate = data.checkoutdate
            daysinfo = checkoutdate - checkindate

            data.amount = roomcategorydetailsobj.roomprice
            totalbill = data.amount * daysinfo.days
            data.save()
            bookingid = data.id
            context = {"bookingid": bookingid, "total": totalbill}
            return render(request, "final.html", context)
            # messages.success(request,
            #                  'Your request for booking has been successful. Your booking id is ' + str(bookingid)
            #                  + ' Your total bill amount is ' + str(totalbill)
            #                  + '. Pay on 8054463693 on Google Pay / Paytm / UPI')
        else:
            formobj = BookingForm(request.POST)
    return render(request, "booking.html", {"form": formobj, "roomdetails":details})



def mylogin(request):
    formobj = LoginForm(request.POST or None)
    redirect_to=request.POST.get('next')
    if formobj.is_valid():
        username = formobj.cleaned_data.get("username")
        userobj = User.objects.get(username__iexact=username)
        login(request, userobj)
        request.session["userid"] = userobj.id
        request.session["myusername"] = userobj.username
        request.session["myuseremail"] = userobj.email
        if redirect_to:
            return redirect(redirect_to)
        else:
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "login.html", {"form": formobj})


def about(request):
    url = "http://api.openweathermap.org/data/2.5/weather?q=Jalandhar&appid=d6bf2e65d36627e9c4da4ace08b789e7&units=metric"
    json_data = requests.get(url).json()
    temperature = json_data["main"]["temp"]
    temperature2 = json_data["name"]
    temperature3 = json_data["weather"][0]["main"]
    tempdata = {"temp": temperature, "temp2": temperature2, "temp3": temperature3}

    return render(request, "aboutus.html",tempdata)


def showcontactus(request):
    myform = ContactForm(request.POST or None)
    if myform.is_valid():
        data = request.POST
        name = data.get("name", "0")
        emailid = data.get("emailid", "0")
        message = data.get("message", "0")
        result = send_mail("Message from Website", "Name : " + name + "\nEmailid : " + emailid + "\nMessage : " + message,
            "royalcontinentalhotell@gmail.com", ["royalcontinentalhotell@gmail.com"], fail_silently=False)
        return render(request, "contactus.html", {"form": myform, "status": result})
    else:
        return render(request, "contactus.html", {"form": myform})




def myaccount(request):
    context = {}
    check = register_table.objects.filter(user__id=request.user.id)
    if len(check) > 0:
        data = register_table.objects.get(user__id=request.user.id)
        context["data"] = data

        if "image" in request.FILES:
            img = request.FILES["image"]
            data.profile_pic = img
            data.save()

    return render(request, "myaccount.html", context)

def room(request):
    obj = Roomcategory.objects.all()  # Getting all the records from database
    context = {"roomdetails": obj}
    return render(request, "rooms.html",context)

def RoomDetails(request, catid):
    obj = Roomcategorydetails.objects.select_related('roomcategoryid').filter(roomcategoryid=catid)
    obj2 = Roomcategorydetails.objects.select_related('roomcategoryid').filter(roomcategoryid=catid).first()
    request.session["catid"]=catid
    context = {"roomcategorydetails": obj, "roomcatdetails": obj2}
    return render(request, "roomdetails.html", context)

@login_required
def changepass(request):
    if request.method == 'POST':
        data = request.POST
        oldpassword = data.get("oldpassword", "1")
        password1 = data.get("password1", "0")
        password2 = data.get("password2", "0")
        if password1 == password2:
            myusername = request.session["myusername"]
            userobj = authenticate(username=myusername, password=oldpassword)
            if userobj:
                userobj.set_password(password1)
                userobj.save()
                logout(request)
                formobj = LoginForm(None)
                context = {"form": formobj, "loginmessage": "done"}
                return render(request, "login.html", context)
            else:
                context = {"mymessage": "Wrong old password"}
        else:
            context = {"mymessage": "New Passwords does not match"}
        return render(request, "changepassword.html", context)
    else:
        return render(request, "changepassword.html")

def mysignout(request):
    if request.session.has_key("myusername"):
        del request.session["myusername"]
        logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
@transaction.atomic
def updateuser(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')

        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'updateprofile.html', {'user_form': user_form, 'profile_form': profile_form})


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


def bad_request(request):
    context = {}

    return render(request, '400.html', context, status=400)


def permission_denied(request):
    context = {}

    return render(request, '403.html', context, status=403)


def page_not_found(request):
    context = {}

    return render(request, '404.html', context, status=404)


def server_error(request):
    context = {}

    return render(request, '500.html', context, status=500)
