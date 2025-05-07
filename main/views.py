import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q, Case, When, Value

from main.accounts.models import User
from main.carousel.models import BlacklistCarousel, FavouriteCarousel, ShownCarousel
from main.places.models import DiningPlace
from main.utils import load_json_data, get_vk_tokens, get_vk_user_info, login_required_session, error_handling, \
    no_recommendation_error
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
def home_page(request):
    """Home page with VK ID processing"""
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    favourite_places = DiningPlace.objects.filter(
        favouritecarousel__user_id=user.id
    ).order_by('-favouritecarousel__added_at')[:3]
    blacklist_places = DiningPlace.objects.filter(
        blacklistcarousel__user_id=user.id
    ).order_by('-blacklistcarousel__added_at')[:3]

    context = {
        "user": user,
        'favourite_places': favourite_places,
        'blacklisted_places': blacklist_places,
    }

    return render(request, 'home.html', context)


@login_required_session
def account_page(request):
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    return render(request, 'account.html', {"user": user})


def faq_page(request):
    return render(request, 'faq.html')


@no_recommendation_error
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
    interested_place_ids = ShownCarousel.objects.filter(
        user_id=user.id
    ).filter(is_interested=True).values_list('place_id', flat=True)

    print(f'Blacklisted place IDs: {blacklisted_place_ids}')
    print(f'Favourite place IDs: {favourite_place_ids}')
    print(f'Shown place IDs: {shown_place_ids}')

    excluded_ids = blacklisted_place_ids.union(favourite_place_ids.union(shown_place_ids))
    print(f'Excluded place IDs: {excluded_ids}')

    if not favourite_place_ids:
        # if no favourite places, recommend the top one
        recommended_place = DiningPlace.objects.exclude(description='').exclude(rating=0).exclude(
            id__in=excluded_ids
        ).order_by('rating')[0]
    else:
        # Use vector search to find similar places
        new_places = DiningPlace.objects.exclude(description='').exclude(rating=0).exclude(
            id__in=excluded_ids
        ).order_by('rating').values_list('id', flat=True)

        # Limit each set to 20 items before combining
        limited_favourite_place_ids = list(favourite_place_ids)[:10]
        limited_interested_place_ids = list(interested_place_ids)[:10]
        limited_new_places = list(new_places)[:10]

        # Combine the limited sets
        combined_places = set(limited_favourite_place_ids + limited_interested_place_ids + limited_new_places)

        # Use the combined set in your vector search
        similar_place_ids = vector_search.get_similar_places(
            combined_places,
            top_k=10,
            exclude_ids=excluded_ids
        )

        # Get the actual place objects
        candidate_places = DiningPlace.objects.filter(id__in=similar_place_ids)
        print(candidate_places)

        if not candidate_places:
            print("No candidates")
            # Fallback if no similar places found
            recommended_places = DiningPlace.objects.exclude(description='').exclude(rating=0).exclude(
                id__in=excluded_ids
            ).order_by('rating')[:1]

            if recommended_places:
                print("Recommended places found")
                recommended_place = recommended_places[0]
                personalized_text = f"Это заведение похоже на твои избранные места. Оно может попасть в их список! Рекомендую"
            else:
                print("No recommended places found")
                # Handle case when no recommendations are available
                return render(request, "no_recommendations.html", {"user": user})
        else:
            print("Generated candidates")
            # Use LLM to select and describe the best match
            place_id, personalized_text = recommender.get_recommendation(
                DiningPlace.objects.filter(id__in=favourite_place_ids),
                candidate_places
            )

            recommended_place = DiningPlace.objects.get(id=place_id)

    print(f"Personalized recommendation: {recommended_place}")

    return render(request, "swipe.html", {"user": user, 'place': recommended_place})


@no_recommendation_error
@login_required_session
def get_recommendation_page(request):
    """Single recommendation page based on user favourite history"""
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    blacklisted_place_ids = list(BlacklistCarousel.objects.filter(
        user_id=user.id
    ).order_by("-added_at").values_list('place_id', flat=True))
    blacklisted_place_objects = DiningPlace.objects.filter(
        id__in=blacklisted_place_ids[:5]
    )

    # Get top 10 most recent favorites
    favourite_places = FavouriteCarousel.objects.filter(
        user_id=user.id
    ).order_by('-added_at')[:10]
    favorite_place_objects = [fp.place_id for fp in favourite_places]
    favourite_place_ids = [fp.id for fp in favorite_place_objects]

    shown_place_ids = list(ShownCarousel.objects.filter(
        user_id=user.id
    ).values_list('place_id', flat=True))

    if not favorite_place_objects:
        # No favorites yet, show a random recommendation
        print("No favourite places found")
        recommended_places = DiningPlace.objects.exclude(description='').exclude(rating=0).exclude(
            id__in=blacklisted_place_ids + shown_place_ids
        ).order_by('rating')[:1]

        if recommended_places:
            print("Recommended places found")
            recommended_place = recommended_places[0]
            personalized_text = f"Это заведение похоже на твои избранные места. Оно может попасть в их список! Рекомендую"
        else:
            # Handle case when no recommendations are available
            print("No recommended places found")
            return render(request, "no_recommendations.html", {"user": user})
    else:
        # Use vector search to find similar places
        print("Favourite places found")
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
            recommended_places = DiningPlace.objects.exclude(description='').exclude(rating=0).exclude(
                id__in=excluded_ids
            ).order_by('rating')[:1]

            if recommended_places:
                print("Recommended places found")
                recommended_place = recommended_places[0]
                personalized_text = f"Это заведение похоже на твои избранные места. Оно может попасть в их список! Рекомендую"
            else:
                print("No recommended places found")
                # Handle case when no recommendations are available
                return render(request, "no_recommendations.html", {"user": user})
        else:
            print("Generated candidates")
            # Use LLM to select and describe the best match
            place_id, personalized_text = recommender.get_recommendation(
                favorite_place_objects,
                candidate_places,
                blacklisted_place_objects
            )

            recommended_place = DiningPlace.objects.get(id=place_id)

    print(f"Personalized recommendation: {recommended_place}")
    # Mark the recommended place as shown
    ShownCarousel.objects.get_or_create(
        user_id=user,
        place_id=recommended_place
    )

    return render(request, "recommendation.html", {
        "user": user,
        'place': recommended_place,
        'personalized_description': personalized_text
    })


def error_page(request):
    """Error page"""
    return HttpResponse("ERROR")


@login_required_session
def history_page(request):
    return render(request, "history.html")


@login_required_session
def blacklist_page(request):
    return render(request, "blacklist.html")


@login_required_session
def no_recommendation_page(request):
    email = request.session["user_email"]
    user = User.objects.get(email=email)

    return render(request, "no_recommendation.html", {"user": user})


@login_required_session
def places_api(request):
    filter_type = request.GET.get('filter', 'favourite')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 8))

    email = request.session["user_email"]
    user = User.objects.get(email=email)

    offset = (page - 1) * limit

    if filter_type == 'favourite':
        place_relations = FavouriteCarousel.objects.filter(
            user_id=user.id
        ).order_by('-added_at').values('place_id', 'added_at')
    elif filter_type == 'interested':
        place_relations = ShownCarousel.objects.filter(
            user_id=user.id,
            is_interested=True
        ).order_by('-added_at').values('place_id', 'added_at')
    else:  # blacklist
        place_relations = BlacklistCarousel.objects.filter(
            user_id=user.id
        ).order_by('-added_at').values('place_id', 'added_at')

    # Extract place IDs while preserving order
    place_ids = [relation['place_id'] for relation in place_relations]

    # Use Case/When to preserve the order when fetching DiningPlace objects
    preserved_order = Case(
        *[When(id=pk, then=Value(i)) for i, pk in enumerate(place_ids)]
    )

    # Fetch places with preserved order
    places = DiningPlace.objects.filter(
        id__in=place_ids
    ).order_by(preserved_order)[offset:offset + limit + 1]

    # Check if there are more places
    has_more = places.count() > limit
    if has_more:
        places = places[:limit]  # Remove the extra item

    places_data = [{
        'id': place.id,
        'name': place.name,
        'photo_link': place.photo_link,
        'address': place.address,
        'category': place.category,
        'rating': place.rating
    } for place in places]

    return JsonResponse({
        'places': places_data,
        'has_more': has_more
    })


@login_required_session
def search_api(request):
    query = request.GET.get('query', '')
    limit = int(request.GET.get('limit', 8))

    places = DiningPlace.objects.exclude(description='').exclude(rating=0).filter(
        (Q(name__icontains=query) | Q(name__icontains=query.capitalize()) | Q(category__icontains=query))
    )[:8]  # Get one extra to check if there's more

    # Check if there are more places
    has_more = places.count() > limit
    if has_more:
        places = places[:limit]  # Remove the extra item

    places_data = [{
        'id': place.id,
        'name': place.name,
        'photo_link': place.photo_link,
        'address': place.address,
        'category': place.category,
        'rating': place.rating
    } for place in places]

    return JsonResponse({
        'places': places_data,
        'has_more': has_more
    })


def logout_page(request):
    request.session.flush()

    return HttpResponseRedirect("/")
