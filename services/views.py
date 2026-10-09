from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone

from services.forms import ServiceRequestForm, RequestCommentForm
from services.models import ServiceRequest, RequestComment, RequestHistory
from services.permissions import (
    is_it_staff,
    can_create_request,
    can_assign_technician,
    can_update_status,
    can_view_all_requests,
)


def _deny(request, text, target="request_list"):
    messages.error(request, text)
    return redirect(target)


@login_required(login_url="login")
def request_list(request):
    requests = ServiceRequest.objects.all().select_related(
        "category", "requester", "assignee"
    ).order_by("-created_at")

    if not can_view_all_requests(request.user):
        requests = requests.filter(requester=request.user)

    search_query = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "")
    priority_filter = request.GET.get("priority", "")

    if search_query:
        requests = requests.filter(subject__icontains=search_query)
    if status_filter:
        requests = requests.filter(status=status_filter)
    if priority_filter:
        requests = requests.filter(priority=priority_filter)

    return render(request, "services/request_list.html", {
        "requests": requests,
        "search_query": search_query,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
    })


@login_required(login_url="login")
def create_request(request):
    # Employee / admin only. IT staff cannot create requests.
    if not can_create_request(request.user):
        return _deny(request, "IT staff cannot create requests.")

    if request.method == "POST":
        form = ServiceRequestForm(request.POST)

        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.requester = request.user
            service_request.status = "New"
            service_request.save()

            RequestHistory.objects.create(
                request=service_request,
                actor=request.user,
                action="Request created",
                new_value="New",
            )

            messages.success(request, "Your service request was created successfully.")
            return redirect("request_list")
    else:
        form = ServiceRequestForm()

    return render(request, "services/create_request.html", {"form": form})


@login_required(login_url="login")
def request_detail(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    is_allowed = (
        service_request.requester_id == request.user.id
        or can_view_all_requests(request.user)
    )
    if not is_allowed:
        return _deny(request, "You are not allowed to view this request.")

    if request.method == "POST":
        form = RequestCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.request = service_request
            comment.author = request.user
            comment.save()

            messages.success(request, "Comment added successfully.")
            return redirect("request_detail", request_id=request_id)
    else:
        form = RequestCommentForm()

    comments = RequestComment.objects.filter(
        request=service_request
    ).select_related("author").order_by("created_at")

    technicians = []
    if can_assign_technician(request.user):
        technicians = User.objects.filter(
            groups__name="Technician", is_active=True
        ).distinct()

    return render(request, "services/request_detail.html", {
        "service_request": service_request,
        "comments": comments,
        "form": form,
        "technicians": technicians,
        "status_choices": ServiceRequest.STATUS_CHOICES,
    })


@login_required(login_url="login")
def update_request_status(request, request_id):
    # IT staff only. The admin/employee cannot change status.
    if not can_update_status(request.user):
        return _deny(
            request,
            "Only IT staff can update the request status.",
            target="request_list",
        )

    if request.method != "POST":
        return redirect("request_detail", request_id=request_id)

    service_request = get_object_or_404(ServiceRequest, id=request_id)
    new_status = request.POST.get("status")
    valid = [value for value, _ in ServiceRequest.STATUS_CHOICES]

    if new_status not in valid:
        messages.error(request, "Invalid request status.")
        return redirect("request_detail", request_id=request_id)

    old_status = service_request.status
    service_request.status = new_status
    fields = ["status"]

    if new_status == "Resolved":
        service_request.resolved_by = request.user
        service_request.resolved_at = timezone.now()
        fields += ["resolved_by", "resolved_at"]
    elif new_status == "Closed":
        service_request.closed_at = timezone.now()
        fields.append("closed_at")

    service_request.save(update_fields=fields)

    if old_status != new_status:
        RequestHistory.objects.create(
            request=service_request,
            actor=request.user,
            action="Status changed",
            old_value=old_status,
            new_value=new_status,
        )

    messages.success(request, "Request status updated successfully.")
    return redirect("request_detail", request_id=request_id)


@login_required(login_url="login")
def dashboard(request):
    if can_view_all_requests(request.user):
        requests = ServiceRequest.objects.all()
    else:
        requests = ServiceRequest.objects.filter(requester=request.user)

    return render(request, "services/dashboard.html", {
        "total_requests": requests.count(),
        "new_requests": requests.filter(status="New").count(),
        "in_progress_requests": requests.filter(status="In Progress").count(),
        "resolved_requests": requests.filter(status="Resolved").count(),
        "overdue_requests": sum(1 for item in requests if item.is_sla_overdue),
    })


@login_required(login_url="login")
def assign_technician(request, request_id):
    # IT staff only. The admin/employee cannot assign technicians.
    if not can_assign_technician(request.user):
        return _deny(request, "Only IT staff can assign technicians.")

    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        technician = get_object_or_404(
            User,
            id=request.POST.get("assignee"),
            is_active=True,
            groups__name="Technician",
        )

        old_assignee = service_request.assignee
        old_status = service_request.status

        service_request.assignee = technician
        # Assigning a brand-new request moves it to "Assigned";
        # otherwise IT staff keep control of the status.
        if old_status == "New":
            service_request.status = "Assigned"
        service_request.save(update_fields=["assignee", "status"])

        RequestHistory.objects.create(
            request=service_request,
            actor=request.user,
            action="Technician assigned",
            old_value=old_assignee.username if old_assignee else "",
            new_value=technician.username,
        )

        messages.success(request, "Technician assigned successfully.")

    return redirect("request_detail", request_id=request_id)
