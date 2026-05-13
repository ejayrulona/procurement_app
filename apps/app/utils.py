from django.utils import timezone

def get_allowed_fiscal_years():
    """
    Returns the fiscal years for which PPMP/APP creation is allowed.
    From October onwards, both current and next year are allowed.
    Before October, only the current year is allowed.
    """

    now = timezone.now()
    current_year = now.year
    current_month = now.month

    if current_month >= 10:  # October onwards — prep season begins
        return [current_year, current_year + 1]

    return [current_year]


def get_default_fiscal_year():
    """
    Returns the most appropriate fiscal year for a new submission.
    From October onwards, defaults to next year.
    """
    
    now = timezone.now()
    if now.month >= 10:
        return now.year + 1
    return now.year