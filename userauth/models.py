from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    email = models.EmailField( unique=True)
    username = models.CharField( unique=True, blank=True, null=True, max_length=50)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='image', null=True, blank=True)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'