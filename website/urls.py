from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path
from django.views.static import serve

from gtb import settings
from .import views

urlpatterns = [

    url('^$', views.start),
    path('Best-Hotel-In-Dubai', views.index, name="index"),
    path('About_Royal_Continental_hotel', views.about, name="aboutpage"),
    path('Best_Room_In_Dubai', views.room, name="roompage"),
    path('signup_Royal_Continental_hotel', views.mysignup.as_view(), name="signpage"),
    path('signout', views.mysignout, name='signout'),
    path('My_Account', views.myaccount, name='myaccount'),
    path('Payment_Page', views.final, name='final'),
    path('contact', views.showcontactus, name='contactus'),
    path('update-profile', views.updateuser, name='updateprofile'),
    path('booking_Royal_Continental_hotel/<int:detailid>', views.mybooking, name="booking"),
    path('login_Royal_Continental_hotel', views.mylogin, name="loginpage"),
    path('Change-Form', views.changepass, name="changepassword"),
    path('Room_Details_Royal_Continental_hotel/<int:catid>', views.RoomDetails, name="myroomdetails"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                      views.activate_account, name='activate'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
   handler400 = 'common.views.bad_request'
   handler403 = 'common.views.permission_denied'
   handler404 = 'common.views.page_not_found'
   handler500 = 'common.views.server_error'