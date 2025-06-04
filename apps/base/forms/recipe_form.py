from django import forms

from apps.base.models import Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    new_ingredients = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        required=False,
        help_text="Введіть нові інгредієнти через кому (якщо потрібно)",
    )

    class Meta:
        model = Recipe
        fields = ["name", "ingredients", "new_ingredients", "description"]

    def save(self, commit=True):
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
