from django import forms

from apps.base.models import Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Recipe
        fields = ["name", "ingredients", "description"]
