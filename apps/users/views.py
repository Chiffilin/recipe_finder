from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.users.forms.register_form import UserCreationFormCustom


def register(request: HttpRequest) -> HttpResponse:
    form = UserCreationFormCustom(request.POST or None)
    if form.is_valid():
        form.save()

        # Auto-login after registration
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        login(request, user)

        return redirect(reverse_lazy("base:index"))
    return render(request, "users/register.html", {"form": form})
