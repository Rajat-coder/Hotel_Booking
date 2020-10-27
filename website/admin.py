from django.contrib import admin

# Register your models here.
from website.models import Roomcategory, Roomcategorydetails, Profile, Booking, register_table


@admin.register(Roomcategory)
class RoomcategoryAdmin(admin.ModelAdmin):
    list_display = ['id','categoryname','services','roomsize','beds','capcity','bedtype','roomavailable','Image']

@admin.register(Roomcategorydetails)
class RoomdetailsAdmin(admin.ModelAdmin):
    list_display = ['roomcategoryid','roomoption','roomprice']


@admin.register(Booking)
class BookingdetailsAdmin(admin.ModelAdmin):
    list_display = ['userid','id','checkindate','checkoutdate','amount','totalpersons','guestname','gender','roomcategoryid','roomdetailid']

@admin.register(Profile)
class RoomdetailsAdmin(admin.ModelAdmin):
    list_display = ['user','birth_date','phone']

@admin.register(register_table)
class RoomdetailsAdmin(admin.ModelAdmin):
    list_display = ['user','profile_pic']
