from services.permissions import (
    is_it_staff, can_create_request, can_assign_technician, can_update_status,
)


def roles(request):
    user = request.user
    return {
        "is_it_staff": is_it_staff(user),
        "can_create_request": can_create_request(user),
        "can_assign_technician": can_assign_technician(user),
        "can_update_status": can_update_status(user),
    }
