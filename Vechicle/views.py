

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import DateRangeSelectionForm, ParticipantForm, ReservationForm
from .models import MyRoom, Reservation
from django.utils import timezone
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect,HttpResponseBadRequest
from dateutil.parser import parse
from django.views.generic.edit import CreateView
from django.contrib import messages
import datetime
import re
from django.core.exceptions import ValidationError
import logging

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
            form = ParticipantForm(request.POST)
            if form.is_valid():
                participant = form.cleaned_data['participant']
                request.session['participant'] = participant
            return redirect('room_list')
        else:
            url_path = request.path
            match = re.search(r'/([^/]+)/?$', url_path)
            if not match:
                return HttpResponseBadRequest()
            room = str(match.group(1))
            request.session['name'] = room
            start_date = request.session.get('start_date')
            end_date = request.session.get('end_date')
            s_dt = parse(start_date)
            e_dt = parse(end_date)
            context= {
                'room_name' : room,
                'start_date': s_dt.strftime("%m/%d/%Y"),
                'end_date': e_dt.strftime("%m/%d/%Y"),
            }
            form = ParticipantForm()
        return render(request, 'reserve.html', {'form': form, 'room_name' : room, 'start_date': s_dt.strftime("%m/%d/%Y"), 'end_date': e_dt.strftime("%m/%d/%Y")})
def finish_room(request):
    start_date = None
    if 'start_date' in request.session:
       start_date = datetime.datetime.fromisoformat(request.session['start_date'])
    end_date = None
    if 'end_date' in request.session:
        end_date = datetime.datetime.fromisoformat(request.session['end_date'])
    
    context = {
        'name' : request.session.get('name'),
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
    Reservation.create_reservation(request.user, request.session.get('name'), start_date, end_date,request.session.get('participant'),)
    for key in list(request.session.keys()):
        if key != 'user':
            del request.session[key]
    
    return redirect('home')
    
def add_reservation(request):
    start_date = None
    if 'start_date' in request.session:
       start_date = datetime.datetime.fromisoformat(request.session['start_date'])
    end_date = None
    if 'end_date' in request.session:
        end_date = datetime.datetime.fromisoformat(request.session['end_date'])
        
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.POST.get('user')
            reservation.name = request.POST.get('name')
            reservation.start_date = request.POST.get('start_date')
            reservation.end_date = request.POST.get('end_date')
            reservation.participant = request.POST.get('participant')
            reservation.status = "REQUEST"
            reservation.save()
            return redirect('home')
        else:
            logging(form.errors)
    else:
        form = ReservationForm(user=request.user,
                               data=request.POST,
                               initial={
                                   'name' : request.session.get('name'),
                                   'start_date': start_date,
                                   'end_date':end_date,
                                   'participant':request.session.get('participant'),
                                   'status': "REQUEST"
                                   }
                               )
    return render(request, 'reservation_form.html', {'form': form, 'user': request.user, 'name': request.session.get('name'), 'start_date': start_date, 'end_date': end_date, 'participant': request.session.get('participant'), 'status': "REQUEST"})

        
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
        })
    
    return JsonResponse(out, safe=False)
        
def home(request):
    list_object = MyRoom.objects.all()
    return render(request, 'index1.html', context={
        'list_object': list_object
    })

