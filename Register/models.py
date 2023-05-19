from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    full_name = models.CharField (max_length=255, blank = True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, blank=True)
    id_number = models.CharField(max_length=20, blank=True)
        
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='customuser_set', # add a related_name attribute
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='customuser_set', # add a related_name attribute
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )

