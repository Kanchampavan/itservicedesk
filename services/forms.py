
from django import forms
from services.models import *


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            "subject",
            "description",
            "category",
            "priority",
        ]

        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter a short request title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Explain your issue in detail",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "priority": forms.Select(attrs={
                "class": "form-select",
            }),
        }

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["subject", "description", "category", "priority"]
        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter a short request title"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Explain your issue in detail"
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
        }


class RequestCommentForm(forms.ModelForm):
    class Meta:
        model = RequestComment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write your comment here..."
            }),
        }
