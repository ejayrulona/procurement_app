import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import PPMPForm
from .models import ProcurementProjectManagementPlan, ProcurementLine, ProcurementLineEntry
from .validators import validate_procurement_lines
from apps.users.decorators import admin_required, any_admin_required, office_required

@office_required
def ppmp_create(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        form = PPMPForm(payload)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        ceiling = form.cleaned_data["ceiling"]
        raw_lines = payload.get("procurement_lines", [])

        try:
            cleaned_lines = validate_procurement_lines(raw_lines, ceiling)
        except ValidationError as error:
            return JsonResponse({"error": error.message}, status=400)

        try:
            office_profile = request.user.office_profile
        except request.user.office_profile.RelatedObjectDoesNotExist:
            return JsonResponse(
                {"error": "Office profile not found. Please complete your profile."},
                status=400
            )

        try:
            with transaction.atomic():
                ppmp = form.save(commit=False)
                ppmp.office_profile = office_profile
                ppmp.submitted_by = request.user
                ppmp.status = ProcurementProjectManagementPlan.Status.PENDING
                ppmp.save()

                for line_data in cleaned_lines:
                    line = ProcurementLine.objects.create(
                        ppmp=ppmp,
                        item_code=line_data["item_code"],
                        mode_of_procurement=line_data["mode_of_procurement"],
                        order=line_data["order"],
                    )

                    ProcurementLineEntry.objects.bulk_create([
                        ProcurementLineEntry(
                            procurement_line=line,
                            item=entry["item"],
                            quantity=entry["quantity"],
                            unit_cost_snapshot=entry["unit_cost_snapshot"],
                            date_needed=entry["date_needed"],
                            remarks=entry["remarks"],
                        )
                        for entry in line_data["entries"]
                    ])

        except Exception as error:
            return JsonResponse(
                {"error": error},
                status=500
            )

        return JsonResponse({
            "message": "PPMP submitted successfully.",
            "ppmp_id": ppmp.pk,
        }, status=201)

    form = PPMPForm(initial={"fiscal_year": timezone.now().year})

    context = {
        "form": form,
        "office_profile": request.user.office_profile,
    }

    return render(request, "ppmp/create-ppmp.html", context)


@login_required
def ppmp(request, id):
    ppmp = get_object_or_404(
        ProcurementProjectManagementPlan.objects.select_related(
            "office_profile",
            "submitted_by",
            "reviewed_by"
        ).prefetch_related(
            "procurement_lines",
            "procurement_lines__item_code",
            "procurement_lines__line_entries__item"
        ), pk=id
    )

    # Guard - users can only view their ppmp
    if not request.user.is_any_admin and ppmp.submitted_by != request.user:
        return redirect("ppmp:ppmps")

    context = {
        "ppmp": ppmp
    }

    return render(request, "ppmp/ppmp.html", context)


@login_required
def ppmps(request):
    if request.user.is_any_admin:
        ppmps = ProcurementProjectManagementPlan.objects.all().select_related(
            "office_profile"
        ).prefetch_related(
            "procurement_lines__item_code",
            "procurement_lines__line_entries__item"
        )
    else:
        ppmps = ProcurementProjectManagementPlan.objects.filter(
            submitted_by=request.user
        ).select_related(
            "office_profile"
        ).prefetch_related(
            "procurement_lines__item_code",
            "procurement_lines__line_entries__item"
        )

    context = {
        "ppmps": ppmps
    }

    return render(request, "ppmp/ppmps.html", context)


def approve_ppmp(request):
    pass


# could be revise_ppmp
def decline_ppmp(request):
    pass


def app_list(request):
    return render(request, "ppmp/app-list.html")


def app(request):
    return render(request, "ppmp/app.html")

def create_ppmp(request):
    return render(request, "ppmp/create-ppmp.html")

def edit_ppmp(request):
    return render(request, "ppmp/edit-ppmp.html")
