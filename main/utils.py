import json
from django.contrib.staticfiles import finders

def load_json_data(filename):
    file_path = finders.find('data/' + filename)
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"File {filename} not found in static directory.")
