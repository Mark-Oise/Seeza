from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.utils import timezone


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_display_name(self):
        return self.display_name

        
