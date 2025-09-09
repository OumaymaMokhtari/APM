from django.db import models
from django.utils import timezone
from django.db.models import Q, Sum
from django.conf import settings


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


# --- SHIFTS (on garde les choix)
class ShiftChoices(models.TextChoices):
    MATIN = "MATIN", "Matin"
    SOIR  = "SOIR",  "Soir"
    NUIT  = "NUIT",  "Nuit"


class ShiftReport(models.Model):
    # clefs du shift
    date     = models.DateField()
    shift    = models.CharField(max_length=10, choices=ShiftChoices.choices)

    # SUP en menu déroulant -> table Employe
    sup      = models.ForeignKey(Employe, on_delete=models.PROTECT, related_name="kpi_shift_reports")

    # effectif total du shift
    effectif = models.PositiveIntegerField()

    # colonnes d’absence (remplacent AbsenceLine/AbsenceType)
    abs_non_justifie = models.PositiveIntegerField(default=0)
    mis_a_pied       = models.PositiveIntegerField(default=0)
    conge            = models.PositiveIntegerField(default=0)
    maternite        = models.PositiveIntegerField(default=0)  # MAT
    maladie          = models.PositiveIntegerField(default=0)
    autorise         = models.PositiveIntegerField(default=0)
    autre            = models.PositiveIntegerField(default=0)
    autre_motif      = models.CharField(max_length=120, blank=True)
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

    # === Helpers / calculs ===
    @property
    def total_absences(self) -> int:
        return (
            self.abs_non_justifie +
            self.mis_a_pied +
            self.conge +
            self.maternite +
            self.maladie +
            self.autorise +
            self.autre
        )

    @property
    def taux_absence(self) -> float:
        return (self.total_absences / self.effectif * 100.0) if self.effectif else 0.0
