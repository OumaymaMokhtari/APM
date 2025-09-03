from datetime import datetime
import json

from django.contrib import messages
from django.db import transaction
from django.db.models import F, Q, Sum
from django.shortcuts import render, redirect

from .forms import KpiForm, KpiTargetForm, KpiValueForm
from .models import (Kpi, KpiTarget, KpiValue, ShiftReport, AbsenceLine, AbsenceType,)


def ajouter_kpi(request):
    if request.method == 'POST':
        form = KpiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI créé avec succès.")
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
            messages.success(request, "Objectif KPI ajouté.")
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
            messages.success(request, "Valeur KPI enregistrée.")
            return redirect('liste_kpi_value')
    else:
        form = KpiValueForm()
    return render(request, 'Manager_KPI/ajouter_kpi_value.html', {'form': form})
def liste_kpis(request):
    kpis = Kpi.objects.all()
    return render(request, 'Manager_KPI/liste_kpis.html', {'kpis': kpis})


def absence_new(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        shift = request.POST.get('shift')
        effectif_raw = request.POST.get('effectif')
        lines_json = request.POST.get('lines_json', '[]')

        try:
            lines = json.loads(lines_json) if lines_json else []
        except json.JSONDecodeError:
            lines = []

        # Validations de base
        errors = []
        if not date:
            errors.append("La date est requise.")
        if not shift:
            errors.append("Le shift est requis.")

        try:
            effectif = int(effectif_raw)
            if effectif < 1:
                errors.append("L'effectif doit être supérieur ou égal à 1.")
        except (TypeError, ValueError):
            effectif = 0
            errors.append("Effectif invalide.")

        total_abs = 0
        for ln in lines:
            try:
                q = int(ln.get('qty', 0))
            except (TypeError, ValueError):
                q = 0
            if q < 0:
                q = 0
            total_abs += q

        if total_abs == 0:
            errors.append("Au moins un type d’absence est requis.")
        if effectif and total_abs > effectif:
            errors.append(f"Total absences ({total_abs}) > Effectif ({effectif}).")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "Manager_KPI/absence_form.html", {
                "posted_lines_json": lines_json,
            })

        # Persistance
        with transaction.atomic():

            report, created = ShiftReport.objects.get_or_create(
                date=date,
                shift=shift,
                sup=request.user,
                defaults={"effectif": effectif},
            )
            if not created:
                report.effectif = effectif
                report.save(update_fields=["effectif"])
                report.lines.all().delete()

            for ln in lines:
                t = ln.get("type")
                q = int(ln.get("qty", 0) or 0)
                autre = ln.get("autre", "") if t == "AUTRE" else ""
                if t == "AUTRE" and not autre:
                    messages.error(request, "Le motif est requis pour le type 'Autre'.")
                    raise ValueError("Motif 'Autre' manquant")
                if q < 1:
                    continue
                AbsenceLine.objects.create(
                    report=report,
                    type=t,
                    qty=q,
                    autre_motif=autre
                )

        messages.success(request, "Shift enregistré avec succès.")
        return redirect('absence_list')

    # GET
    return render(request, "Manager_KPI/absence_form.html")


def absence_list(request):
    """
    Historique empilé par type avec filtres Du / Au / Shift.
    Alimente le template absence_list.html via 'rows'.
    """
    # -- filtres GET --
    def parse_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    d_from = parse_date(request.GET.get("from", "") or "")
    d_to   = parse_date(request.GET.get("to", "") or "")
    f_shift = request.GET.get("shift") or "" 

    flt = Q()
    if d_from:
        flt &= Q(report__date__gte=d_from)
    if d_to:
        flt &= Q(report__date__lte=d_to)
    if f_shift in ("MATIN", "SOIR", "NUIT"):
        flt &= Q(report__shift=f_shift)

    qs = (AbsenceLine.objects
          .select_related("report", "report__sup")
          .filter(flt)
          .values("report_id",
                  "report__date",
                  "report__shift",
                  "report__sup__first_name",
                  "report__sup__last_name",
                  "report__sup__username",
                  "type")
          .annotate(
              qty=Sum("qty"),
              effectif=F("report__effectif"),
          )
          .order_by("-report__date", "report__shift", "type"))

    totals = {}
    for r in qs:
        rid = r["report_id"]
        totals[rid] = totals.get(rid, 0) + (r["qty"] or 0)

    label_map = dict(AbsenceType.choices)
    rows = []
    for r in qs:
        rid = r["report_id"]
        total_shift = totals.get(rid, 0)
        eff = r["effectif"] or 0
        taux = (total_shift / eff * 100.0) if eff else None

        # SUP : prénom/nom si présents, sinon username
        first = (r.get("report__sup__first_name") or "").strip()
        last  = (r.get("report__sup__last_name") or "").strip()
        usern = (r.get("report__sup__username") or "").strip()
        fullname = (f"{first} {last}").strip()
        sup_name = fullname or usern or "—"

        dt = r["report__date"]
        wk_jx = f"WK{dt.isocalendar().week} – J{dt.isoweekday()}"

        rows.append({
            "shift_report_id": rid,
            "date": dt,
            "wk_jx": wk_jx,
            "shift": r["report__shift"],
            "sup_name": sup_name,
            "type_label": label_map.get(r["type"], r["type"]),
            "qty": r["qty"] or 0,
            "effectif": eff,
            "total_shift": total_shift,
            "taux_pct": taux,
        })

    return render(request, "Manager_KPI/absence_list.html", {"rows": rows})
def absence_edit(request, pk):
    return render(request, "Manager_KPI/absence_form.html", {"edit_id": pk})
