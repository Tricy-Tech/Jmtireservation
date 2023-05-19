from django.contrib import admin
from .models import Driver
# Register your models here.

class DriverAdmin(admin.ModelAdmin):
    list_display = ('id','full_name', 'email')
    

admin.site.register(Driver,DriverAdmin)