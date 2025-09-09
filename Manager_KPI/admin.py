from django.contrib import admin
from .models import Kpi, ShiftReport

@admin.register(Kpi)
class KpiAdmin(admin.ModelAdmin):
    list_display  = ("nom","departement","frequence","aggregation_type","date_modification")
    list_filter   = ("departement","frequence","aggregation_type")
    search_fields = ("nom",)

@admin.register(ShiftReport)
class ShiftReportAdmin(admin.ModelAdmin):
    list_display  = ("date","shift","sup","effectif","total_absences","taux_absence")
    list_filter   = ("date","shift","sup")
