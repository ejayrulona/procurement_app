from django.utils import timezone

def get_allowed_fiscal_years():
    """
    Returns the fiscal years for which PPMP/APP creation is allowed.
    Always allows current year and one year in advance.
    """

    current_year = timezone.now().year
    return [current_year, current_year + 1]


def get_default_fiscal_year():
    """
    Returns the current year as the default fiscal year.
    """

    return timezone.now().year


def is_ppmp_editable(ppmp, user):
    """
    A PPMP is editable until January 15 of the year after its fiscal year.
    After that it becomes read-only for all users.
    Role-based rules still apply within the editable period.
    """
    
    now = timezone.now()
    grace_deadline = timezone.datetime(ppmp.fiscal_year + 1, 1, 15, tzinfo=timezone.asia)

    if now > grace_deadline:
        return False

    if user.is_any_admin:
        return True

    if user.is_office:
        return ppmp.submission_type == ppmp.SubmissionType.INDICATIVE

    return False