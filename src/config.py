import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')

REGION_MAP_FILE = os.path.join(DATA_DIR, 'region_dept_commune_map.json')

# Function to load region-department-commune map
def load_region_dept_commune_map():
    try:
        with open(REGION_MAP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Region-department-commune map not found at {REGION_MAP_FILE}")