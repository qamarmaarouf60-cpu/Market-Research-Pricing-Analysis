from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class MyUserAdmin(UserAdmin):
    # Tu peux personnaliser les colonnes affichées dans la liste ici
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    