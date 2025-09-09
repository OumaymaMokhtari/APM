from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Employe, Departement

class EmployeCreationForm(UserCreationForm):
    """Formulaire de création d'un Employe."""
    class Meta:
        model = Employe
        fields = (
            "username", "password1", "password2",
            "first_name", "last_name", "email",
            "nom", "role", "departement",
            "is_active", "is_staff", "is_superuser", "groups",
        )

class EmployeUpdateForm(UserChangeForm):
    """Formulaire d'édition d'un Employe."""
    password = None  # on ne montre pas le hash
    class Meta:
        model = Employe
        fields = (
            "username",
            "first_name", "last_name", "email",
            "nom", "role", "departement",
            "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
        )

class DepartementForm(forms.ModelForm):
    """Formulaire simple pour créer/éditer un Département."""
    class Meta:
        model = Departement
        fields = ("nom", "description", "responsable")
