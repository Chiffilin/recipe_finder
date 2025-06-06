from django import forms

from apps.base.models import Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "select2 form-control"}),
        required=False,
    )
    new_ingredients = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "class": "form-control",
                "placeholder": "Наприклад: часник, петрушка",
            }
        ),
        required=False,
        help_text="Введіть нові інгредієнти через кому (якщо потрібно)",
    )

    class Meta:
        model = Recipe
        fields = [
            "name",
            "ingredients",
            "new_ingredients",
            "description",
            "cooking_time",
            "calories",
            "protein",
            "fat",
            "carbohydrates",
            "rating",
            "cuisine",
            "category",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "cooking_time": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "calories": forms.NumberInput(attrs={"class": "form-control", "step": 1}),
            "protein": forms.NumberInput(attrs={"class": "form-control", "step": 0.1}),
            "fat": forms.NumberInput(attrs={"class": "form-control", "step": 0.1}),
            "carbohydrates": forms.NumberInput(attrs={"class": "form-control", "step": 0.1}),
            "rating": forms.NumberInput(attrs={"class": "form-control", "step": 0.1, "min": 0, "max": 5}),
            "cuisine": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get("class"):
                field.widget.attrs["class"] = "form-control"

    def save(self, commit=True) -> Recipe:
        recipe = super().save(commit=False)

        if commit:
            recipe.save()
            self.save_m2m()

            new_ingredients_text = self.cleaned_data.get("new_ingredients", "")
            if new_ingredients_text:
                names = [name.strip().lower() for name in new_ingredients_text.split(",") if name.strip()]
                for name in names:
                    ingredient, _ = Ingredient.objects.get_or_create(name=name)
                    recipe.ingredients.add(ingredient)

        return recipe
