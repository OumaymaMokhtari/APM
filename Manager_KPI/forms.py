from django import forms
from .models import Kpi, ShiftReport

class KpiForm(forms.ModelForm):
    class Meta:
        model = Kpi
        fields = ['nom', 'unite', 'frequence', 'departement', 'aggregation_type']

class ShiftReportForm(forms.ModelForm):
    class Meta:
        model = ShiftReport
        fields = [
            "date","shift","sup","effectif",
            "abs_non_justifie","mis_a_pied","conge","maternite",
            "maladie","autorise","autre",
        ]
