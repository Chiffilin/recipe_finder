from django import forms

from apps.fridge.models import FridgeItem


class FridgeItemForm(forms.ModelForm):
    class Meta:
        model = FridgeItem
        fields = ["ingredient", "quantity", "unit", "purchased_at", "expires_at"]
        widgets = {
            "purchased_at": forms.DateInput(attrs={"type": "date"}),
            "expires_at": forms.DateInput(attrs={"type": "date"}),
        }
