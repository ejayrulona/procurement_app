from datetime import date
from django.core.exceptions import ValidationError
from apps.inventory.models import Item, ItemCode
from .models import ModeOfProcurement

def parse_date(value, prefix):
    try:
        parsed = date.fromisoformat(value)

        if parsed < date.today():
            raise ValidationError(f"{prefix}: Date needed cannot be in the past.")
        return parsed
    except (ValueError, TypeError):
        raise ValidationError(f"{prefix}: Invalid date format. Use ")

def validate_procurement_lines(lines, ceiling):
    if not lines:
        raise ValidationError("At least one procurement line is required. Use mm/dd/yyyy.")

    valid_modes = [choice[0] for choice in ModeOfProcurement.choices]
    total = 0
    cleaned_lines = []

    for line_index, line in enumerate(lines, start=1):
        line_prefix = f"Line {line_index}"

        item_code_id = line.get("item_code_id")
        mode_of_procurement = line.get("mode_of_procurement")
        project_name = line.get("project_name", "").strip()
        entries = line.get("entries", [])

        if not item_code_id:
            raise ValidationError(f"{line_prefix}: Item code is required.")

        if not mode_of_procurement:
            raise ValidationError(f"{line_prefix}: Mode of procurement is required.")
        
        if mode_of_procurement not in valid_modes:
            raise ValidationError(f"{line_prefix}: Invalid mode of procurement.")
        
        if not project_name:
            raise ValidationError(f"{line_prefix}: Project name is required.")
        
        if len(project_name) > 200:
            raise ValidationError(f"{line_prefix}: Project name must not exceed 200 characters.")

        if not entries:
            raise ValidationError(f"{line_prefix}: At least one item entry is required.")

        try:
            item_code = ItemCode.objects.get(pk=item_code_id)
        except ItemCode.DoesNotExist:
            raise ValidationError(f"{line_prefix}: Invalid item code selected.")

        cleaned_entries = []

        for entry_index, entry in enumerate(entries, start=1):
            entry_prefix = f"{line_prefix} - Entry {entry_index}"

            item_id = entry.get("item_id")
            date_needed = entry.get("date_needed")
            remarks = entry.get("remarks", "").strip()

            if not item_id:
                raise ValidationError(f"{entry_prefix}: Item is required.")

            try:
                quantity = int(entry.get("quantity"))

                if quantity <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValidationError(f"{entry_prefix}: Quantity must be a positive integer and greater than zero.")

            if not date_needed:
                raise ValidationError(f"{entry_prefix}: Date needed is required.")
            
            parsed_date = parse_date(date_needed, entry_prefix)

            if len(remarks) > 500:
                raise ValidationError(f"{entry_prefix}: Remarks must not exceed 500 characters.")
            
            try:
                item = Item.objects.get(pk=item_id, item_code=item_code)
            except Item.DoesNotExist:
                raise ValidationError(
                    f"{entry_prefix}: Item does not belong to the selected item code."
                )

            unit_cost_snapshot = item.unit_cost
            entry_total = unit_cost_snapshot * int(quantity)
            total += entry_total

            cleaned_entries.append({
                "item": item,
                "quantity": int(quantity),
                "unit_cost_snapshot": unit_cost_snapshot,
                "date_needed": parsed_date,
                "remarks": entry.get("remarks", "").strip(),
            })

        cleaned_lines.append({
            "item_code": item_code,
            "mode_of_procurement": mode_of_procurement,
            "project_name": project_name,
            "order": line_index,
            "entries": cleaned_entries,
        })

    if total > ceiling:
        raise ValidationError(
            f"Total amount of ₱{total:,.2f} exceeds the ceiling of ₱{ceiling:,.2f}."
        )

    return cleaned_lines