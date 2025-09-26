from django.contrib import admin
from .models import Kpi, Absence


# Admin pour les KPI : affiche les colonnes clés, ajoute des filtres et une recherche par nom.
@admin.register(Kpi)
class KpiAdmin(admin.ModelAdmin):
    list_display  = ("nom", "departement", "frequence", "aggregation_type", "date_modification")
    list_filter   = ("departement", "frequence", "aggregation_type")
    search_fields = ("nom",)


# Admin pour les absences : liste les rapports (date/shift/superviseur), filtres, recherche du superviseur et tri par date décroissante.
@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display  = ("date", "shift", "sup", "effectif", "total_absences", "taux_absence")
    list_filter   = ("date", "shift", "sup")
    search_fields = ("sup__username", "sup__first_name", "sup__last_name")
    ordering      = ("-date", "shift", "sup")
