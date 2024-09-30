from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from .models import Favorite

# View to add a restaurant to favorites
def add_favorite(request):
    if request.method == 'POST':
        user = request.user
        place_id = request.POST.get('place_id')
        restaurant_name = request.POST.get('restaurant_name')

        # Create a new favorite entry if it doesn't exist
        favorite, created = Favorite.objects.get_or_create(user=user, place_id=place_id, defaults={'restaurant_name': restaurant_name})
        if created:
            return JsonResponse({'message': 'Favorite added successfully!'}, status=201)
        return JsonResponse({'message': 'Already in favorites!'}, status=200)

# View to list a user's favorites
def list_favorites(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user)
    return JsonResponse({'favorites': [{'name': fav.restaurant_name, 'place_id': fav.place_id} for fav in favorites]})

