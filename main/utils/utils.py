import json
import requests
from django.contrib.staticfiles import finders
from main.defs import VK_APP_ID, VK_OAUTH_URL, VK_REDIRECT_URI, VK_USER_INFO_URL

session = requests.Session()
session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})


def load_json_data(filename):
    """Загружает JSON-файл из статической папки"""
    file_path = finders.find(f"data/{filename}")
    if not file_path:
        raise FileNotFoundError(f"File {filename} not found in static directory.")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def refresh_vk_tokens(refresh_token, device_id):
    """Обновляет токены через VK OAuth"""
    try:
        response = session.post(
            VK_OAUTH_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": VK_APP_ID,
                "device_id": device_id,
                "scope": "vkid.personal_info email",
            },
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error refreshing VK tokens: {e}")
        return None


def get_vk_tokens(code, device_id, code_verifier):
    """Получает access_token, refresh_token и id_token по коду авторизации"""
    try:
        response = session.post(
            VK_OAUTH_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": VK_APP_ID,
                "code": code,
                "code_verifier": code_verifier,
                "device_id": device_id,
                "redirect_uri": VK_REDIRECT_URI,
            },
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting VK tokens: {e}")
        return None


def get_vk_user_info(access_token, refresh_token, device_id, retry=1):
    """Получает информацию о пользователе VK. Если токен истёк, пробует обновить его."""
    if retry > 1:
        return None  # Избегаем зацикливания

    try:
        response = session.post(
            VK_USER_INFO_URL,
            data={"client_id": VK_APP_ID, "access_token": access_token},
        )
        response.raise_for_status()
        return response.json().get("user")
    except requests.RequestException:
        # Если токен просрочен, пробуем обновить и перезапрашиваем
        refreshed_tokens = refresh_vk_tokens(refresh_token, device_id)
        if not refreshed_tokens:
            return None

        return get_vk_user_info(
            refreshed_tokens.get("access_token"),
            refreshed_tokens.get("refresh_token"),
            device_id,
            retry=retry + 1,
        )
