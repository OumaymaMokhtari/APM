from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employe
from .forms import EmployeCreationForm, EmployeUpdateForm

class EmployeAdmin(UserAdmin):
    add_form = EmployeCreationForm
    form = EmployeUpdateForm
    model = Employe

    list_display = ['id', 'nom', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser']
    
    fieldsets = (
        (None, {'fields': ('nom', 'role', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('nom',)
    ordering = ('nom',)

admin.site.register(Employe, EmployeAdmin)
