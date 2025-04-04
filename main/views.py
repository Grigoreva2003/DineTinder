import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from main.accounts.models import User
from main.carousel.models import BlacklistCarousel, FavouriteCarousel, ShownCarousel
from main.places.models import DiningPlace
from main.utils import load_json_data, get_vk_tokens, get_vk_user_info, login_required_session
from main.places.views import PlaceListView, PlaceFilterView

logger = logging.getLogger(__name__)


def landing_page(request):
    """Landing page with dynamic data"""
    try:
        landing_data = load_json_data('landing.json')
    except FileNotFoundError as e:
        logger.error(f"Error loading landing.json: {e}")
        landing_data = {}

    return render(request, 'landing.html', {'landing_data': landing_data})


def vk_login_page(request):
    """Login page"""
    return render(request, 'vk_login.html')

def simple_login_page(request):
    """Login page"""
    return render(request, 'simple_login.html')

@login_required_session
def home_page(request):
    """Home page with VK ID processing"""
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    return render(request, "home.html", {"user": user})


def vk_authenticate(request):
    """VK ID SDK Authentication and User Registration"""
    code = request.GET.get('code')
    device_id = request.GET.get('device_id')
    code_verifier = request.COOKIES.get('code_verifier')

    if not code or not device_id or not code_verifier:
        logger.error("Required parameters (code, device_id, code_verifier) were not provided")
        return HttpResponseRedirect("/error")

    tokens = get_vk_tokens(code, device_id, code_verifier)
    if not tokens:
        logger.error(f"Error retrieving VK ID tokens (code={code}, device_id={device_id})")
        return HttpResponseRedirect("/error")

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    user_info = get_vk_user_info(access_token, refresh_token, device_id)
    if not user_info:
        logger.error(f"Error retrieving VK ID user data (access_token={access_token})")
        return HttpResponseRedirect("/error")

    name, sex, email = user_info.get('first_name'), user_info.get('sex'), user_info.get('email')
    sex = "женский" if sex == 1 else "мужской"

    user, created = User.objects.update_or_create(
        email=email,
        defaults={'name': name, 'sex': sex, 'access_token': access_token, 'refresh_token': refresh_token}
    )

    logger.info(f"User {'created' if created else 'updated'}: {user}")
    print(f"User {'created' if created else 'updated'}: {user}")

    request.session["user_email"] = user.email

    return HttpResponseRedirect("/home")


@login_required_session
def get_recommendation_page(request):
    """Home page with VK ID processing"""
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    blacklisted_place_ids = BlacklistCarousel.objects.filter(
        user_id=user.id
    ).values_list('place_id', flat=True)
    favourite_place_ids = FavouriteCarousel.objects.filter(
        user_id=user.id
    ).values_list('place_id', flat=True)
    shown_place_ids = ShownCarousel.objects.filter(
        user_id=user.id
    ).values_list('place_id', flat=True)

    print(f'Blacklisted place IDs: {blacklisted_place_ids}')
    print(f'Favourite place IDs: {favourite_place_ids}')
    print(f'Shown place IDs: {shown_place_ids}')

    excluded_recommendations = blacklisted_place_ids.union(favourite_place_ids.union(shown_place_ids))
    print(f'Excluded place IDs: {excluded_recommendations}')

    # Get places, excluding blacklisted ones
    recommended_places = DiningPlace.objects.exclude(
        id__in=excluded_recommendations
    )[:5]  # Limit to 5 recommendations
    print(recommended_places)

    return render(request, "recommendation.html", {"user": user, 'place': recommended_places[0]})


@login_required_session
def search_places_page(request):
    """Home page with VK ID processing"""
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    return render(request, "swipe.html", {"user": user})

def error_page(request):
    """Страница ошибки"""
    return HttpResponse("ERROR")
