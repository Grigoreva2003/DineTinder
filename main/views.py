import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from main.accounts.models import User
from main.utils import load_json_data, get_vk_tokens, get_vk_user_info


logger = logging.getLogger(__name__)


def landing_page(request):
    """Landing page with dynamic data"""
    try:
        landing_data = load_json_data('landing.json')
    except FileNotFoundError as e:
        logger.error(f"Error loading landing.json: {e}")
        landing_data = {}

    return render(request, 'landing.html', {'landing_data': landing_data})


def login(request):
    """Login page"""
    return render(request, 'login.html')


def home(request):
    """Home page with VK ID processing"""
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

    user, created = User.objects.get_or_create(email=email, defaults={'name': name, 'sex': sex})
    if created:
        print(f"New user created: {name}, {sex}, {email}")
        logger.info(f"New user created: {name}, {sex}, {email}")
    else:
        print(f"User already exists: {name}, {sex}, {email}")
        logger.info(f"User already exists: {name}, {sex}, {email}")

    return render(request, "home.html", {"user": user})



def error_page(request):
    """Страница ошибки"""
    return HttpResponse("ERROR")
