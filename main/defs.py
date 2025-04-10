import os
from dotenv import load_dotenv

# loading .env file from build/ directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(BASE_DIR, 'build', '.env')
load_dotenv(dotenv_path=dotenv_path)

# secrets from .env file
MOS_DATA_API_KEY = os.getenv('MOS_DATA_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
YANDEX_MAPS_API_KEY = os.getenv('YANDEX_MAPS_API_KEY')
YANDEX_DISK_API_KEY = os.getenv('YANDEX_DISK_API_KEY')

DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

VK_APP_ID = os.getenv('VK_APP_ID')
VK_APP_SECRET = os.getenv('VK_APP_SECRET')
VK_SERVICE_CLIENT_SECRET = os.getenv('VK_SERVICE_CLIENT_SECRET')


# constant URLs
VK_REDIRECT_URI = "http://localhost/vk/auth"
VK_OAUTH_URL = "https://id.vk.com/oauth2/auth"
VK_USER_INFO_URL = "https://id.vk.com/oauth2/user_info"

YANDEX_DISK_IMG_URL = "DineTinder/imgs"
