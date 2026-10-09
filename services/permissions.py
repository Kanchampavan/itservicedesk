"""Role rules for the IT Service Desk.

Employee / admin side : create requests only.
IT staff side (pavan, Technician group): update status + assign a technician.
"""


def is_it_staff(user):
    """IT staff = 'pavan' or anyone in the Technician group (never the admin)."""
    return (
        user.is_authenticated
        and not user.is_superuser
        and (
            user.username == "pavan"
            or user.groups.filter(name="Technician").exists()
        )
    )


def can_create_request(user):
    """Employees / admin can create requests. IT staff cannot."""
    return user.is_authenticated and not is_it_staff(user)


def can_assign_technician(user):
    """Only IT staff can assign technicians."""
    return is_it_staff(user)


def can_update_status(user):
    """Only IT staff can change the status."""
    return is_it_staff(user)


def can_view_all_requests(user):
    return user.is_authenticated and (user.is_superuser or is_it_staff(user))
