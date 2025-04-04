import psycopg2
import requests
from main.defs import YANDEX_DISK_IMG_URL, YANDEX_DISK_API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# # uncomment if you want to iterate over all the dining_places database
# cursor.execute("SELECT id, photo_link FROM dining_places WHERE photo_link IS NOT NULL AND photo_link <> ''")
# places_data = cursor.fetchall()

upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
get_info_url = "https://cloud-api.yandex.net/v1/disk/resources"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {YANDEX_DISK_API_KEY}',
}

# iteration only over top selected places
try:
    response = requests.get("http://127.0.0.1:80/places/")
    response.raise_for_status()
    places_data = response.json().get("places", [])
    print(f"Fetched {len(places_data)} places from API.")
except requests.RequestException as e:
    print(f"API request failed: {e}")
    places_data = []

for row in places_data:
    # # uncomment if want to iterate over all the dining_places database
    # place_id, photo_link = row
    place_id, photo_link = row.get("id"), row.get("photo_link")
    file_path = f"{YANDEX_DISK_IMG_URL}/{place_id}.jpg"

    if requests.get(
            get_info_url,
            headers=headers,
            params={'path': file_path}).status_code == 200:
        print(f"{file_path} was uploaded")
        continue

    response = requests.post(
        upload_url,
        headers=headers,
        params={
            'path': file_path,
            'url': photo_link
        }
    )

    if response.status_code == 202:
        print(f"Uploaded: {photo_link} → {file_path}")
    else:
        print(f"Failed to upload {photo_link}: {response.status_code} {response.text}")

print("Finished uploading")
cursor.close()
conn.close()
