from django.shortcuts import render, redirect
from .forms import KpiTargetForm, KpiValueForm
from .models import KpiTarget, KpiValue
from .forms import KpiForm
from .models import Kpi

def ajouter_kpi(request):
    if request.method == 'POST':
        form = KpiForm(request.POST)
        if form.is_valid():
            kpi = form.save()
            return redirect('liste_kpis') 
    else:
        form = KpiForm()
    return render(request, 'Manager_KPI/ajouter_kpi.html', {'form': form})

def ajouter_kpi_target(request):
    if request.method == 'POST':
        form = KpiTargetForm(request.POST)
        if form.is_valid():
            kpi_target = form.save(commit=False)
            kpi_target.created_by = request.user
            kpi_target.save()
            return redirect('liste_kpi_target')
    else:
        form = KpiTargetForm()
    return render(request, 'Manager_KPI/ajouter_kpi_target.html', {'form': form})

def ajouter_kpi_value(request):
    if request.method == 'POST':
        form = KpiValueForm(request.POST)
        if form.is_valid():
            kpi_value = form.save(commit=False)
            kpi_value.created_by = request.user 
            kpi_value.save()
            return redirect('liste_kpi_value')
    else:
        form = KpiValueForm()
    return render(request, 'Manager_KPI/ajouter_kpi_value.html', {'form': form})

def liste_kpis(request):
    kpis = Kpi.objects.all()
    return render(request, 'Manager_KPI/liste_kpis.html', {'kpis': kpis})