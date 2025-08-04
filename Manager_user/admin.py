from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employe
from .forms import EmployeCreationForm, EmployeUpdateForm

class EmployeAdmin(UserAdmin):
    add_form = EmployeCreationForm
    form = EmployeUpdateForm
    model = Employe

    list_display = ['nom', 'prenom', 'telephone', 'role']
    fieldsets = (
        (None, {'fields': ('nom', 'prenom', 'telephone', 'adresse', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'prenom', 'telephone', 'adresse', 'role', 'password1', 'password2'),
        }),
    )

admin.site.register(Employe, EmployeAdmin)
