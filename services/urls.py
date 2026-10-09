
from django.urls import path
from services import views

urlpatterns = [
    path("", views.request_list, name="request_list"),
    path("create/", views.create_request, name="create_request"),
    path("request/<int:request_id>/", views.request_detail, name="request_detail"),
    path(
    "request/<int:request_id>/update-status/",
    views.update_request_status,
    name="update_request_status",
),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
    "requests/<int:request_id>/assign/",
    views.assign_technician,
    name="assign_technician"
),
]