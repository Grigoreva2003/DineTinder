import requests
import psycopg2
from psycopg2 import sql
from main.defs import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, MOS_DATA_API_KEY

BASE_URL = "https://apidata.mos.ru/v1/datasets/1903/rows"

FILTER_QUERY = "TypeObject eq 'ресторан' or TypeObject eq 'бар'" \
               " or TypeObject eq 'кафе' or TypeObject eq 'предприятие быстрого обслуживания'" \
               " or TypeObject eq 'кафетерий'"

BATCH_SIZE = 1_000
TOTAL_ROWS = 20_000


def get_category(original_name: str) -> str:
    """Maps the original TypeObject name to a more generalized category."""
    category_mapping = {
        "предприятие быстрого обслуживания": "фастфуд",
        "кафетерий": "кофейня"
    }
    return category_mapping.get(original_name, original_name)


def fetch_data(skip: int) -> list:
    """Fetches a batch of data from the API."""
    params = {
        "$filter": FILTER_QUERY,
        "$top": BATCH_SIZE,
        "$skip": skip,
        "api_key": MOS_DATA_API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()

    print(f"Failed to fetch data at skip={skip}. Status code: {response.status_code}")
    return []


def insert_data(cursor, data: list):
    """Inserts fetched data into the PostgreSQL database."""
    for item in data:
        cells = item.get("Cells", {})
        name = cells.get("Name", "Unknown")
        address = cells.get("Address", "Unknown")
        category = get_category(cells.get("TypeObject", "Unknown"))
        description = ""  # Placeholder
        photo_link = ""  # Placeholder
        rating = 0.0  # Placeholder

        cursor.execute(
            sql.SQL(
                "INSERT INTO public.dining_places (name, photo_link, address, description, category, rating)"
                " VALUES (%s, %s, %s, %s, %s, %s)"),
            (name, photo_link, address, description, category, rating)
        )


with psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
) as conn:
    with conn.cursor() as cursor:
        for skip in range(0, TOTAL_ROWS, BATCH_SIZE):
            data = fetch_data(skip)

            if data:
                insert_data(cursor, data)
                print(f"Inserted {min(skip + BATCH_SIZE, TOTAL_ROWS)} rows")
            else:
                print(f"Empty data")

        conn.commit()
