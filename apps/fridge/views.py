from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms.fridge_form import FridgeItemForm
from .models import FridgeItem


# @login_required
def fridge_view(request: HttpRequest) -> HttpResponse:
    items = FridgeItem.objects.filter(user=request.user)

    if request.method == "POST":
        form = FridgeItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect("fridge:fridge")
    else:
        form = FridgeItemForm()

    return render(
        request,
        "fridge/fridge_list.html",
        {
            "items": items,
            "form": form,
        },
    )


# @login_required
def add_fridge_item(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = FridgeItemForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("fridge:fridge")  # або куди потрібно
    else:
        form = FridgeItemForm(user=request.user)

    return render(request, "fridge/add_item.html", {"form": form})


@login_required
def update_fridge_item(request: HttpRequest, pk):
    item = get_object_or_404(FridgeItem, pk=pk, user=request.user)

    if request.method == "POST":
        form = FridgeItemForm(request.POST, instance=item, user=request.user)  # ✅ user тут
        if form.is_valid():
            form.save()  # ❌ не передаємо user тут
            return redirect("fridge:fridge")
    else:
        form = FridgeItemForm(instance=item, user=request.user)

    return render(request, "fridge/fridge_form.html", {"form": form, "title": "Оновити інгредієнт"})


@login_required
def delete_fridge_item(request: HttpRequest, pk) -> HttpResponse:
    item = get_object_or_404(FridgeItem, pk=pk, user=request.user)

    if request.method == "POST":
        item.delete()
        return redirect("fridge:fridge")

    return render(request, "fridge/fridge_item_confirm_delete.html", {"item": item})
