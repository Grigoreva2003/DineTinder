import logging
from functools import wraps
from django.shortcuts import redirect

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
