import json
from datetime import date
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .export_service import generate_app_excel
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
                        procurement_program=line_data["procurement_program"],
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
                {"error": str(error)},
                status=500
            )

        return JsonResponse({
            "message": "PPMP submitted successfully.",
            "ppmp_id": ppmp.pk,
        }, status=201)

    form = PPMPForm(
        initial={
            "fiscal_year": timezone.now().year, 
            "submission_type": ProcurementProjectManagementPlan.SubmissionType.INDICATIVE
        }
    )

    context = {
        "form": form,
        "office_profile": request.user.office_profile,
        "mode_of_procurement": ModeOfProcurement.choices
    }

    return render(request, "ppmp/create-ppmp.html", context)


@office_required
def ppmp_create_final(request, id):
    # Pre-populate the PPMP create final form with data from an approved indicative PPMP
    indicative_ppmp = get_object_or_404(
        ProcurementProjectManagementPlan.objects.prefetch_related(
            "procurement_lines__line_entries__item"
        ),
        pk=id,
        submitted_by=request.user,
        submission_type=ProcurementProjectManagementPlan.SubmissionType.INDICATIVE,
        status=ProcurementProjectManagementPlan.Status.APPROVED
    )

    already_exists = ProcurementProjectManagementPlan.objects.filter(
        office_profile=indicative_ppmp.office_profile,
        fiscal_year=indicative_ppmp.fiscal_year,
        classification=indicative_ppmp.classification,
        submission_type=ProcurementProjectManagementPlan.SubmissionType.FINAL
    ).exists()

    if already_exists:
        return JsonResponse(
            {"error": "A final PPMP already exists for this classification and fiscal year."},
            status=400
        )
    
    existing_lines = indicative_ppmp.procurement_lines.prefetch_related(
        "line_entries__item__item_code__object_code"
    ).all()

    form = PPMPForm(
        initial={
            "fiscal_year": indicative_ppmp.fiscal_year,
            "classification": indicative_ppmp.classification,
            "source_of_funds": indicative_ppmp.source_of_funds,
            "ceiling": indicative_ppmp.ceiling,
            "submission_type": ProcurementProjectManagementPlan.SubmissionType.FINAL
        }
    )

    context = {
        "form": form,
        "office_profile": request.user.office_profile,
        "mode_of_procurement": ModeOfProcurement.choices,
        "existing_lines": existing_lines,
        "is_final": True,
        "indicative_ppmp": indicative_ppmp,
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


@login_required
def ppmp_edit(request, id):
    ppmp = get_object_or_404(
        ProcurementProjectManagementPlan.objects.select_related("office_profile"),
        pk=id
    )

    # Add guard rail to not allow admin aid to edit PPMPs
    if request.user.is_adminaid:
        return JsonResponse(
            {"error": "Only administrators are allowed to edit PPMPs."},
            status=403
        )

    if request.user.is_office:
        if ppmp.submission_type != ProcurementProjectManagementPlan.SubmissionType.INDICATIVE:
            return JsonResponse(
                {"error": "Office users can only edit indicative PPMPs."},
                status=403
            )
        
        if ppmp.submitted_by != request.user:
            return JsonResponse({"error": "Unauthorized."}, status=403)

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
                ppmp.status = ProcurementProjectManagementPlan.Status.PENDING  
                ppmp.remarks = ""                                               
                ppmp.reviewed_by = None                                         
                ppmp.reviewed_at = None
                ppmp.save()

                # Delete existing lines — entries cascade automatically
                ppmp.procurement_lines.all().delete()

                # Recreate lines and entries fresh
                for line_data in cleaned_lines:
                    line = ProcurementLine.objects.create(
                        ppmp=ppmp,
                        item_code=line_data["item_code"],
                        mode_of_procurement=line_data["mode_of_procurement"],
                        procurement_program=line_data["procurement_program"],
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

    # Check if APP exists and if APP matches the PPMP
    try:
        app = AnnualProcurementPlan.objects.get(
            fiscal_year=ppmp.fiscal_year,
            submission_type=ppmp.submission_type
        )
    except AnnualProcurementPlan.DoesNotExist:
        return JsonResponse(
            {
                "error": (
                    f"No { ppmp.get_submission_type_display() } APP exists for"
                    f"FY: { ppmp.fiscal_year }. Please create one before approving."
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


@any_admin_required
def ppmp_revise(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    ppmp = get_object_or_404(ProcurementProjectManagementPlan, pk=id)

    if ppmp.status != ProcurementProjectManagementPlan.Status.PENDING:
        return JsonResponse(
            {"error": "Only pending PPMPs can be returned for revision."},
            status=400
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    remarks = payload.get("remarks", "").strip()

    if not remarks:
        return JsonResponse(
            {"error": "Remarks are required when returning a PPMP for revision."},
            status=400
        )

    ppmp.status = ProcurementProjectManagementPlan.Status.FOR_REVISION
    ppmp.reviewed_by = request.user
    ppmp.reviewed_at = timezone.now()
    ppmp.remarks = remarks
    ppmp.save()

    return JsonResponse({
        "message": "PPMP returned for revision.",
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
        submission_type=ProcurementProjectManagementPlan.SubmissionType.INDICATIVE
    )

    return JsonResponse({
        "message": f"APP for FY: {fiscal_year} created successfully.",
        "app_id": app.pk,
    }, status=201)


@admin_required
def app_create_final(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    fiscal_year = get_default_fiscal_year()
    allowed_years = get_allowed_fiscal_years()

    if fiscal_year not in allowed_years:
        return JsonResponse(
            {"error": f"APP cannot be created for FY{fiscal_year} at this time."},
            status=400
        )

    # Final APP requires an existing indicative APP for the same year
    if not AnnualProcurementPlan.objects.filter(
        fiscal_year=fiscal_year,
        submission_type=AnnualProcurementPlan.SubmissionType.INDICATIVE
    ).exists():
        return JsonResponse(
            {
                "error": (
                    f"No Indicative APP exists for FY{fiscal_year}. "
                    "Please create an indicative APP first before creating a final APP."
                )
            },
            status=400
        )

    # Check a final APP doesn't already exist
    if AnnualProcurementPlan.objects.filter(
        fiscal_year=fiscal_year,
        submission_type=AnnualProcurementPlan.SubmissionType.FINAL
    ).exists():
        return JsonResponse(
            {"error": f"A final APP for FY{fiscal_year} already exists."},
            status=400
        )

    app = AnnualProcurementPlan.objects.create(
        fiscal_year=fiscal_year,
        submission_type=AnnualProcurementPlan.SubmissionType.FINAL,
        prepared_by=request.user,
    )

    return JsonResponse({
        "message": f"Final APP for FY{fiscal_year} created successfully.",
        "app_id": app.id,
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

@admin_required
def app_add_schedule(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    app = get_object_or_404(AnnualProcurementPlan, pk=id)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    advertisement_date = (payload.get("advertisement_date") or "").strip()
    submission_date = (payload.get("submission_date") or "").strip()
    notice_of_award_date = (payload.get("notice_of_award_date") or "").strip()
    contract_signing_date = (payload.get("contract_signing_date") or "").strip()

    # Parse only the dates that were provided
    def parse_optional_date(value, field_name):
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValidationError(f"{field_name}: Invalid date format. Use YYYY-MM-DD.")

    try:
        ad_date  = parse_optional_date(advertisement_date, "Advertisement date")
        sub_date = parse_optional_date(submission_date, "Submission date")
        noa_date = parse_optional_date(notice_of_award_date, "Notice of award date")
        cs_date  = parse_optional_date(contract_signing_date, "Contract signing date")
    except ValidationError as error:
        return JsonResponse({"error": error.message}, status=400)

    # Validate logical order only for dates that are provided
    provided_dates = [
        (ad_date, "Advertisement"),
        (sub_date, "Submission"),
        (noa_date, "Notice of Award"),
        (cs_date, "Contract Signing"),
    ]
    filled_dates = [(date, label) for date, label in provided_dates if date is not None]

    for i in range(1, len(filled_dates)):
        if filled_dates[i][0] <= filled_dates[i - 1][0]:
            return JsonResponse(
                {
                    "error": (
                        f"{filled_dates[i][1]} date must be after "
                        f"{filled_dates[i - 1][1]} date."
                    )
                },
                status=400
            )

    try:
        with transaction.atomic():
            app.app_entries.all().update(
                advertisement_date=ad_date,
                submission_date=sub_date,
                notice_of_award_date=noa_date,
                contract_signing_date=cs_date,
            )
    except Exception:
        return JsonResponse(
            {"error": "An error occurred while saving. Please try again."},
            status=500
        )

    return JsonResponse({
        "message": "Schedule updated successfully for all entries.",
        "app_id": app.id,
    }, status=200)


APP_TEMPLATE_PATH = str(settings.APP_TEMPLATE_PATH)

@login_required
def export_app_excel(request, id):
    """
    GET /ppmp/app/<pk>/export/
    Exports the APP as an .xlsx file using the official template.
    """

    app = get_object_or_404(
        AnnualProcurementPlan.objects.prefetch_related(
            "app_entries__ppmp__office_profile",
            "app_entries__ppmp__procurement_lines__item_code__object_code",
            "app_entries__ppmp__procurement_lines__line_entries__item",
        ),
        pk=id
    )

    # Fetch and serialize records from DB
    records = []

    for entry in app.app_entries.all():
        for line in entry.ppmp.procurement_lines.all():
            records.append({
                "code_pap": line.item_code.code,
                "program_project": line.procurement_program,
                "object_code": line.item_code.object_code.code,
                "pmo_end_user": entry.pmo_end_user,
                "mode_of_procurement": line.get_mode_of_procurement_display(),
                "advertisement_date": entry.advertisement_date,
                "submission_date": entry.submission_date,
                "notice_of_award_date": entry.notice_of_award_date,
                "contract_signing_date": entry.contract_signing_date,
                "source_of_funds": entry.source_of_funds,
                "total": float(entry.total),
                "mooe": float(entry.mooe),
                "co": float(entry.co),
                "remarks": entry.remarks or "",
            })

    # Populate template and get bytes
    excel_bytes = generate_app_excel(
        records=records,
        template_path=APP_TEMPLATE_PATH,
    )

    filename = f"APP_{app.get_submission_type_display()}_FY{app.fiscal_year}.xlsx"

    # Return as file download
    response = HttpResponse(
        content=excel_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response