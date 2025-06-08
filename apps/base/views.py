from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
        template_name="base/home.html",
    )


def home(request: HttpRequest) -> HttpResponse:
    return render(
        request=request,
        template_name="base/home.html",
    )


def recipe_list(request: HttpRequest) -> HttpResponse:
    # recipes = Recipe.objects.all()
    # return render(request, "base/recipe_list.html", {"recipes": recipes})
    query = request.GET.get("q", "")
    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(
        request,
        "base/recipe_list.html",
        {
            "recipes": recipes,
            "query": query,  # ← якщо захочеш виводити в шаблоні
        },
    )


def recipe_detail(request: HttpRequest, pk) -> HttpResponse:
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, "base/recipe_detail.html", {"recipe": recipe})


def find_recipes(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q")
    recipes = Recipe.objects.all()
    if query:
        recipes = recipes.filter(Q(name__icontains=query) | Q(ingredients__name__icontains=query)).distinct()
    return render(request, "base/recipe_list.html", {"recipes": recipes})


def add_recipe(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("base:recipe_list")  # або на іншу сторінку
    else:
        form = RecipeForm()

    return render(request, "base/add_recipe.html", {"form": form})


@login_required
def delete_recipe(request: HttpRequest, pk: int) -> HttpResponse:
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        recipe.delete()
        return redirect("base:recipe_list")

    return render(request, "base/confirm_delete.html", {"recipe": recipe})


def update_recipe(request: HttpRequest, pk: int) -> HttpResponse:
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect("base:recipe_list")  # або інша сторінка після оновлення
    else:
        form = RecipeForm(instance=recipe)

    return render(
        request,
        "base/update_recipe.html",
        {
            "form": form,
            "recipe": recipe,
        },
    )
