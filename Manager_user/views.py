from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps

from .forms import EmployeCreationForm, EmployeUpdateForm, DepartementForm
from .models import Employe, Departement  



# ------------------------------
# Helpers d'autorisation
# ------------------------------
def can_manage_hr(user) -> bool:
    """Accès autorisé pour:
       - Plant Manager
       - Manager du département RH/HR
    """
    if not getattr(user, "is_authenticated", False):
        return False
    role = (getattr(user, "role", "") or "").lower()

    dep_name = ""
    dep = getattr(user, "departement", None)
    if dep:
        dep_name = (getattr(dep, "nom", "") or "").lower()

    return role == "plant manager" or (role == "manager" and dep_name in ("rh", "hr"))


def hr_required(viewfunc):
    """Décorateur: exige Plant Manager OU Manager RH/HR.
       Redirige vers l'accueil si l'accès est refusé.
    """
    @wraps(viewfunc)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not can_manage_hr(request.user):
            messages.error(request, "Accès réservé au Plant Manager et au Manager RH.")
            return redirect("accueil")
        return viewfunc(request, *args, **kwargs)
    return _wrapped


# ------------------------------
# Vues publiques / générales
# ------------------------------
def accueil(request):
    return render(request, 'accueil.html')


# ------------------------------
# Employés (protégé)
# ------------------------------
@hr_required
def liste_employes(request):
    employes = Employe.objects.all()
    return render(request, 'manager_user/liste_employes.html', {'employes': employes})

@hr_required
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

@hr_required
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

@hr_required
def supprimer_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    employe.delete()
    messages.success(request, "Employé supprimé.")
    return redirect('liste_employes')


# ------------------------------
# Départements (protégé)
# ------------------------------
@hr_required
def liste_departements(request):
    departements = Departement.objects.all()
    return render(request, 'departements/liste_departements.html', {'departements': departements})

@hr_required
def ajouter_departement(request):
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Département ajouté.")
            return redirect('liste_departements')
    else:
        form = DepartementForm()
    return render(request, 'departements/form_departement.html', {'form': form})

@hr_required
def modifier_departement(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    form = DepartementForm(request.POST or None, instance=departement)
    if form.is_valid():
        form.save()
        messages.success(request, "Département modifié.")
        return redirect('liste_departements')
    return render(request, 'departements/form_departement.html', {'form': form})

@hr_required
def supprimer_departement(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    if request.method == 'POST':
        departement.delete()
        messages.success(request, "Département supprimé.")
        return redirect('liste_departements')
    return render(request, 'departements/confirmer_suppression.html', {'objet': departement})

@hr_required
def detail_departement(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    services = departement.services.all()
    return render(request, 'departement/detail_departement.html', {'departement': departement, 'services': services})

# Décommente si tu utilises Service et n'oublie pas de l'importer
# @hr_required
# def detail_service(request, pk):
#     service = get_object_or_404(Service, pk=pk)
#     postes = service.postes.all()
#     return render(request, 'departement/detail_service.html', {'service': service, 'postes': postes})
