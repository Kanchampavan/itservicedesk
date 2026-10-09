from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class SLAConfig(models.Model):
    PRIORITY_CHOICES = [
        ("Critical", "Critical"),
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        unique=True
    )
    hours = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.priority} - {self.hours} hours"


class ServiceRequest(models.Model):
    PRIORITY_CHOICES = [
        ("Critical", "Critical"),
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    STATUS_CHOICES = [
        ("New", "New"),
        ("Assigned", "Assigned"),
        ("In Progress", "In Progress"),
        ("On Hold", "On Hold"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_requests"
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="requests"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Medium",
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="New",
        db_index=True
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assigned_requests"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    resolution_details = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="resolved_requests"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    @property
    def sla_deadline(self):
        sla = SLAConfig.objects.filter(
            priority=self.priority
        ).first()

        if not sla:
            return None

        return self.created_at + timedelta(hours=sla.hours)

    @property
    def is_sla_overdue(self):
        if self.status in ["Resolved", "Closed"]:
            return False

        deadline = self.sla_deadline

        if deadline is None:
            return False

        return timezone.now() > deadline

    @property
    def sla_remaining(self):
        if self.status in ["Resolved", "Closed"]:
            return None

        deadline = self.sla_deadline

        if deadline is None:
            return None

        remaining = deadline - timezone.now()
        return remaining

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"REQ-{self.id}: {self.subject}"


class RequestComment(models.Model):
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="request_comments"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on REQ-{self.request_id}"


class RequestHistory(models.Model):
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="history"
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="request_history"
    )
    action = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"REQ-{self.request_id}: {self.action}"