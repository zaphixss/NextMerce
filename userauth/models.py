from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    email = models.EmailField( unique=True)
    username = models.CharField( unique=True, blank=True, null=True, max_length=50)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'