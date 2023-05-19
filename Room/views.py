

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import DateRangeSelectionForm, ParticipantForm, ReservationForm
from .models import MyRoom, Reservation
from django.utils import timezone
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect,HttpResponseBadRequest
from dateutil.parser import parse
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import datetime
import re
from django.core.exceptions import ValidationError
import logging
from django.contrib.staticfiles import finders

def refresh(request):
    request.session.clear()
    return redirect('/')

def date_selection(request):
    if request.method == 'POST':
        form = DateRangeSelectionForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # Store the selected dates in the session
            request.session['start_date'] = start_date.isoformat()
            request.session['end_date'] = end_date.isoformat()
            # Redirect to the room selection page
            return redirect(list_Room)
    else:
        form = DateRangeSelectionForm()
    return render(request, 'date_selection.html', {'form': form})


def list_Room(request):
    # Get all rooms
    rooms = MyRoom.objects.all()
        
    # Get reservations that overlap with the selected dates, if any
    start_date = request.session.get('start_date')
    end_date = request.session.get('end_date')
    overlapping_reservations = None
    if start_date and end_date:
        overlapping_reservations = Reservation.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            status=Reservation.APPROVE,
        )

    # Exclude rooms that have overlapping reservations
    unavailable_rooms = [reservation.name for reservation in overlapping_reservations] if overlapping_reservations else []
    available_rooms = [room for room in rooms if room not in unavailable_rooms]
    s_dt = parse(start_date)
    e_dt = parse(end_date)
    context = {
        'u_rooms': unavailable_rooms,
        'a_rooms' : available_rooms,
        'start_date': s_dt.strftime("%m/%d/%Y"),
        'end_date': e_dt.strftime("%m/%d/%Y"),
    }

    return render(request, 'index1.html', context)

def Reserve(request, name):
        if request.method == 'POST':
            reason = request.POST.get('reason')
            participant = request.POST.get('participant')
            destination = request.POST.get('destination')
            request.session['reason'] = reason
            request.session['participant'] = participant
            request.session['destination'] = destination
            if not participant and not reason:
                request.session['error'] = "The reason and participant field is required."
                return render(request, 'reserve.html')
            if not reason:
                request.session['error'] = "The reason field is required."
                return render(request, 'reserve.html')
            if not participant:
                request.session['error'] = "The participant field is required."
                return render(request, 'reserve.html')
            if not participant.isdigit():
                request.session['error'] = 'Participant must be an integer.'
                return render(request, 'reserve.html')
            
            if request.session['category'] == 1:
                if not participant and not reason and not destination:
                    request.session['error'] = "The reason, participant and destination field is required."
                    return render(request, 'reserve.html')
                if not participant and destination:
                    request.session['error'] = "The particiapnt and destinaiton field is required."
                    return render(request, 'reserve.html')
                if not reason and destination:
                    request.session['error'] = "The reason and destinaiton field is required."
                    return render(request, 'reserve.html')
                if not destination:
                    request.session['error'] = "The destinaiton field is required."
                    return render(request, 'reserve.html')
            
           
            
            request.session['error']= ""
            return redirect('room_list')
        else:
            url_path = request.path
            match = re.search(r'/([^/]+)/?$', url_path)
            if not match:
                return HttpResponseBadRequest()
            room = str(match.group(1))
            request.session['name'] = room
            my_instance = MyRoom.objects.get(name=room)
            category = 'category'
            Category = getattr(my_instance, category)
            request.session['category'] = Category
            start_date = request.session.get('start_date')
            end_date = request.session.get('end_date')
            s_dt = parse(start_date)
            e_dt = parse(end_date)
            request.session['s_dt']= s_dt.strftime("%m/%d/%Y")
            request.session['e_dt']= e_dt.strftime("%m/%d/%Y")            
        return render(request, 'reserve.html')
    
def finish_room(request):
    start_date = None
    if 'start_date' in request.session:
       start_date = datetime.datetime.fromisoformat(request.session['start_date'])
    end_date = None
    if 'end_date' in request.session:
        end_date = datetime.datetime.fromisoformat(request.session['end_date'])
    
    context = {
        'name' : request.session.get('name'),
        'reason' : request.session.get('reason'),
        'destination' : request.session.get('destination'),
        'start_date': start_date,
        'end_date':end_date,
        'participant':request.session.get('participant'),
        'status': "REQUEST"
    }
    
    return render(request, 'reservation_form.html', context)

def sumbit_room(request):
    start_date = None
    if 'start_date' in request.session:
       start_date = datetime.datetime.fromisoformat(request.session['start_date'])
    end_date = None
    if 'end_date' in request.session:
        end_date = datetime.datetime.fromisoformat(request.session['end_date'])
    Reservation.create_reservation(request.user, request.session.get('name'), start_date, end_date,request.session.get('participant'),request.session.get('destination'),request.session.get('reason'))
    for key in list(request.session.keys()):
        if key != 'user':
            del request.session[key]
    
    return redirect('home')

        
def all_events1(request):                                                                                                 
    all_events1 = Reservation.objects.all()
    out = []                                                                                                         
    for event in all_events1:                                                                                           
        out.append({                                                                                                     
            'title': f"{event.user} - {event.name.name}",
            'status': event.status,
            'id': event.id,                                                                                              
            'start': event.start_date.strftime("%m/%d/%Y, %H:%M:%S"),                                                         
            'end': event.end_date.strftime("%m/%d/%Y, %H:%M:%S"), 
            'className': 'reserved' if event.status == 1 else '',
        })
    
    return JsonResponse(out, safe=False)
        
def home(request):
    list_object = MyRoom.objects.all()
    return render(request, 'index1.html', context={
        'list_object': list_object
    })
    
def Email_approve(request):
    message = 'hye'
    email = ['kanekihimito29@gmail.com','tmuhdridhwan@gmail.com']
    name = 'trying'
    sender = settings.EMAIL_HOST_USER
    send_mail(
    name,#Title
    message,#message
    sender,# sender
    email,#reseive email
    )
    return render(request,'email_sent.html')

# views.py
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings
'''
def send_email(request):
    if request.method == 'POST':
        subject = 'Test email with attachment'
        message = 'Please see the attached file for more information.'
        from_email = 'tmuhammadridhwan@gmail.com'
        recipient_list = ['kanekihimito29@gmail.com','tmuhdridhwan@gmail.com']
        uploaded_file = request.FILES['file']
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
        email.send()
        return render(request, 'email_sent.html')
    return render(request, 'file.html')
'''
import os
def send_email_vechicle(request, pemohon,driver, file):
    recipient_email = pemohon
    subject = 'Test email with attachment'
    message = 'Please see the attached file for more information.'
    from_email = 'tmuhammadridhwan@gmail.com'
    recipient_list = ['kanekihimito29@gmail.com', recipient_email]

    # Get the path of the PDF file
    file_path = os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemohon', file)

    # Open the file and read its contents
    with open(file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

        # Create the email message and attach the PDF file
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach('Notis Tempahan.pdf', pdf_data, 'application/pdf')
    email.send()
    
    recipient_email = driver
    subject = 'Test email with attachment'
    message = 'Please see the attached file for more information.'
    from_email = 'tmuhammadridhwan@gmail.com'
    recipient_list = ['kanekihimito29@gmail.com', recipient_email]

    # Get the path of the PDF file
    file_path = os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemandu', file)

    # Open the file and read its contents
    with open(file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

        # Create the email message and attach the PDF file
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach('Notis Pemandu.pdf', pdf_data, 'application/pdf')
    email.send()

    return HttpResponse('Email sent with attached PDF file')

def send_email_applicant(request,driver, file):
    recipient_email = driver
    subject = 'Test email with attachment'
    message = 'Please see the attached file for more information.'
    from_email = 'tmuhammadridhwan@gmail.com'
    recipient_list = ['kanekihimito29@gmail.com', recipient_email]

    # Get the path of the PDF file
    file_path = os.path.join(settings.BASE_DIR, 'pdf', 'PDF_save/Pemohon', file)

    # Open the file and read its contents
    with open(file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

        # Create the email message and attach the PDF file
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach('Notis Pemandu.pdf', pdf_data, 'application/pdf')
    email.send()

    return HttpResponse('Email sent with attached PDF file')


    
# views.py
from django.shortcuts import render
from django.core.mail import send_mail
from Register.models import CustomUser

def s_email(request):
    subject = 'Test email'
    message = 'This is a test email sent from a Django application.'
    from_email = 'tmuhammadridhwan@gmail.com'
    recipient_list = ['kanekihimito29@gmail.com','tmuhdridhwan@gmail.com']
    send_mail(subject, message, from_email, recipient_list)
    return render(request, 'email_sent.html')

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Reservation

def print_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    template_path = 'myapp/reservation_pdf.html'
    context = {'reservation': reservation}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="reservation_{}.pdf"'.format(pk)
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed!')
    return response

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
