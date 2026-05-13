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
from .models import AnnualProcurementPlan   
from . utils import get_allowed_fiscal_years, get_default_fiscal_year
from apps.ppmp.models import ProcurementProjectManagementPlan 
from apps.users.decorators import admin_required, any_admin_required, office_required

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

@any_admin_required
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