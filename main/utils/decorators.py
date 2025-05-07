import logging
from functools import wraps
from django.shortcuts import redirect, render

logger = logging.getLogger(__name__)


def login_required_session(view_func):
    """Decorator to check if a user is logged in via session"""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("user_email"):
            logger.info("User not logged in")
            return redirect("/login/vk")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def error_handling(view_func):
    """Decorator to check if a user is logged in via session"""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            return redirect("/error/")

    return _wrapped_view


def no_recommendation_error(view_func):
    """Decorator to check if a user is logged in via session"""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            # return redirect('/no_recommendation/')
            return render(request, "recommendation.html", {
                # "user": user,
                # 'place': recommended_place,
                # 'personalized_description': personalized_text
            })

    return _wrapped_view
