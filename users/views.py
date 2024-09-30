from django.views import View
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView
from .forms import RegisterForm, LoginForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import FavoriteRestaurant, Profile  # Make sure Profile is imported here
from .forms import UpdateUserForm, UpdateProfileForm
import os
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.contrib.auth import login


def home(request):
    return render(request, 'users/home.html')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # Redirect to home page if a user is already logged in
        if request.user.is_authenticated:
            return redirect('users-home')
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after registration
            login(request, user)  # Log in the user after registration
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('users-home')
        else:
            messages.error(request, f'Error: {form.errors}')
        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Set session expiry to 0 seconds. It will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)
            # Force session updates to ensure the cookie gets modified
            self.request.session.modified = True

        return super(CustomLoginView, self).form_valid(form)


@login_required
def add_to_favorites(request, place_id):
    restaurant_name = request.GET.get('name')

    if not FavoriteRestaurant.objects.filter(user=request.user, restaurant_place_id=place_id).exists():
        FavoriteRestaurant.objects.create(
            user=request.user,
            restaurant_name=restaurant_name,
            restaurant_place_id=place_id,
        )

    return redirect('restaurant_details', place_id=place_id)


@login_required
def view_favorites(request):
    favorites = FavoriteRestaurant.objects.filter(user=request.user)
    return render(request, 'users/favorites.html', {'favorites': favorites})


@login_required
def profile(request):
    # Ensure the user has a profile, if not, create one
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully')
            return redirect('users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Your password has been changed successfully"
    success_url = reverse_lazy('users-home')


# Load environment variables from .env file
load_dotenv()


def show_map(request):
    return render(request, 'users/map.html')


def restaurant_details(request, place_id):
    api_key = os.getenv('API_KEY')
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        restaurant = response.json().get('result', {})
        return render(request, 'users/restaurant_details.html', {'restaurant': restaurant})
    else:
        return render(request, 'users/restaurant_details.html', {'error': 'Failed to fetch restaurant details'})


def fetch_restaurants(request):
    latitude = 33.7490  # Example: Atlanta, GA
    longitude = -84.3880
    default_radius = 5000  # Default radius in meters (5 km)
    api_key = os.getenv('API_KEY')

    query = request.GET.get('query', '')  # Get the search query from request
    min_rating = float(request.GET.get('min_rating', 0))  # Get the minimum rating, default is 0
    radius = int(request.GET.get('max_distance', default_radius))  # Get the maximum distance, default is 5000 meters

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

    # Request the first page of results
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
