from django import forms

from apps.base.models import Ingredient
from apps.fridge.models import FridgeItem  # або твоя назва додатку


class FridgeItemForm(forms.ModelForm):
    ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control select2"}),
        help_text="Оберіть існуючий інгредієнт або введіть новий нижче",
    )

    new_ingredient = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Наприклад: куряче філе",
            },
        ),
        help_text="Введіть новий інгредієнт, якщо його немає у списку",
    )

    class Meta:
        model = FridgeItem
        fields = ["ingredient", "new_ingredient", "quantity", "unit", "purchased_at", "expires_at"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": 0.01}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "purchased_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "expires_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # передамо користувача при ініціалізації
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        ingredient = cleaned_data.get("ingredient")
        new_ingredient = cleaned_data.get("new_ingredient")

        if not ingredient and not new_ingredient:
            raise forms.ValidationError("Оберіть існуючий або введіть новий інгредієнт.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        ingredient = self.cleaned_data.get("ingredient")
        new_ingredient = self.cleaned_data.get("new_ingredient")

        if not ingredient and new_ingredient:
            ingredient, _ = Ingredient.objects.get_or_create(name=new_ingredient.strip().lower())

        instance.ingredient = ingredient
        if self.user:
            instance.user = self.user

        if commit:
            instance.save()

        return instance
