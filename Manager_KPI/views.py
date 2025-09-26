from datetime import datetime
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse

from Manager_user.models import Employe
from .models import Kpi, Absence


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

# Convertit proprement en entier non négatif (retourne default en cas d’erreur).
def _to_int(x, default=0):
    """Convertit en int >= 0 (évite les ValueError)."""
    try:
        return max(0, int(x))
    except Exception:
        return default


# Renvoie uniquement les employés ayant le rôle "superviseur" (compatible Enum/texte).
def supervisors_qs():
    """
    Retourne uniquement les employés ayant le rôle 'superviseur'.
    Compatible avec un Enum Employe.Role.SUPERVISEUR ou une chaîne simple.
    """
    qs = Employe.objects.all()
    if hasattr(Employe, "Role") and hasattr(Employe.Role, "SUPERVISEUR"):
        return qs.filter(role=Employe.Role.SUPERVISEUR)
    return qs.filter(role__iexact="superviseur")

# ---------------------------------------------------------------------
# Vues KPI (génériques)
# ---------------------------------------------------------------------

# Crée un nouveau KPI via formulaire (POST) ou affiche le formulaire (GET).
def ajouter_kpi(request):
    from .forms import KpiForm  # import local
    if request.method == 'POST':
        form = KpiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI créé avec succès.")
            return redirect('liste_kpis')
    else:
        form = KpiForm()
    return render(request, 'Manager_KPI/ajouter_kpi.html', {'form': form})


# Affiche la liste simple de tous les KPI.
def liste_kpis(request):
    kpis = Kpi.objects.all()
    return render(request, 'Manager_KPI/liste_kpis.html', {'kpis': kpis})


# ---------------------------------------------------------------------
# KPI Absence (modèle Absence)
# ---------------------------------------------------------------------

# Création/mise à jour d’une Absence (clé unique: date+shift+sup) à partir des 7 motifs.
def absence_new(request):

    sups = supervisors_qs().order_by("nom")

    if request.method == "POST":
        date_str = request.POST.get("date")
        shift    = request.POST.get("shift")
        effectif = _to_int(request.POST.get("effectif"))
        sup_id   = request.POST.get("sup_id")
        sup      = supervisors_qs().filter(id=sup_id).first()

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Date invalide.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})
        if not shift:
            messages.error(request, "Veuillez choisir un shift.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})
        if not sup:
            messages.error(request, "Veuillez choisir un SUP (superviseur).")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})
        if effectif < 1:
            messages.error(request, "Effectif invalide (≥ 1).")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})

        data = {
            "abs_non_justifie": _to_int(request.POST.get("abs_non_justifie")),
            "mis_a_pied":       _to_int(request.POST.get("mis_a_pied")),
            "conge":            _to_int(request.POST.get("conge")),
            "maternite":        _to_int(request.POST.get("maternite")),
            "maladie":          _to_int(request.POST.get("maladie")),
            "autorise":         _to_int(request.POST.get("autorise")),
            "autre":            _to_int(request.POST.get("autre")),
        }
        autre_motif = (request.POST.get("autre_motif") or "").strip()
        total_abs = sum(data.values())

        if total_abs == 0:
            messages.error(request, "Renseigne au moins un type d’absence.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})
        if total_abs > effectif:
            messages.error(request, f"Total absences ({total_abs}) > Effectif ({effectif}).")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})
        if data["autre"] > 0 and not autre_motif:
            messages.error(request, "Merci de préciser le motif si ‘Autre’ > 0.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups})

        Absence.objects.update_or_create(
            date=date, shift=shift, sup=sup,
            defaults={
                "effectif": effectif,
                "autre_motif": autre_motif,
                **data,
            }
        )

        messages.success(request, "Absence enregistrée.")
        return redirect("absence_list")

    # GET
    return render(request, "Manager_KPI/absence_form.html", {"sups": sups})


# Édite une Absence existante (gère le changement de clé en “upsert” + suppression ancien).
def absence_edit(request, pk):
    """
    Édition d’une Absence existante.
    Si la clé (date, shift, sup) change, on upsert la nouvelle puis
    on supprime l’ancienne pour éviter les doublons.
    """
    obj  = get_object_or_404(Absence, pk=pk)
    sups = supervisors_qs().order_by("nom")

    if request.method == "POST":
        date_str = request.POST.get("date") or obj.date.strftime("%Y-%m-%d")
        shift    = request.POST.get("shift") or obj.shift
        effectif = _to_int(request.POST.get("effectif"), obj.effectif)
        sup_id   = request.POST.get("sup_id") or str(obj.sup_id)

        sup = supervisors_qs().filter(id=sup_id).first()
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Date invalide.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})

        if not shift:
            messages.error(request, "Veuillez choisir un shift.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})
        if not sup:
            messages.error(request, "Veuillez choisir un SUP (superviseur).")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})
        if effectif < 1:
            messages.error(request, "Effectif invalide (≥ 1).")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})

        data = {
            "abs_non_justifie": _to_int(request.POST.get("abs_non_justifie"), obj.abs_non_justifie),
            "mis_a_pied":       _to_int(request.POST.get("mis_a_pied"),       obj.mis_a_pied),
            "conge":            _to_int(request.POST.get("conge"),            obj.conge),
            "maternite":        _to_int(request.POST.get("maternite"),        obj.maternite),
            "maladie":          _to_int(request.POST.get("maladie"),          obj.maladie),
            "autorise":         _to_int(request.POST.get("autorise"),         obj.autorise),
            "autre":            _to_int(request.POST.get("autre"),            obj.autre),
        }
        autre_motif = (request.POST.get("autre_motif") or obj.autre_motif or "").strip()
        total_abs = sum(data.values())
        if total_abs == 0:
            messages.error(request, "Renseigne au moins un type d’absence.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})
        if total_abs > effectif:
            messages.error(request, f"Total absences ({total_abs}) > Effectif ({effectif}).")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})
        if data["autre"] > 0 and not autre_motif:
            messages.error(request, "Merci de préciser le motif si ‘Autre’ > 0.")
            return render(request, "Manager_KPI/absence_form.html", {"sups": sups, "obj": obj})

        with transaction.atomic():
            new_abs, _ = Absence.objects.update_or_create(
                date=date,
                shift=shift,
                sup=sup,
                defaults={
                    "effectif": effectif,
                    "autre_motif": autre_motif,
                    **data,
                }
            )
            if new_abs.pk != obj.pk:
                obj.delete()

        messages.success(request, "Shift mis à jour avec succès.")
        return redirect("absence_list")

    # GET : pré-remplissage
    ctx = {
        "sups": sups,
        "obj": obj,
        "abs_non_justifie": obj.abs_non_justifie,
        "mis_a_pied": obj.mis_a_pied,
        "conge": obj.conge,
        "maternite": obj.maternite,
        "maladie": obj.maladie,
        "autorise": obj.autorise,
        "autre": obj.autre,
        "autre_motif": obj.autre_motif,
    }
    return render(request, "Manager_KPI/absence_form.html", ctx)

# Liste historique des absences avec filtres et pagination basée sur les dates (2 jours/page).
def absence_list(request):
    # -- filtres --
    def parse_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    d_from  = parse_date(request.GET.get("from", "") or "")
    d_to    = parse_date(request.GET.get("to", "") or "")
    f_shift = request.GET.get("shift") or ""  # 'MATIN'|'SOIR'|'NUIT'

    flt = Q()
    if d_from:  flt &= Q(date__gte=d_from)
    if d_to:    flt &= Q(date__lte=d_to)
    if f_shift in ("MATIN", "SOIR", "NUIT"):
        flt &= Q(shift=f_shift)

    # Tous les enregistrements filtrés (triés)
    reports = (Absence.objects
               .select_related("sup")
               .filter(flt)
               .order_by("-date", "shift", "sup_id"))

    # Pagination par dates distinctes (2 jours/page)
    days_per_page = 2
    all_dates = sorted({r.date for r in reports}, reverse=True)
    date_paginator = Paginator(all_dates, days_per_page)
    page_obj = date_paginator.get_page(request.GET.get("page"))
    page_dates = set(page_obj.object_list)

    label_map = [
        ("abs_non_justifie", "Absent non justifié"),
        ("mis_a_pied",       "Mis à pied"),
        ("conge",            "Congé"),
        ("maternite",        "Maternité (MAT)"),
        ("maladie",          "Maladie"),
        ("autorise",         "Autorisé"),
        ("autre",            "Autre"),
    ]

    groups = []
    for rep in reports:
        if rep.date not in page_dates:
            continue

        types = [{"label": label, "qty": int(getattr(rep, field) or 0)}
                 for field, label in label_map]

        first = getattr(rep.sup, "prenom", "") or getattr(rep.sup, "first_name", "")
        last  = getattr(rep.sup, "nom", "")    or getattr(rep.sup, "last_name", "")
        sup_name = (f"{first} {last}".strip()) or getattr(rep.sup, "username", "") or str(rep.sup)

        wk = rep.date.isocalendar().week
        j  = rep.date.isoweekday()

        groups.append({
            "first": {
                "shift_report_id": rep.id,
                "date": rep.date,
                "wk_jx": f"WK{wk} – J{j}",
                "shift": rep.shift,
                "sup_name": sup_name,
                "effectif": rep.effectif,
                "total_shift": rep.total_absences,
                "taux_pct": (rep.total_absences / rep.effectif * 100.0) if rep.effectif else None,
            },
            "types": types,  # 7 lignes
        })

    # Conserver les filtres dans la pagination
    q = request.GET.copy()
    q.pop("page", None)
    qs_keep = q.urlencode()

    return render(request, "Manager_KPI/absence_list.html", {
        "groups": groups,     # liste des blocs à afficher
        "page_obj": page_obj, # pagination basée sur les dates
        "qs_keep": qs_keep,
    })

# Supprime une entrée d’absence (POST uniquement) puis revient à la liste en gardant les filtres.
@transaction.atomic
def absence_delete(request, pk):
    if request.method != "POST":
        messages.error(request, "Méthode non autorisée.")
        return redirect("absence_list")

    report = get_object_or_404(Absence, pk=pk)
    report.delete()
    messages.success(request, "Shift supprimé avec succès.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or ""
    if next_url.startswith("?"):
        return redirect(f"{reverse('absence_list')}{next_url}")
    return redirect("absence_list")
