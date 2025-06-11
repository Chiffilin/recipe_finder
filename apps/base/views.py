from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
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


# Допоміжна функція для фільтрації за кількістю інгредієнтів
# Ця функція тепер ТІЛЬКИ фільтрує, але не анотує сама.
# Вона очікує, що 'num_ingredients' вже анотований, якщо 'max_ingredients_str' є.
def filter_by_ingredient_count_logic(recipes_queryset, max_ingredients_str):
    """Застосовує логіку фільтрації кверісету за максимальною кількістю інгредієнтів.
    Приймає кверісет, який вже має бути анотований 'num_ingredients' (якщо 'max_ingredients_str' є).
    Повертає відфільтрований кверісет.
    """
    if max_ingredients_str and max_ingredients_str.isdigit():
        try:
            max_ingredients_int = int(max_ingredients_str)
            # Фільтруємо за анотованим полем
            recipes_queryset = recipes_queryset.filter(num_ingredients__lte=max_ingredients_int)
        except ValueError:
            # Якщо max_ingredients_str не є числом (хоча HTML-input type="number" має запобігати цьому),
            # ми просто ігноруємо цей фільтр.
            pass
    return recipes_queryset


def find_recipes(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q")
    max_ingredients = request.GET.get("max_ingredients")
    sort_by = request.GET.get("sort_by")

    # 1. Починаємо з усіх рецептів
    recipes = Recipe.objects.all()

    # 2. Визначаємо, чи потрібно анотувати кількість інгредієнтів
    # Це необхідно, якщо користувач хоче фільтрувати за кількістю АБО сортувати за нею.
    needs_ingredient_count_annotation = False
    if max_ingredients and max_ingredients.isdigit():
        needs_ingredient_count_annotation = True
    if sort_by in ["ingredients_asc", "ingredients_desc"]:
        needs_ingredient_count_annotation = True

    if needs_ingredient_count_annotation:
        # Анотуємо кожен рецепт кількістю пов'язаних інгредієнтів.
        # Це створює тимчасове поле 'num_ingredients' для кожного рецепта в QuerySet.
        recipes = recipes.annotate(num_ingredients=Count("ingredients"))

    # 3. Застосування фільтрації за кількістю інгредієнтів
    # Ця функція тепер очікує, що 'num_ingredients' вже анотований, якщо 'max_ingredients' є.
    recipes = filter_by_ingredient_count_logic(recipes, max_ingredients)

    # 4. Застосування текстового пошуку (за назвою або інгредієнтами)
    if query:
        search_terms = [term.strip() for term in query.split(",") if term.strip()]
        if search_terms:
            complex_query = Q()
            for term in search_terms:
                # Пошук за назвою рецепта АБО за назвою інгредієнта
                complex_query |= Q(name__icontains=term) | Q(ingredients__name__icontains=term)
            recipes = recipes.filter(complex_query)
        else:
            # Якщо пошуковий запит складається лише з пробілів/ком, повертаємо порожній результат.
            # Якщо ви хочете показувати всі рецепти у цьому випадку, змініть на `recipes = Recipe.objects.all()`
            recipes = Recipe.objects.none()

    # 5. Застосування сортування
    if sort_by:
        if sort_by == "name_asc":  # Сортування за назвою (А-Я)
            recipes = recipes.order_by("name")
        elif sort_by == "name_desc":  # Сортування за назвою (Я-А)
            recipes = recipes.order_by("-name")
        elif sort_by == "ingredients_asc":  # Сортування за кількістю інгредієнтів (від меншої до більшої)
            # 'num_ingredients' вже анотований, якщо сортування за кількістю обрано.
            recipes = recipes.order_by("num_ingredients")
        elif sort_by == "ingredients_desc":  # Сортування за кількістю інгредієнтів (від більшої до меншої)
            # 'num_ingredients' вже анотований, якщо сортування за кількістю обрано.
            recipes = recipes.order_by("-num_ingredients")

        # Додаємо сортування за PK як вторинне, щоб забезпечити стабільний порядок
        # для рецептів з однаковою назвою або кількістю інгредієнтів.
        # Це допомагає уникнути "стрибків" рецептів при однаковій первинній умові сортування.
        # `recipes.query.order_by` дозволяє додати PK до вже існуючих правил сортування.
        recipes = recipes.order_by(*recipes.query.order_by, "pk")

    # 6. Застосовуємо distinct в кінці для унікальності
    # Це важливо, оскільки JOIN з інгредієнтами може створити дублікати рецептів.
    # distinct() повинен бути після всіх фільтрацій та сортувань.
    recipes = recipes.distinct()

    # 7. Передача даних у шаблон
    return render(
        request,
        "base/recipe_list.html",
        {
            "recipes": recipes,
            "current_max_ingredients": max_ingredients,  # Передаємо поточне значення фільтра
            "current_query": query,  # Передаємо поточний пошуковий запит
            "current_sort_by": sort_by,  # Передаємо поточний вибір сортування
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
