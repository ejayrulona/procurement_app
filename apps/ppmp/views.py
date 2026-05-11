import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import PPMPForm
from .models import (
    ProcurementProjectManagementPlan, ProcurementLine, ProcurementLineEntry, ModeOfProcurement,
    AnnualProcurementPlan, AnnualProcurementPlanEntry    
)
from . utils import get_allowed_fiscal_years, get_default_fiscal_year
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
                        project_name=line_data["project_name"],
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
                {"error": "An error occurred while saving. Please try again."},
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
        "mode_of_procurement": ModeOfProcurement.choices
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


@admin_required
def ppmp_edit(request, id):
    ppmp = get_object_or_404(
        ProcurementProjectManagementPlan.objects.select_related("office_profile"),
        pk=id
    )

    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
        
        form = PPMPForm(payload, instance=ppmp)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)
        
        ceiling = form.cleaned_data["ceiling"]
        raw_lines = payload.get("procurement_lines", [])

        try:
            cleaned_lines = validate_procurement_lines(raw_lines, ceiling)
        except ValidationError as error:
            return JsonResponse({"error": error.message}, status=400)
        
        try:
            with transaction.atomic():
                ppmp = form.save(commit=False)
                ppmp.save()

                # Delete existing lines — entries cascade automatically
                ppmp.procurement_lines.all().delete()

                # Recreate lines and entries fresh
                for line_data in cleaned_lines:
                    line = ProcurementLine.objects.create(
                        ppmp=ppmp,
                        item_code=line_data["item_code"],
                        mode_of_procurement=line_data["mode_of_procurement"],
                        project_name=line_data["project_name"],
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
                {"error": "An error occurred while saving. Please try again."},
                status=500
            )

        return JsonResponse({
            "message": "PPMP updated successfully.",
            "ppmp_id": ppmp.pk,
        }, status=200)

    existing_lines = ppmp.procurement_lines.prefetch_related(
        "line_entries__item__item_code__object_code"
    ).all()

    form = PPMPForm(instance=ppmp)

    context = {
        "form": form,
        "ppmp": ppmp,
        "office_profile": ppmp.office_profile,
        "mode_of_procurement": ModeOfProcurement.choices,
        "existing_lines": existing_lines,
    }

    return render(request, "ppmp/edit-ppmp.html", context)


@any_admin_required
def ppmp_approve(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    ppmp = get_object_or_404(ProcurementProjectManagementPlan, pk=id)

    if ppmp.status != ProcurementProjectManagementPlan.Status.PENDING:
        return JsonResponse(
            {"error": "Only pending PPMPs can be approved."},
            status=400
        )

    # Check APP exists for this fiscal year
    try:
        app = AnnualProcurementPlan.objects.get(fiscal_year=ppmp.fiscal_year)
    except AnnualProcurementPlan.DoesNotExist:
        return JsonResponse(
            {
                "error": (
                    f"No APP exists for FY: {ppmp.fiscal_year}. "
                    "Please create an APP for this fiscal year before approving PPMPs."
                )
            },
            status=400
        )

    try:
        with transaction.atomic():
            ppmp.status = ProcurementProjectManagementPlan.Status.APPROVED
            ppmp.reviewed_by = request.user
            ppmp.reviewed_at = timezone.now()
            ppmp.save()

            AnnualProcurementPlanEntry.objects.create(
                app=app,
                ppmp=ppmp,
            )

    except Exception:
        return JsonResponse(
            {"error": "An error occurred during approval."},
            status=500
        )

    return JsonResponse({
        "message": "PPMP approved and added to the Annual Procurement Plan.",
        "ppmp_id": ppmp.id,
        "app_id": app.id,
    }, status=200)


# could be revise_ppmp
@any_admin_required
def ppmp_decline(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    ppmp = get_object_or_404(
        ProcurementProjectManagementPlan, pk=id
    )

    if ppmp.status != ProcurementProjectManagementPlan.Status.PENDING:
        return JsonResponse(
            {"error": "Only pending PPMPs can be declined."},
            status=400
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    remarks = payload.get("remarks", "").strip()

    if not remarks:
        return JsonResponse(
            {"error": "Remarks are required when declining a PPMP."},
            status=400
        )

    ppmp.status = ProcurementProjectManagementPlan.Status.DECLINED
    ppmp.reviewed_by = request.user
    ppmp.reviewed_at = timezone.now()
    ppmp.remarks = remarks
    ppmp.save()

    return JsonResponse({
        "message": "PPMP declined.",
        "ppmp_id": ppmp.id,
    }, status=200)

@admin_required
def app_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    fiscal_year = get_default_fiscal_year()

    allowed_years = get_allowed_fiscal_years()
    if fiscal_year not in allowed_years:
        return JsonResponse(
            {"error": f"APP cannot be created for FY{fiscal_year} at this time."},
            status=400
        )

    if AnnualProcurementPlan.objects.filter(fiscal_year=fiscal_year).exists():
        return JsonResponse(
            {"error": f"An APP for FY: {fiscal_year} already exists."},
            status=400
        )

    app = AnnualProcurementPlan.objects.create(
        fiscal_year=fiscal_year,
        prepared_by=request.user,
    )

    return JsonResponse({
        "message": f"APP for FY: {fiscal_year} created successfully.",
        "app_id": app.pk,
    }, status=201)


@any_admin_required
def app_list(request):
    apps = AnnualProcurementPlan.objects.select_related(
        "prepared_by"
    ).prefetch_related(
        "app_entries"
    ).annotate(
        annotated_grand_total=Sum("app_entries__mooe") + Sum("app_entries__co"),
        annotated_grand_total_mooe=Sum("app_entries__mooe"),
        annotated_grand_total_co=Sum("app_entries__co"),
    ).all()

    context = {
        "apps": apps,
        "fiscal_year": get_default_fiscal_year
    }

    return render(request, "ppmp/app-list.html", context)


@any_admin_required
def app(request, id):
    app = get_object_or_404(
        AnnualProcurementPlan.objects.select_related(
            "prepared_by"
        ).prefetch_related(
            "app_entries",
            "app_entries__ppmp__office_profile",
            "app_entries__ppmp__procurement_lines__item_code__object_code",
            "app_entries__ppmp__procurement_lines__line_entries__item"
        ),
        pk=id
    )

    context = {
        "app": app
    }

    return render(request, "ppmp/app.html", context)