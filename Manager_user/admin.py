# Manager_user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employe, Departement
from .forms import EmployeCreationForm, EmployeUpdateForm



@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    """Admin simple pour les départements."""
    list_display = ("nom", "responsable")
    search_fields = ("nom",)
    autocomplete_fields = ("responsable",)


@admin.register(Employe)
class EmployeAdmin(UserAdmin):
    """
    Admin pour le modèle utilisateur custom `Employe` (hérite d'AbstractUser).
    → On conserve les champs d'auth Django (username, password…)
    → On expose les champs ajoutés: nom, role, departement
    """
    add_form = EmployeCreationForm          # formulaire de création
    form = EmployeUpdateForm                # formulaire d’édition
    model = Employe

    # colonnes de la liste
    list_display = ("username", "get_name", "role", "departement", "is_active", "is_staff")
    list_filter  = ("role", "departement", "is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email", "nom")
    ordering = ("username",)

    # lecture seule utile
    readonly_fields = ("last_login", "date_joined")

    # sections d'édition (édition)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Identité", {"fields": ("first_name", "last_name", "email", "nom", "role", "departement")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )

    # sections d'édition (création)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "password1", "password2",
                "first_name", "last_name", "email",
                "nom", "role", "departement",
                "is_active", "is_staff", "is_superuser", "groups",
            ),
        }),
    )

    def get_name(self, obj):
        """Affiche un nom lisible dans la liste."""
        return obj.get_full_name() or f"{obj.first_name} {obj.last_name}".strip() or obj.nom or obj.username
    get_name.short_description = "Nom complet"


# ====== Optionnel: admin dédié aux Superviseurs ======
# Décommente si tu as bien défini le modèle Superviseur(Employe).
# @admin.register(Superviseur)
# class SuperviseurAdmin(EmployeAdmin):
#     """Vue filtrée des employés avec rôle 'superviseur'."""
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.filter(role="superviseur")
# 
#     def save_model(self, request, obj, form, change):
#         # on force le rôle pour garantir l’intégrité
#         obj.role = "superviseur"
#         super().save_model(request, obj, form, change)
