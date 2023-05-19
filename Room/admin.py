from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import MyRoom,Reservation
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from reportlab.pdfgen import canvas
from django.http import HttpResponse

import datetime
from django.shortcuts import render,redirect
import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from .views import link_callback, send_email_vechicle, send_email_applicant
from django.utils.html import format_html
from django.forms import ModelChoiceField
from django import forms
from Driver.models import Driver



# Register your models here.

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].queryset = MyRoom.objects.all()
        self.fields['name'].label_from_instance = lambda obj: obj.name
        self.fields['driver'].queryset = Driver.objects.all()
        self.fields['driver'].label_from_instance = lambda obj: obj.full_name
        
class ReservationAdmin(admin.ModelAdmin):

    list_display = ('user', 'date','Facilities' , 'start_date', 'end_date', 'status','email_send', 'print_pdf','file', 'Disemak')
    actions = ['pdf_action']
        
    def Disemak(self, obj):
        if obj.status == Reservation.REQUESTED:
            return format_html('<span style="color: red;">&#10008;</span>')  # Cross symbol
        else:
            return format_html('<span style="color: green;">&#10004;</span>')  # Tick symbol
    
    def date(self,obj):
        return obj.reserved
        
    date.short_description = 'Tarikh pemohonan'
    def Facilities(self,obj):
        return obj.name.name


    def print_pdf(self, obj):
        url = reverse('admin:reservation_print_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}">Print PDF</a>', url)

    def email_send(self, obj):
        url = reverse('admin:reservation_email_send', args=[obj.pk])
        return format_html('<a class="button" href="{}">Send Email</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('print_pdf/<int:pk>/', self.print_pdf_view, name='reservation_print_pdf'),
            path('send_email/<int:pk>/', self.email_send_view, name='reservation_email_send')
        ]
        return my_urls + urls
    def email_send_view(self, request, pk):
        reservation = Reservation.objects.get(pk=pk)
        email = reservation.user.email
        driver_email= reservation.driver.email
        file = reservation.file
        if reservation.status == 1:
            if reservation.name.category == 1:
                return send_email_vechicle(request,email,driver_email,file)
        return send_email_applicant(request,email,file)
    
    def print_pdf_view(self, request, pk):
        reservation = Reservation.objects.get(pk=pk)
        if reservation.status == 1:
            template_path = 'Status Tempahan Kenderaan Lulus.html'
        elif reservation.status == 2:
            template_path = 'Status Tempahan Kenderaan Gagal.html'
        else:
            messages.error(request, "Tempahan belum disemak.")
            return redirect ('/admin/Room/reservation')
        context = {
            'id' : str(reservation.pk),
            'facility': str(reservation.name.name),
            'reason' : str(reservation.reason),
            'participant' : reservation.participant,
            'destination' : reservation.destination,
            'Name' : str(reservation.user),
            'start_date' : reservation.start_date.date,
            'start_time' : reservation.start_date.time,
            'end_date' : reservation.end_date.date,
            'end_time' : reservation.end_date.time
            }
        template = get_template(template_path)
        html = template.render(context)
                
        # Generate a unique file name for the PDF file
        file_num = 1
        file_ext= '.pdf'
        filename = f"{reservation.user.full_name} - {reservation.name.name}"
        while True:
            if os.path.exists(os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemohon', filename + " " + str(file_num)+ " " + file_ext)):
                file_num +=1
            else:
                break
        
        filename = filename + " " + str(file_num) + " " + file_ext
        reservation.file = str(filename)
        reservation.save()
        # Set the file path for the PDF file
        file_path = os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemohon', filename)

        # Generate the PDF and write it to the file
        with open(file_path, 'wb') as file:
            pisa_status = pisa.CreatePDF(html, dest=file, link_callback=link_callback)
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')

        # Send a response to the client to confirm that the PDF has been saved
        response = HttpResponse('PDF file saved to ' + file_path)
        if reservation.status == 1:
            if reservation.name.category == 1:
                template_path = 'Notis Pemandu.html'
                context = {
                    'driver': str(reservation.driver.full_name),
                    'id' : str(reservation.pk),
                    'facility': str(reservation.name.name),
                    'reason' : str(reservation.reason),
                    'participant' : reservation.participant,
                    'destination' : reservation.destination,
                    'Name' : str(reservation.user),
                    'start_date' : reservation.start_date.date,
                    'start_time' : reservation.start_date.time,
                    'end_date' : reservation.end_date.date,
                    'end_time' : reservation.end_date.time
                    }
                template = get_template(template_path)
                html = template.render(context)
                        
                # Generate a unique file name for the PDF file
                # Set the file path for the PDF file
                file_path = os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemandu', filename)

                # Generate the PDF and write it to the file
                with open(file_path, 'wb') as file:
                    pisa_status = pisa.CreatePDF(html, dest=file, link_callback=link_callback)
                    if pisa_status.err:
                        return HttpResponse('We had some errors <pre>' + html + '</pre>')

                # Send a response to the client to confirm that the PDF has been saved
                response = HttpResponse('PDF file saved to ' + file_path)
        return redirect('/admin/Room/reservation')
    
    def pdf_action(self, request, queryset):
        for reservation in queryset:
            template_path = 'Borang mohon kenderaan bp.html'
            context = {
                'reason': str(reservation.reason),
                'participant': reservation.participant,
                'destination': reservation.destination,
                'Name': str(reservation.user.full_name),
                'start_date': reservation.start_date.date,
                'start_time': reservation.start_date.time,
                'end_date': reservation.end_date.date,
                'end_time': reservation.end_date.time
            }
            template = get_template(template_path)
            html = template.render(context)

            # Generate a unique file name for the PDF file
            file_num = 1
            file_ext = '.pdf'
            filename = f"{reservation.user.full_name} - {reservation.name.name}"
            while True:
                if os.path.exists(os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemohon',
                                               filename + " " + str(file_num) + " " + file_ext)):
                    file_num += 1
                else:
                    break

            filename = filename + " " + str(file_num) + " " + file_ext

            # Set the file path for the PDF file
            file_path = os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemohon', filename)

            # Generate the PDF and write it to the file
            with open(file_path, 'wb') as file:
                pisa_status = pisa.CreatePDF(html, dest=file, link_callback=link_callback)
                if pisa_status.err:
                    return HttpResponse('We had some errors <pre>' + html + '</pre>')

        # Send a response to the client to confirm that the PDF has been saved
        message = f"{len(queryset)} PDF files saved successfully."
        self.message_user(request, message)

    pdf_action.short_description = 'Print PDF'
    
    def pdf_action_view(self, request):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        queryset = self.get_queryset(request).filter(pk__in=selected)
        self.pdf_action(request, queryset)

        return redirect('/admin/Room/reservation')
    
    form = ReservationForm
       
class MyRoomAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    
    

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(MyRoom,MyRoomAdmin)