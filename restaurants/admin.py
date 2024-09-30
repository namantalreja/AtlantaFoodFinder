from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Favorite

# Register your model
admin.site.register(Favorite)

