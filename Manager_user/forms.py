from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Employe, Departement, Service, Poste

class EmployeCreationForm(UserCreationForm):
    class Meta:
        model = Employe
        fields = ['nom', 'role', 'departement', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"{self.cleaned_data['nom']}".lower()
        if commit:
            user.save()
        return user

class EmployeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['username', 'nom', 'role', 'departement']
class DepartementForm(forms.ModelForm):
    class Meta:
        model = Departement
        fields = ['nom', 'description', 'responsable']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom', 'departement']
class PosteForm(forms.ModelForm):
    class Meta:
        model = Poste
        fields = ['nom', 'service']


