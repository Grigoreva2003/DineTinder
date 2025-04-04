import requests
from main.defs import YANDEX_MAPS_API_KEY


try:
    response = requests.get("http://127.0.0.1:80/places/")
    response.raise_for_status()
    places_data = response.json().get("places", [])
    print(f"Fetched {len(places_data)} places from API.")
except requests.RequestException as e:
    print(f"API request failed: {e}")
    places_data = []

for row in places_data:
    name, category, address = row.get("name"), row.get("category"), row.get("address")
    if name != "White Rabbit":
        continue

    maps_url = 'https://search-maps.yandex.ru/v1/'
    params = {
        'apikey': YANDEX_MAPS_API_KEY,
        'text': ' '.join([name, category, address]),
        'lang': 'ru_RU',
        'type': 'biz',
    }
    print(params)

    response = requests.get(maps_url, params=params)
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.status_code)
    break