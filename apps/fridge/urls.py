from django.urls import path

from apps.fridge import views

app_name = "fridge"

urlpatterns = [
    path("", views.fridge_view, name="fridge"),
    path("add/", views.add_fridge_item, name="add_fridge_item"),
    path("<int:pk>/update/", views.update_fridge_item, name="update_fridge_item"),
    path("<int:pk>/delete/", views.delete_fridge_item, name="delete_fridge_item"),
]
