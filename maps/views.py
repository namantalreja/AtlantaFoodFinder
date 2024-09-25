from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings


def show_map(request):
    return render(request, 'maps/map.html')


def fetch_restaurants(request):
    latitude = 33.7490  # Example: Atlanta, GA
    longitude = -84.3880
    radius = 5000  # Radius in meters
    api_key = 'AIzaSyB1GIVqhfRZSP9QalUq_B9T0efp69Z4NIA'  # Replace with your API key

    query = request.GET.get('query', '')  # Get the search query from request
    min_rating = float(request.GET.get('min_rating', 0))  # Get the minimum rating, default is 0

    # Base URL for the Google Places API
    base_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&radius={radius}"
        f"&type=restaurant"
        f"&key={api_key}"
    )

    # Add the query to the URL if present
    if query:
        base_url += f"&keyword={query}"

    # Collect all results
    all_results = []

    # Request the first page
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        all_results.extend([res for res in data.get('results', []) if res.get('rating', 0) >= min_rating])

        # Check if there's a next page token, and keep fetching until there are no more pages
        while 'next_page_token' in data:
            next_page_token = data['next_page_token']

            # The API requires a short delay before using the next_page_token
            import time
            time.sleep(2)

            # Request the next page using the next_page_token
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