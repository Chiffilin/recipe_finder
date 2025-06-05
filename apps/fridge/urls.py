from django.urls import path

from apps.fridge import views

app_name = "fridge"

urlpatterns = [
    path("", views.fridge_view, name="fridge"),
    path("add/", views.add_fridge_item, name="add_fridge_item"),
]
