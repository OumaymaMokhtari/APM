from django import forms
from Manager_user.models import Employe
from .models import Kpi, Absence


# Formulaire pour créer/modifier un KPI (nom, unité, fréquence, département, agrégation).
class KpiForm(forms.ModelForm):
    class Meta:
        model = Kpi
        fields = ["nom", "unite", "frequence", "departement", "aggregation_type"]


# Formulaire pour saisir un rapport d’absence (date, shift, superviseur, effectif, motifs).
class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = [
            "date", "shift", "sup", "effectif",
            "abs_non_justifie", "mis_a_pied", "conge", "maternite",
            "maladie", "autorise", "autre", "autre_motif",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "effectif": forms.NumberInput(attrs={"min": 1}),
            "abs_non_justifie": forms.NumberInput(attrs={"min": 0}),
            "mis_a_pied": forms.NumberInput(attrs={"min": 0}),
            "conge": forms.NumberInput(attrs={"min": 0}),
            "maternite": forms.NumberInput(attrs={"min": 0}),
            "maladie": forms.NumberInput(attrs={"min": 0}),
            "autorise": forms.NumberInput(attrs={"min": 0}),
            "autre": forms.NumberInput(attrs={"min": 0}),
        }
        labels = {
            "abs_non_justifie": "Absent non justifié",
            "mis_a_pied": "Mis à pied",
            "conge": "Congé",
            "maternite": "Maternité (MAT)",
            "maladie": "Maladie",
            "autorise": "Autorisé",
            "autre": "Autre",
            "autre_motif": "Motif (si Autre > 0)",
        }

    # Restreint le choix du superviseur (sup) aux employés ayant le rôle "superviseur".
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Employe.objects.all()
        if hasattr(Employe, "Role") and hasattr(Employe.Role, "SUPERVISEUR"):
            qs = qs.filter(role=Employe.Role.SUPERVISEUR)
        else:
            qs = qs.filter(role__iexact="superviseur")
        self.fields["sup"].queryset = qs.order_by("nom")


# Alias conservé pour compatibilité : identique à AbsenceForm (anciens imports).
class ShiftReportForm(AbsenceForm):
    pass
