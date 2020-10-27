from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Roomcategory(models.Model):
    categoryname=models.CharField(max_length=30)
    services = RichTextField()
    roomsize=models.CharField(max_length=30)
    beds = models.CharField(max_length=30)
    capcity = models.CharField(max_length=30)
    bedtype = models.CharField(max_length=30)
    roomavailable=models.IntegerField(default=0)
    Image = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank='True', null='True')

    def __str__(self):
        return self.categoryname

class Roomcategorydetails(models.Model):
    roomcategoryid=models.ForeignKey(Roomcategory,on_delete=models.CASCADE)
    roomoption=models.CharField(max_length=200)
    roomprice=models.IntegerField()

    def __str__(self):
        return str(self.roomoption
                   )

class Booking(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    roomcategoryid = models.ForeignKey(Roomcategory, on_delete=models.CASCADE)
    roomdetailid = models.ForeignKey(Roomcategorydetails, on_delete=models.CASCADE)
    checkindate = models.DateField()
    checkoutdate = models.DateField()
    amount = models.IntegerField()
    totalpersons = models.IntegerField()
    guestname = models.CharField(max_length=70)
    gender_choices = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=6, choices=gender_choices)

    def __str__(self):
        return str(self.userid)



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class register_table(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_pic = models.ImageField(upload_to="profiles/%Y/%m/%d", null=True, blank=True,
                                    default='/staticfiles/images/user.png')

    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = register_table.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)