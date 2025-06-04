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

    cooking_time = models.PositiveIntegerField(help_text="Час приготування в хвилинах", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def get_edit_url(self):
        return reverse("base:edit_recipe", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("base:delete_recipe", kwargs={"pk": self.pk})
