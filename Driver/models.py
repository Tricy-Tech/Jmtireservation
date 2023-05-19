from django.db import models


class Driver(models.Model):
    full_name = models.CharField (max_length=255, blank = True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, blank=True)

