from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models import FavouriteCarousel, ShownCarousel, BlacklistCarousel
from ..accounts.models import User
from ..places.models import DiningPlace
from ..utils import login_required_session


@require_POST
@login_required_session
def mark_favorite(request, place_id):
    """Mark a place as favorite (heart icon)"""
    user = User.objects.get(email=request.session["user_email"])
    place = DiningPlace.objects.get(id=place_id)

    try:
        favorite, created = FavouriteCarousel.objects.get_or_create(
            user_id=user,
            place_id=place
        )

        if not created:
            favorite.delete()
            is_favorite = False
            print("Removed from favorites")
        else:
            is_favorite = True
            print("Added to favorites")

        return JsonResponse({'success': True, 'is_favorite': is_favorite})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@login_required_session
def mark_blacklist(request, place_id):
    """Blacklist a place (broken heart/dislike)"""
    user = User.objects.get(email=request.session["user_email"])
    place = DiningPlace.objects.get(id=place_id)

    try:
        blacklist, created = BlacklistCarousel.objects.get_or_create(
            user_id=user,
            place_id=place
        )

        if not created:
            blacklist.delete()
            print("Removed from blacklist")
        else:
            print("Added to blacklist")

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@login_required_session
def mark_interested(request, place_id):
    """Mark a place as interesting (swipe right)"""
    user = User.objects.get(email=request.session["user_email"])
    place = DiningPlace.objects.get(id=place_id)

    try:
        shown, created = ShownCarousel.objects.get_or_create(
            user_id=user,
            place_id=place,
            defaults={'is_interested': True}
        )

        if not created:
            shown.is_interested = True
            shown.save()
        print("Interesting place")

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@login_required_session
def mark_not_interested(request, place_id):
    """Mark a place as not interesting (swipe left)"""
    user = User.objects.get(email=request.session["user_email"])
    place = DiningPlace.objects.get(id=place_id)

    try:
        shown, created = ShownCarousel.objects.get_or_create(
            user_id=user,
            place_id=place,
            defaults={'is_interested': False}
        )

        if not created:
            shown.is_interested = False
            shown.save()
        print("Not really nteresting place")

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




@require_GET
@login_required_session
def check_favorite(request, place_id):
    """Check if a place is favorited by the user"""
    user = User.objects.get(email=request.session["user_email"])
    place = DiningPlace.objects.get(id=place_id)

    is_favorite = FavouriteCarousel.objects.filter(
        user_id=user,
        place_id=place
    ).exists()
    print("Favourite checked")

    return JsonResponse({'is_favorite': is_favorite})


@require_POST
@login_required_session
def mark_shown(request, place_id):
    """Mark a place as shown to the user without interest status yet"""
    user = User.objects.get(email=request.session["user_email"])
    place = DiningPlace.objects.get(id=place_id)

    ShownCarousel.objects.get_or_create(
        user_id=user,
        place_id=place
    )
    print("Place was shown")

    return JsonResponse({'success': True})
