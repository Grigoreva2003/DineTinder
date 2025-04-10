import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from main.accounts.models import User
from main.carousel.models import BlacklistCarousel, FavouriteCarousel, ShownCarousel
from main.places.models import DiningPlace
from main.utils import load_json_data, get_vk_tokens, get_vk_user_info, login_required_session
from main.places.views import PlaceListView, PlaceFilterView
from .vector_search import DiningPlaceVectorSearch
from .llm_recommender import GeminiRecommender

logger = logging.getLogger(__name__)


vector_search = DiningPlaceVectorSearch()
print(f"Successfully build index with {vector_search.build_index()} items")
recommender = GeminiRecommender()


def landing_page(request):
    """Landing page with dynamic data"""
    try:
        landing_data = load_json_data('landing.json')
    except FileNotFoundError as e:
        logger.error(f"Error loading landing.json: {e}")
        landing_data = {}

    return render(request, 'landing.html', {'landing_data': landing_data})


def vk_login_page(request):
    """Login page via VK ID SDK"""
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


# @login_required_session
# def get_recommendation_page(request):
#     """Single recommendation page based on user favourite history"""
#     email = request.session["user_email"]
#     user = User.objects.get(email=email)
#
#     blacklisted_place_ids = BlacklistCarousel.objects.filter(
#         user_id=user.id
#     ).values_list('place_id', flat=True)
#     favourite_place_ids = FavouriteCarousel.objects.filter(
#         user_id=user.id
#     ).values_list('place_id', flat=True)
#     shown_place_ids = ShownCarousel.objects.filter(
#         user_id=user.id
#     ).values_list('place_id', flat=True)
#
#     print(f'Blacklisted place IDs: {blacklisted_place_ids}')
#     print(f'Favourite place IDs: {favourite_place_ids}')
#     print(f'Shown place IDs: {shown_place_ids}')
#
#     excluded_recommendations = blacklisted_place_ids.union(favourite_place_ids)
#     print(f'Excluded place IDs: {excluded_recommendations}')
#
#     # Get places, excluding blacklisted ones
#     recommended_places = DiningPlace.objects.exclude(
#         id__in=excluded_recommendations
#     )[:10]  # Limit to 10 recommendations
#
#     return render(request, "recommendation.html", {"user": user, 'place': recommended_places[0]})


@login_required_session
def search_places_page(request):
    """Search places page with swipe mechanics"""
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
    )[:10]  # Limit to 10 recommendations
    print(recommended_places[0])
    return render(request, "swipe.html", {"user": user, 'place': recommended_places[0]})


@login_required_session
def get_recommendation_page(request):
    """Single recommendation page based on user favourite history"""
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    blacklisted_place_ids = list(BlacklistCarousel.objects.filter(
        user_id=user.id
    ).values_list('place_id', flat=True))

    # Get top 10 most recent favorites
    favourite_places = FavouriteCarousel.objects.filter(
        user_id=user.id
    ).order_by('-added_at')[:10]
    print(f'favourite_places: {favourite_places}')

    favorite_place_objects = [fp.place_id for fp in favourite_places]
    favourite_place_ids = [fp.id for fp in favorite_place_objects]

    shown_place_ids = list(ShownCarousel.objects.filter(
        user_id=user.id
    ).values_list('place_id', flat=True))

    if not favorite_place_objects:
        print("No favourite places found")
        # No favorites yet, show a random recommendation
        recommended_places = DiningPlace.objects.exclude(
            id__in=blacklisted_place_ids + shown_place_ids
        ).order_by('?')[:1]

        if recommended_places:
            print("Recommended places found")
            recommended_place = recommended_places[0]
            personalized_text = f"Try {recommended_place.name} - we think you might like it!"
        else:
            # Handle case when no recommendations are available
            print("No recommended places found")
            return HttpResponseRedirect("/error")
            # return render(request, "no_recommendations.html", {"user": user})
    else:
        print("Favourite places found")
        # Use vector search to find similar places
        excluded_ids = blacklisted_place_ids + shown_place_ids + favourite_place_ids
        print(f"Excluded IDs: {excluded_ids}")
        print(f"Favourite IDs: {favourite_place_ids}")

        similar_place_ids = vector_search.get_similar_places(
            favourite_place_ids,
            top_k=10,
            exclude_ids=excluded_ids
        )

        # Get the actual place objects
        candidate_places = DiningPlace.objects.filter(id__in=similar_place_ids)
        print(candidate_places)

        if not candidate_places:
            print("No candidates")
            # Fallback if no similar places found
            recommended_places = DiningPlace.objects.exclude(
                id__in=excluded_ids
            ).order_by('?')[:1]

            if recommended_places:
                print("Recommended places found")
                recommended_place = recommended_places[0]
                personalized_text = f"Try {recommended_place.name} - it's popular with our users!"
            else:
                print("No recommended places found")
                # Handle case when no recommendations are available
                return render(request, "no_recommendations.html", {"user": user})
        else:
            print("Generated candidates")
            # Use LLM to select and describe the best match
            place_id, personalized_text = recommender.get_recommendation(
                favorite_place_objects,
                candidate_places
            )

            recommended_place = DiningPlace.objects.get(id=place_id)

    print(f"Personalized recommendation: {recommended_place}")
    # Mark the recommended place as shown
    # ShownCarousel.objects.get_or_create(
    #     user_id=user,
    #     place_id=recommended_place
    # )

    return render(request, "recommendation.html", {
        "user": user,
        'place': recommended_place,
        'personalized_description': personalized_text
    })


def error_page(request):
    """Error page"""
    return HttpResponse("ERROR")
