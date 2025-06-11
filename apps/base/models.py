from django.db import models
from django.urls import reverse


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)

    rating = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    protein = models.FloatField(blank=True, null=True)
    fat = models.FloatField(blank=True, null=True)
    carbohydrates = models.FloatField(blank=True, null=True)
    cuisine = models.CharField(max_length=100, blank=True, null=True)

    cooking_time = models.PositiveIntegerField(help_text="Час приготування в хвилинах", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # --- ДОДАЙТЕ ЦІ ПОЛЯ ---
    external_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    youtube_url = models.URLField(max_length=500, blank=True, null=True)

    # --- КІНЕЦЬ ДОДАВАННЯ ---
    def __str__(self) -> str:
        return self.name

    def get_edit_url(self) -> str:
        return reverse("base:edit_recipe", kwargs={"pk": self.pk})

    def get_delete_url(self) -> str:
        return reverse("base:delete_recipe", kwargs={"pk": self.pk})
