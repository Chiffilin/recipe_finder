import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.base.forms.recipe_form import RecipeForm
from apps.base.models import Ingredient, Recipe


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


THEMEALDB_API_BASE_URL = "https://www.themealdb.com/api/json/v1/1/"


@login_required  # Дозволяє доступ лише авторизованим користувачам
def import_recipes_from_api(request: HttpRequest) -> HttpResponse:
    """Імпортує рецепти з TheMealDB API за введеною назвою.
    Ця функція доступна за окремим URL для авторизованих користувачів-персоналу.
    """
    if not request.user.is_staff:
        messages.error(request, "У вас немає дозволу на виконання цієї операції.")
        return redirect("base:recipe_list")

    search_term = ""  # Зберігаємо останній пошуковий термін для відображення у формі

    if request.method == "POST":
        search_term = request.POST.get("search_term", "").strip()

        if not search_term:
            messages.error(request, "Будь ласка, введіть назву рецепту для пошуку.")
            # Повертаємося до форми з повідомленням про помилку
            return render(request, "base/import_recipes_form.html", {"current_search_term": search_term})

        imported_count = 0
        skipped_count = 0
        errors = []

        try:
            # Змінено ендпоінт на search.php?s=
            # Важливо: використовуємо f-рядок для безпечного включення search_term
            response = requests.get(f"{THEMEALDB_API_BASE_URL}search.php?s={search_term}", timeout=10)
            response.raise_for_status()  # Підніме HTTPError для поганих відповідей

            data = response.json()
            meals = data.get("meals")

            if not meals:
                messages.info(request, f"Рецептів за запитом '{search_term}' не знайдено в TheMealDB.")
                # Повертаємося до форми з повідомленням
                return render(request, "base/import_recipes_form.html", {"current_search_term": search_term})

            for meal_data in meals:  # TheMealDB може повернути кілька рецептів
                try:
                    meal_id = meal_data.get("idMeal")

                    # Перевіряємо, чи рецепт вже існує за external_id
                    if Recipe.objects.filter(external_id=meal_id).exists():
                        skipped_count += 1
                        continue

                    with transaction.atomic():
                        recipe_name = meal_data.get("strMeal")
                        recipe_instructions = meal_data.get("strInstructions")
                        recipe_image_url = meal_data.get("strMealThumb")
                        recipe_category_name = meal_data.get("strCategory")
                        recipe_cuisine_name = meal_data.get("strArea")
                        recipe_youtube_url = meal_data.get("strYoutube")
                        cooking_time = 30  # Default if not available

                        # Створюємо Recipe, використовуючи CharField для category та cuisine
                        recipe = Recipe.objects.create(
                            name=recipe_name,
                            description=recipe_instructions[:1000] if recipe_instructions else "",
                            instructions=recipe_instructions,
                            cooking_time=cooking_time,
                            image_url=recipe_image_url,
                            youtube_url=recipe_youtube_url,
                            external_id=meal_id,
                            category=recipe_category_name,
                            cuisine=recipe_cuisine_name,
                        )

                        for i in range(1, 21):
                            ingredient_name = meal_data.get(f"strIngredient{i}")
                            # ingredient_measure = meal_data.get(f"strMeasure{i}") # Якщо потрібні мірки

                            if (
                                ingredient_name
                                and ingredient_name.strip()
                                and ingredient_name.strip().lower() != "null"
                            ):
                                ingredient_obj, created = Ingredient.objects.get_or_create(name=ingredient_name.strip())
                                recipe.ingredients.add(ingredient_obj)

                    imported_count += 1

                except Exception as e:
                    errors.append(f"Неочікувана помилка при обробці рецепту з ID {meal_id}: {e}")

        except requests.exceptions.Timeout:
            messages.error(request, "Запит до TheMealDB API перевищив час очікування. Спробуйте ще раз.")
        except requests.exceptions.ConnectionError:
            messages.error(request, "Не вдалося встановити з'єднання з TheMealDB API. Перевірте інтернет-з'єднання.")
        except requests.exceptions.HTTPError as e:
            messages.error(
                request,
                f"Помилка HTTP від TheMealDB API: {e.response.status_code} - {e.response.reason}. Можливо, API повернув помилку для запиту.",
            )
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Загальна помилка при запиті до TheMealDB API: {e}")
        except Exception as e:
            messages.error(request, f"Критична помилка під час імпорту: {e}")

        # Після імпорту, збираємо повідомлення
        if imported_count > 0:
            messages.success(request, f"Успішно імпортовано {imported_count} рецептів за запитом '{search_term}'.")
        if skipped_count > 0:
            messages.info(request, f"Пропущено {skipped_count} рецептів (вже існують) за запитом '{search_term}'.")
        if errors:
            for error_msg in errors:
                messages.error(request, f"Помилка імпорту: {error_msg}")

        # Після обробки POST-запиту, рендеримо форму з оновленими повідомленнями
        return render(request, "base/import_recipes_form.html", {"current_search_term": search_term})

    # Якщо це GET-запит, рендеримо шаблон з формою
    context = {"current_search_term": search_term}
    return render(request, "base/import_recipes_form.html", context)
