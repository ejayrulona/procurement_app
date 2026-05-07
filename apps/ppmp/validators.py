from django.core.exceptions import ValidationError
from apps.inventory.models import Item, ItemCode


def validate_procurement_lines(lines, ceiling):
    if not lines:
        raise ValidationError("At least one procurement line is required.")

    total = 0
    cleaned_lines = []

    for line_index, line in enumerate(lines, start=1):
        line_prefix = f"Line {line_index}"

        item_code_id = line.get("item_code_id")
        mode_of_procurement = line.get("mode_of_procurement")
        entries = line.get("entries", [])

        if not item_code_id:
            raise ValidationError(f"{line_prefix}: Item code is required.")

        if not mode_of_procurement:
            raise ValidationError(f"{line_prefix}: Mode of procurement is required.")

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
            quantity = entry.get("quantity")
            date_needed = entry.get("date_needed")

            if not item_id:
                raise ValidationError(f"{entry_prefix}: Item is required.")

            if not quantity or int(quantity) <= 0:
                raise ValidationError(f"{entry_prefix}: Quantity must be greater than zero.")

            if not date_needed:
                raise ValidationError(f"{entry_prefix}: Date needed is required.")

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
                "date_needed": date_needed,
                "remarks": entry.get("remarks", "").strip(),
            })

        cleaned_lines.append({
            "item_code": item_code,
            "mode_of_procurement": mode_of_procurement,
            "order": line_index,
            "entries": cleaned_entries,
        })

    if total > ceiling:
        raise ValidationError(
            f"Total amount of ₱{total:,.2f} exceeds the ceiling of ₱{ceiling:,.2f}."
        )

    return cleaned_lines