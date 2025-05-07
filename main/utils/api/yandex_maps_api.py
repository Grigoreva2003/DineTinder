import psycopg2
import requests

from main.defs import YANDEX_MAPS_API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

# try:
#     response = requests.get("http://127.0.0.1:80/places/")
#     response.raise_for_status()
#     places_data = response.json().get("places", [])
#     print(f"Fetched {len(places_data)} places from API.")
# except requests.RequestException as e:
#     print(f"API request failed: {e}")
#     places_data = []

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# uncomment if you want to iterate over all the dining_places database
cursor.execute(
    "SELECT id, name, category, address FROM dining_places WHERE description <> '' and rating <> 0 and url IS NULL")
places_data = cursor.fetchall()

for i, row in enumerate(places_data):
    # name, category, address = row.get("name"), row.get("category"), row.get("address")
    id, name, category, address = row
    # if name != "White Rabbit":
    #     continue

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
        url = response.json()['features'][0]['properties']['CompanyMetaData'].get('url', '')

        cursor.execute(
            "UPDATE dining_places SET url = %s WHERE id = %s",
            (url, id)
        )
        conn.commit()
    else:
        print(response.status_code)

    # if i == 3:
    #     break
