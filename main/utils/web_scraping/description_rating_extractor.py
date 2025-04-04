import time
import requests
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from main.defs import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected to the database successfully.")
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()

cursor.execute("SELECT id, name, category, address FROM dining_places WHERE rating = 0;")
places_data = cursor.fetchall()
# try:
#     response = requests.get("http://127.0.0.1:80/places/")
#     response.raise_for_status()
#     places_data = response.json().get("places", [])
#     print(f"Fetched {len(places_data)} places from API.")
# except requests.RequestException as e:
#     print(f"API request failed: {e}")
#     places_data = []

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

for place in places_data:
    place_id, name, category, address = place
    # place_id, name, category, address, description, rating = place["id"], place["name"], place["category"], place[
    #     "address"], place["description"], place["rating"]
    if name in ["KFC", "Вкусно - и точка", "Ростикс KFC"]:
        continue
    # if rating != 0 or description != f"":
    #     continue
    search_query = f"yandex maps {name} {category} {address}"
    search_url = f"https://ya.ru/search/?text={search_query}"

    driver.get(search_url)

    try:
        yandex_map_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "https://yandex.ru/maps")]'))
        )
        map_url = yandex_map_link.get_attribute("href")
        if "reviews/" in map_url:
            map_url = map_url.replace("reviews/", "")
        print(f"Extracted Yandex Maps URL: {map_url}")

        driver.get(map_url)
        # time.sleep(3)

        rating_value = 0
        description_text = ""

        try:
            rating_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "business-rating-badge-view__rating-text"))
            )
            rating_value = '.'.join(rating_element.text.split(","))
            print(f"Extracted Rating: {rating_value}")
        except Exception as e:
            print(f"Failed to extract rating for {name}. Defaulting to {rating_value}.")
        try:
            desc_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "business-story-entry-view__description"))
            )
            description_text = desc_element.text
            print(f"Extracted Description: {description_text}")
        except Exception as e:
            print(f"Failed to extract description for {name}. Defaulting to empty string.")

        cursor.execute(
            "UPDATE dining_places SET rating = %s, description = %s WHERE id = %s",
            (rating_value, description_text, place_id),
        )
        conn.commit()
        print()

    except Exception as e:
        print(f"Failed to extract data for {name}: {e}")

cursor.close()
conn.close()

driver.quit()
print("Process completed.")
