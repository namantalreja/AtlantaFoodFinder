from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # Import the User model for linking favorites to a user

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link favorite to a user
    place_id = models.CharField(max_length=255)  # Store Google Places or restaurant ID
    restaurant_name = models.CharField(max_length=255)  # Store restaurant name

    def __str__(self):
        return f'{self.user.username} - {self.restaurant_name}'