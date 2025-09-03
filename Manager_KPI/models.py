from django.db import models
from django.utils import timezone  
from Manager_user.models import Departement, Employe
from django.conf import settings
from django.db import models
from django.db.models import Q, Sum

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

class ShiftChoices(models.TextChoices):
    MATIN = "MATIN", "Matin"
    SOIR  = "SOIR",  "Soir"
    NUIT  = "NUIT",  "Nuit"

class AbsenceType(models.TextChoices):
    ABS_NON_JUST = "ABS_NON_JUST", "Absent non justifié"
    MIS_A_PIED   = "MIS_A_PIED",   "Mis à pied"
    CONGE        = "CONGE",        "Congé"
    MALADIE      = "MALADIE",      "Maladie"
    MATERNITE    = "MATERNITE",    "Maternité (MAT)"
    AUTORISE     = "AUTORISE",     "Autorisé"
    AUTRE        = "AUTRE",        "Autre"

class ShiftReport(models.Model):
    date     = models.DateField()
    shift    = models.CharField(max_length=10, choices=ShiftChoices.choices)
    sup      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="kpi_shift_reports")
    effectif = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "shift", "sup"]
        constraints = [
            models.UniqueConstraint(fields=["date", "shift", "sup"], name="uniq_shiftreport_date_shift_sup"),
            models.CheckConstraint(check=Q(effectif__gte=1), name="ck_shiftreport_effectif_gte_1"),
        ]

    def __str__(self):
        return f"{self.date} · {self.get_shift_display()} · {self.sup}"

    # helpers
    @property
    def total_absences(self):
        return self.lines.aggregate(s=Sum("qty"))["s"] or 0

    @property
    def taux_absence(self):
        return (self.total_absences / self.effectif * 100.0) if self.effectif else 0.0


class AbsenceLine(models.Model):
    report = models.ForeignKey(ShiftReport, on_delete=models.CASCADE, related_name="lines")
    type   = models.CharField(max_length=20, choices=AbsenceType.choices)
    qty    = models.PositiveIntegerField()    # ≥ 1 pour une ligne enregistrée
    autre_motif = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["report_id", "type"]
        constraints = [
            models.CheckConstraint(check=Q(qty__gte=1), name="ck_absenceline_qty_gte_1"),
            models.UniqueConstraint(fields=["report", "type"], name="uniq_line_per_type_per_report"),
        ]

    def __str__(self):
        return f"{self.report} · {self.get_type_display()} · {self.qty}"