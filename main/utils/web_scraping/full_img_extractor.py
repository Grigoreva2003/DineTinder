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

cursor.execute("SELECT id, name, category, address FROM dining_places WHERE photo_link = '';")
places_data = cursor.fetchall()

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
time.sleep(1)

for place in places_data:
    place_id, name, category, address = place
    search_query = f"{name} {category} {address} фото"
    url = f"https://yandex.ru/images/search?text={search_query}"

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img"))
        )

        # Extract image URLs
        image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
        image_urls = [img.get_attribute("src") for img in image_elements if img.get_attribute("src")]

        # Find the first valid image URL
        if image_urls:
            first_image_url = image_urls[0]
            if "captcha" in first_image_url:
                time.sleep(10)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img"))
                )
                image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
                first_image_url = [img.get_attribute("src") for img in image_elements if img.get_attribute("src")][0]

            update_query = "UPDATE dining_places SET photo_link = %s WHERE id = %s;"
            cursor.execute(update_query, (first_image_url, place_id))
            conn.commit()

            print(f"Updated {name} with image: {first_image_url}")

        else:
            print(f"No images found for {name}")

    except Exception as e:
        print(f"Error processing {name}: {e}")

driver.quit()
cursor.close()
conn.close()
print("Database connection closed.")
