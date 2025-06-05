from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.base.models import Ingredient
from core import settings

User = get_user_model()


class FridgeItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.CharField(max_length=20, default="шт")
    purchased_at = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    def is_expired(self) -> bool:
        return self.expires_at and self.expires_at < timezone.now().date()

    def __str__(self):
        return f"{self.ingredient.name} ({self.quantity} {self.unit})"
