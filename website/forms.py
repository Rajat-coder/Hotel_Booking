from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django import forms
from django.core.mail import EmailMessage
from django.forms import ModelForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from website.models import Booking,Profile
from website.token_generator import account_activation_token


class signupform(forms.ModelForm):
    username=forms.CharField(label="Username",max_length=100)
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    email = forms.CharField(label="Email", max_length=100)
    password1=forms.CharField(label="Password",widget=forms.PasswordInput)
    password2=forms.CharField(label="Confirm password",widget=forms.PasswordInput)


    class Meta:
        model=User
        fields=('username','email','first_name','last_name',)

    def clean_password2(self):
        pass1=self.cleaned_data.get("password1")
        pass2 =self.cleaned_data.get("password2")
        if pass1 and pass2 and pass1 != pass2:
            raise forms.ValidationError("Password does not match or not enterted properly")
        return pass2

    def save(self, commit=True):
        userobj=super(signupform,self).save(commit=False)
        userobj.set_password(self.cleaned_data["password2"])
        userobj.is_active = False
        if commit:
            userobj.save()
            current_site = "http://bestjalandharhotel.herokuapp.com/"
            email_subject = 'Activate Your Account'
            message = render_to_string('activate_account.html', {
                'user': userobj,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(userobj.pk)).decode(),
                'token': account_activation_token.make_token(userobj),
            })
            to_email = self.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
        return userobj

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('birth_date', 'phone')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','first_name','last_name',)

class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        user1 = self.cleaned_data.get("username")
        pass1 = self.cleaned_data.get("password")

        user_obj = authenticate(username=user1, password=pass1)

        if not user_obj:
            raise forms.ValidationError("Wrong username / password or not activated by email")

        return super(LoginForm, self).clean(*args, **kwargs)

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        exclude = ('userid', 'roomcategoryid','roomdetailid','amount')


class ContactForm(forms.Form):
 name = forms.CharField(label="Name")
 emailid = forms.CharField(label="Email ID")
 message = forms.CharField(label="Message", widget=forms.Textarea)