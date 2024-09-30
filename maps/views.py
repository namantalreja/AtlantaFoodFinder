from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()
def show_map(request):
    return render(request, 'maps/map.html')

def restaurant_details(request, place_id):
    api_key = str(os.getenv('API_KEY'))  # Replace with your API key
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        restaurant = response.json().get('result', {})
        return render(request, 'maps/restaurant_details.html', {'restaurant': restaurant})
    else:
        return render(request, 'maps/restaurant_details.html', {'error': 'Failed to fetch restaurant details'})
def fetch_restaurants(request):
    latitude = 33.7490  # Example: Atlanta, GA
    longitude = -84.3880
    default_radius = 5000  # Default radius in meters (5 km)
    api_key = 'AIzaSyB1GIVqhfRZSP9QalUq_B9T0efp69Z4NIA'   # Replace with your API key

    query = request.GET.get('query', '')  # Get the search query from request
    min_rating = float(request.GET.get('min_rating', 0))  # Get the minimum rating, default is 0
    radius = int(request.GET.get('max_distance', default_radius))  # Get the maximum distance, default is 5000 meters

    # Limit the radius to Google's max of 50,000 meters
    if radius > 50000:
        radius = 50000

    # Base URL for the Google Places API
    base_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&radius={radius}"
        f"&type=restaurant"
        f"&key={api_key}"
    )

    if query:
        base_url += f"&keyword={query}"

    all_results = []

    # Request the first page
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        all_results.extend([res for res in data.get('results', []) if res.get('rating', 0) >= min_rating])

        # Handle pagination with next_page_token
        while 'next_page_token' in data:
            next_page_token = data['next_page_token']
            import time
            time.sleep(2)

            next_url = (
                f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                f"?pagetoken={next_page_token}"
                f"&key={api_key}"
            )
            response = requests.get(next_url)
            if response.status_code == 200:
                data = response.json()
                all_results.extend([res for res in data.get('results', []) if res.get('rating', 0) >= min_rating])
            else:
                break
    else:
        return JsonResponse({"error": "Failed to fetch data from Google Places API"}, status=500)

    return JsonResponse({'results': all_results})