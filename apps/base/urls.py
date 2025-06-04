from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    # base:index
    path("", views.home, name="home"),
    path("recipe", views.recipe_list, name="recipe_list"),
    path("recipe/<int:pk>/", views.recipe_detail, name="recipe_detail"),  # ← новий маршрут
    path("find", views.find_recipes, name="find_recipes"),
    path("add/", views.add_recipe, name="add_recipe"),
    path("recipes/<int:pk>/delete/", views.delete_recipe, name="delete_recipe"),
    path("recipe/<int:pk>/edit/", views.update_recipe, name="update_recipe"),
]
