from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms.fridge_form import FridgeItemForm
from .models import FridgeItem


# @login_required
def fridge_view(request: HttpRequest) -> HttpResponse:
    items = FridgeItem.objects.filter(user=request.user)
    return render(request, "fridge/fridge_list.html", {"items": items})


# @login_required
def add_fridge_item(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = FridgeItemForm(request.POST)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.user = request.user
            fridge_item.save()
            return redirect("fridge:fridge")
    else:
        form = FridgeItemForm()

    return render(request, "fridge/fridge_form.html", {"form": form})
