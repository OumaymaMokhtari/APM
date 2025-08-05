from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import EmployeCreationForm, EmployeUpdateForm, DepartementForm, ServiceForm, PosteForm
from .models import Employe, Departement, Service, Poste

def accueil(request):
    return render(request, 'accueil.html')

def liste_employes(request):
    employes = Employe.objects.all()
    return render(request, 'manager_user/liste_employes.html', {'employes': employes})

def create_employe(request):
    if request.method == 'POST':
        form = EmployeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé ajouté avec succès.")
            return redirect('liste_employes')
    else:
        form = EmployeCreationForm()
    return render(request, 'manager_user/ajouter_employe.html', {'form': form})

def modifier_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    if request.method == 'POST':
        form = EmployeUpdateForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé modifié avec succès.")
            return redirect('liste_employes')
        else:
            print(form.errors)
    else:
        form = EmployeUpdateForm(instance=employe)
    return render(request, 'manager_user/ajouter_employe.html', {'form': form})
def supprimer_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    employe.delete()
    return redirect('liste_employes')
def liste_departements(request):
    departements = Departement.objects.all()
    return render(request, 'departements/liste_departements.html', {'departements': departements})
def ajouter_departement(request):
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_departements')
    else:
        form = DepartementForm()
    return render(request, 'departements/form_departement.html', {'form': form})

def modifier_departement(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    form = DepartementForm(request.POST or None, instance=departement)
    if form.is_valid():
        form.save()
        return redirect('liste_departements')
    return render(request, 'departements/form_departement.html', {'form': form})

def supprimer_departement(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    if request.method == 'POST':
        departement.delete()
        return redirect('liste_departements')
    return render(request, 'departements/confirmer_suppression.html', {'objet': departement})
def detail_departement(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    services = departement.services.all()
    return render(request, 'departement/detail_departement.html', {'departement': departement, 'services': services})

def detail_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    postes = service.postes.all()
    return render(request, 'departement/detail_service.html', {'service': service, 'postes': postes})
