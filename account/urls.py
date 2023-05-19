"""account URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from Register.views import register,login_view
from Room.views import list_Room,date_selection,home,all_events1, Reserve,refresh,finish_room,sumbit_room,Email_approve,send_email_applicant,send_email_vechicle,s_email,print_reservation
from pdf.views import render_pdf_view
from django.contrib.auth.views import LoginView, LogoutView
from telegram_message.views import send_telegram_message,telegram_sent

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', login_view,name='login'),
    path('logout/', LogoutView.as_view() ,name='logout'),
    path('rooms/', list_Room, name='room_list'),
    path('rooms/reservation/<str:name>', Reserve, name="myreservation"),
    path('rooms/reservation_finish', finish_room, name='finish_room'),
    path('rooms/reservation_submit', sumbit_room, name='submit_room'),
    path('refresh/', refresh, name='refresh'),
    path('date_selection/', date_selection, name='date_selection'),
    path('all_events1/', all_events1, name='all_events1'),
    path('email_approve', send_email_applicant, name= 'email_approve'),
    path('view_pdf/', render_pdf_view, name='view_pdf'),
    path('send_telegram_message/', send_telegram_message, name='send_telegram_message'),
    path('send_message/', telegram_sent, name='send_message'),
]
