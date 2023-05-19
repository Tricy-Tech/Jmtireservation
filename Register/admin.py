from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'id_number')

admin.site.register(CustomUser, CustomUserAdmin)