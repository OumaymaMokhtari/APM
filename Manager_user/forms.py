from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Employe, Departement


# Formulaire d’ajout d’un nouvel utilisateur Employe (avec champs d’authentification).
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


# Formulaire de mise à jour d’un Employe existant (sans afficher le mot de passe hashé).
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


# Formulaire simple pour ajouter/éditer un département (nom, description, responsable).
class DepartementForm(forms.ModelForm):
    """Formulaire simple pour créer/éditer un Département."""
    class Meta:
        model = Departement
        fields = ("nom", "description", "responsable")
