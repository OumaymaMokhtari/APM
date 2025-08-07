from django.contrib import admin

from .models import KpiTarget, KpiValue

@admin.register(KpiTarget)
class KpiTargetAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KpiTarget._meta.fields]

@admin.register(KpiValue)
class KpiValueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KpiValue._meta.fields]
