from django.db import models
from django.utils import timezone  
from Manager_user.models import Departement, Employe

class Kpi(models.Model):
    FREQUENCE_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly")
    ]
    
    AGGREGATION_CHOICES = [
        ("sum", "Somme"),
        ("avg", "Moyenne")
    ]

    nom = models.CharField(max_length=255)
    unite = models.CharField(max_length=50)
    frequence = models.CharField(max_length=10, choices=FREQUENCE_CHOICES)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='kpis')
    aggregation_type = models.CharField(max_length=10, choices=AGGREGATION_CHOICES)
    
    date_measured = models.DateField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class KpiTarget(models.Model):
    kpi = models.OneToOneField(Kpi, on_delete=models.CASCADE, related_name='target')
    valeur_objectif = models.FloatField()
    target_date = models.DateField(default=timezone.now)
    frequency = models.CharField(
        max_length=10,
        choices=Kpi.FREQUENCE_CHOICES
    )
    created_by = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Objectif pour {self.kpi.nom}"

class KpiValue(models.Model):
    kpi = models.ForeignKey(Kpi, on_delete=models.CASCADE, null=True)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='kpi_values_enregistrees')
    valeur = models.FloatField()
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='kpi_values_crees')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kpi.nom} = {self.valeur}"
