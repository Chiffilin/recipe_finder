from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    # Можеш додати інші поля, наприклад avatar, preferred_units тощо

    def __str__(self):
        return self.username
