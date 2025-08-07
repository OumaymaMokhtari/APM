from django.urls import path
from . import views

urlpatterns = [
    path('kpis/', views.liste_kpis, name='liste_kpis'),
    path('ajouter_kpi/', views.ajouter_kpi, name='ajouter_kpi'),
    path('kpis/ajouter-target/', views.ajouter_kpi_target, name='ajouter_kpi_target'),
    path('kpis/ajouter-value/', views.ajouter_kpi_value, name='ajouter_kpi_value'),
]
