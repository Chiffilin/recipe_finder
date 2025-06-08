from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.base.urls")),
    path("fridge/", include("apps.fridge.urls")),
    path("users/", include("apps.users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]
