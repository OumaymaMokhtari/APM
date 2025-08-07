from django import forms
from .models import KpiTarget, KpiValue
from .models import Kpi

class KpiForm(forms.ModelForm):
    class Meta:
        model = Kpi
        fields = ['nom', 'unite', 'frequence', 'departement', 'aggregation_type']
class KpiTargetForm(forms.ModelForm):
    class Meta:
        model = KpiTarget
        fields = ['kpi', 'valeur_objectif', 'target_date', 'frequency', 'valid_from', 'valid_to']

class KpiValueForm(forms.ModelForm):
    class Meta:
        model = KpiValue
        fields = ['kpi', 'valeur', 'employe', 'date']
