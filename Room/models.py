

from django.db import models
from django.core.exceptions import ValidationError
from Register.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from Driver.models import Driver

class MyRoom(models.Model):
    ROOM = 0
    VECHICLE = 1
    CATEGORY =    (
        (ROOM, _("Bilik")),
        (VECHICLE, _("Kenderaan"))
    )
    
    name = models.CharField(max_length=200)
    category = models.SmallIntegerField(choices=CATEGORY, default=ROOM)
    
    def is_available_on_date(self, start_date,end_date):
        reservations = self.reservations.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            status=Reservation.APPROVE,
        )
        return not reservations.exists()
    

class Reservation(models.Model):
    REQUESTED = 0
    APPROVE = 1
    DENIED = 2
    STATUS =    (
        (REQUESTED, _("Menuggu")),
        (APPROVE, _("Diluluskan")),
        (DENIED, _("Tidak Diluluskan"))
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reservations')
    name = models.ForeignKey(MyRoom, on_delete=models.CASCADE, related_name='reservations')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    participant = models.IntegerField(default=1)
    status = models.SmallIntegerField(choices=STATUS, default=REQUESTED)
    destination = models.CharField( max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=200, blank=True,null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='reservations', blank=True, null=True)
    file = models.CharField(max_length=255, blank=True, null= True)
    reserved = models.DateTimeField(default=timezone.now)
    
    
    
    def create_reservation(user,name, start_date, end_date,participant,destination,reason):
        my_instance = MyRoom.objects.get(name=name)
        my_dricer = Driver.objects.get
        existing_reservations = Reservation.objects.filter(
            name=my_instance,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status=Reservation.APPROVE
        )
        if existing_reservations.exists():
            raise ValidationError(f"{name} is already reserved during that time.")
        reservation = Reservation.objects.create(
            user=user,
            name=my_instance,
            start_date=start_date,
            end_date=end_date,
            participant = participant,
            status=Reservation.REQUESTED,
            destination = destination,
            reason = reason,
        )
        return reservation
# Create your models here.
