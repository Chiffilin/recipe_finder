from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.base.forms.recipe_form import RecipeForm
from apps.base.models import Recipe


def index(
    request: HttpRequest,
) -> HttpResponse:
    """Render the index page."""
    # return HttpResponse("Hello, world! This is the index page.")
    return render(
        request=request,
        template_name="base/index.html",
    )


def home(request: HttpRequest) -> HttpResponse:
    return render(
        request=request,
        template_name="base/home.html",
    )


def recipe_list(request: HttpRequest) -> HttpResponse:
    recipes = Recipe.objects.all()
    return render(request, "base/recipe_list.html", {"recipes": recipes})


def recipe_detail(request: HttpRequest, pk) -> HttpResponse:
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, "base/recipe_detail.html", {"recipe": recipe})


def find_recipes(request: HttpRequest) -> HttpResponse:
    recipes = None
    selected_ingredients = []

    if request.method == "POST":
        ingredients_text = request.POST.get("ingredients_text", "")
        # Розбиваємо за комами, прибираємо пробіли
        selected_ingredients = [i.strip().lower() for i in ingredients_text.split(",") if i.strip()]

        # Пошук рецептів, які містять хоча б один із введених інгредієнтів
        recipes = Recipe.objects.filter(ingredients__name__in=selected_ingredients).distinct()

    return render(
        request,
        "base/find_recipes.html",
        {
            "recipes": recipes,
            "selected": ", ".join(selected_ingredients),
        },
    )


def add_recipe(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("base:recipe_list")  # або на іншу сторінку
    else:
        form = RecipeForm()

    return render(request, "base/add_recipe.html", {"form": form})
