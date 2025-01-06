import requests
import gzip
import shutil
import os
import pandas as pd
import logging
from tqdm import tqdm
import json
from urllib.request import urlopen
from collections import defaultdict
import ssl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEPT_CODE_TO_REGION = {
    '01': 'Auvergne-Rhône-Alpes',
    '02': 'Hauts-de-France',
    '03': 'Auvergne-Rhône-Alpes',
    '04': 'Provence-Alpes-Côte d\'Azur',
    '05': 'Provence-Alpes-Côte d\'Azur',
    '06': 'Provence-Alpes-Côte d\'Azur',
    '07': 'Auvergne-Rhône-Alpes',
    '08': 'Grand Est',
    '09': 'Occitanie',
    '10': 'Grand Est',
    '11': 'Occitanie',
    '12': 'Occitanie',
    '13': 'Provence-Alpes-Côte d\'Azur',
    '14': 'Normandie',
    '15': 'Auvergne-Rhône-Alpes',
    '16': 'Nouvelle-Aquitaine',
    '17': 'Nouvelle-Aquitaine',
    '18': 'Centre-Val de Loire',
    '19': 'Nouvelle-Aquitaine',
    '2A': 'Corse',
    '2B': 'Corse',
    '21': 'Bourgogne-Franche-Comté',
    '22': 'Bretagne',
    '23': 'Nouvelle-Aquitaine',
    '24': 'Nouvelle-Aquitaine',
    '25': 'Bourgogne-Franche-Comté',
    '26': 'Auvergne-Rhône-Alpes',
    '27': 'Normandie',
    '28': 'Centre-Val de Loire',
    '29': 'Bretagne',
    '30': 'Occitanie',
    '31': 'Occitanie',
    '32': 'Nouvelle-Aquitaine',
    '33': 'Nouvelle-Aquitaine',
    '34': 'Occitanie',
    '35': 'Bretagne',
    '36': 'Centre-Val de Loire',
    '37': 'Centre-Val de Loire',
    '38': 'Auvergne-Rhône-Alpes',
    '39': 'Bourgogne-Franche-Comté',
    '40': 'Nouvelle-Aquitaine',
    '41': 'Centre-Val de Loire',
    '42': 'Auvergne-Rhône-Alpes',
    '43': 'Auvergne-Rhône-Alpes',
    '44': 'Pays de la Loire',
    '45': 'Centre-Val de Loire',
    '46': 'Occitanie',
    '47': 'Nouvelle-Aquitaine',
    '48': 'Occitanie',
    '49': 'Pays de la Loire',
    '50': 'Normandie',
    '51': 'Grand Est',
    '52': 'Grand Est',
    '53': 'Pays de la Loire',
    '54': 'Grand Est',
    '55': 'Grand Est',
    '56': 'Bretagne',
    '57': 'Grand Est',
    '58': 'Bourgogne-Franche-Comté',
    '59': 'Hauts-de-France',
    '60': 'Hauts-de-France',
    '61': 'Normandie',
    '62': 'Hauts-de-France',
    '63': 'Auvergne-Rhône-Alpes',
    '64': 'Nouvelle-Aquitaine',
    '65': 'Occitanie',
    '66': 'Occitanie',
    '67': 'Grand Est',
    '68': 'Grand Est',
    '69': 'Auvergne-Rhône-Alpes',
    '70': 'Bourgogne-Franche-Comté',
    '71': 'Bourgogne-Franche-Comté',
    '72': 'Pays de la Loire',
    '73': 'Auvergne-Rhône-Alpes',
    '74': 'Auvergne-Rhône-Alpes',
    '75': 'Île-de-France',
    '76': 'Normandie',
    '77': 'Île-de-France',
    '78': 'Île-de-France',
    '79': 'Nouvelle-Aquitaine',
    '80': 'Hauts-de-France',
    '81': 'Occitanie',
    '82': 'Occitanie',
    '83': 'Provence-Alpes-Côte d\'Azur',
    '84': 'Provence-Alpes-Côte d\'Azur',
    '85': 'Pays de la Loire',
    '86': 'Nouvelle-Aquitaine',
    '87': 'Nouvelle-Aquitaine',
    '88': 'Grand Est',
    '89': 'Bourgogne-Franche-Comté',
    '90': 'Bourgogne-Franche-Comté',
    '91': 'Île-de-France',
    '92': 'Île-de-France',
    '93': 'Île-de-France',
    '94': 'Île-de-France',
    '95': 'Île-de-France',
    '971': 'Guadeloupe',
    '972': 'Martinique',
    '973': 'Guyane',
    '974': 'La Réunion',
    '976': 'Mayotte'
}

class DataDownloader:
    def __init__(self, url, download_folder='data', filename='full.csv.gz'):
        self.url = url
        self.filename = filename
        self.unzipped_filename = filename.replace('.gz', '')
        self.download_folder = download_folder
        self.pickle_filename = os.path.join(download_folder, 'full.pkl')

        # Ensure the download folder exists
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

    def download_file(self):
        # Download with tqdm progress bar
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(self.filename, 'wb') as file, tqdm(
                desc=self.filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))

    def unzip_file(self):
        # Unzip the gz file
        with gzip.open(self.filename, 'rb') as f_in:
            with open(self.unzipped_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def load_csv_to_dataframe(self):
        # Load the unzipped CSV file into a pandas DataFrame with low_memory=False to avoid dtype warnings
        return pd.read_csv(self.unzipped_filename, low_memory=False)

    def save_dataframe_as_pickle(self, df):
        # Save DataFrame as a pickle file in the specified folder
        df.to_pickle(self.pickle_filename)
        logging.info(f"DataFrame saved as {self.pickle_filename}")

    def clean_up(self):
        # Remove the downloaded and unzipped files
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.unzipped_filename):
            os.remove(self.unzipped_filename)
        logging.info("Temporary files deleted.")

    def run(self):
        # Execute the whole process
        logging.info("Starting the download process...")
        self.download_file()
        logging.info("Download complete. Unzipping the file...")
        self.unzip_file()
        logging.info("Unzipping complete. Loading the CSV into a DataFrame...")
        df = self.load_csv_to_dataframe()
        logging.info("Cleaning duplicates")
        df = df.drop_duplicates(subset='id_parcelle', keep='first')
        logging.info("Data loaded into DataFrame. Saving as pickle...")
        self.save_dataframe_as_pickle(df)
        logging.info("Cleaning up temporary files...")
        self.clean_up()
        logging.info("Process completed successfully!")

    def load_geojson(self, name, url):
        data_path = os.path.join('data', f'{name}.geojson')
        ssl_context = ssl._create_unverified_context()  # Create an unverified SSL context

        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    geojson = json.load(f)
                logging.info(f"Successfully loaded GeoJSON data from {data_path}")
                return geojson
            except Exception as e:
                logging.error(f"Failed to load GeoJSON data from {data_path}: {e}")
                return None
        else:
            try:
                with urlopen(url, context=ssl_context) as response:
                    geojson = json.load(response)
                # Save to local file
                os.makedirs('data', exist_ok=True)
                with open(data_path, 'w', encoding='utf-8') as f:
                    json.dump(geojson, f)
                logging.info(f"Successfully downloaded and saved GeoJSON data to {data_path}")
                return geojson
            except Exception as e:
                logging.error(f"Failed to download GeoJSON data from {url}: {e}")
                return None
def extract_department_code(commune_code):
    """
    Extracts the department code from the commune's INSEE code.
    Rules:
    - Overseas departments: start with '97' -> use first three chars ('971', '972', '973', '974', '976')
    - Corsica: '2A' or '2B'
    - Else: first two chars
    """
    if commune_code.startswith('97'):
        # Overseas departments or regions
        return commune_code[:3]

    if commune_code.startswith('2A') or commune_code.startswith('2B'):
        # Corsica
        return commune_code[:2]

    # Default case: first two chars
    return commune_code[:2]
def build_regions_dict(regions_geojson):
    return {
        feature['properties']['code']: feature['properties']['nom']
        for feature in regions_geojson['features']
    }


def build_departments_dict(departments_geojson):
    departments_dict = {}
    for feature in departments_geojson['features']:
        dept_code = feature['properties']['code']
        dept_name = feature['properties']['nom']
        region_name = DEPT_CODE_TO_REGION.get(dept_code)

        if not region_name:
            region_name = "Inconnue"

        departments_dict[dept_code] = {
            'name': dept_name,
            'region_code': None,
            'region_name': region_name
        }
    return departments_dict


def build_communes_dict(communes_geojson):
    communes_dict = {}
    for feature in communes_geojson['features']:
        commune_code = feature['properties']['code']
        commune_name = feature['properties']['nom']
        dept_code = extract_department_code(commune_code)
        communes_dict[commune_code] = {
            'name': commune_name,
            'department_code': dept_code
        }
    return communes_dict


def build_region_dept_commune_map(communes_dict, departments_dict):
    inverted_regions = {name: code for code, name in regions_dict.items()}
    # First, we need a structure to hold data before sorting and finalizing.
    region_dept_commune_map = {}

    for ccode, cinfo in communes_dict.items():
        dept_code = cinfo['department_code']
        commune_name = cinfo['name']
        dept_info = departments_dict.get(dept_code)

        if dept_info:
            region_name = dept_info['region_name']
            dept_name = dept_info['name']
            region_code = inverted_regions.get(region_name, None)

            # Ensure region key exists
            if region_name not in region_dept_commune_map:
                region_dept_commune_map[region_name] = {
                    'code': region_code,
                    'departments': {}
                }

            # Ensure department key exists under this region
            if dept_name not in region_dept_commune_map[region_name]['departments']:
                region_dept_commune_map[region_name]['departments'][dept_name] = {
                    'code': dept_code,
                    'communes': []
                }

            # Append the commune as a dict with code and name
            region_dept_commune_map[region_name]['departments'][dept_name]['communes'].append({
                'code': ccode,
                'name': commune_name
            })

    # Optionally sort the communes by name
    for region_name, rdata in region_dept_commune_map.items():
        for dept_name, ddata in rdata['departments'].items():
            ddata['communes'].sort(key=lambda x: x['name'])

    return region_dept_commune_map

if __name__ == '__main__':
    url = 'https://files.data.gouv.fr/geo-dvf/latest/csv/2023/full.csv.gz'
    regions_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'
    departments_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson'
    communes_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson'

    downloader = DataDownloader(url)
    downloader.run()
    regions_geojson = downloader.load_geojson('regions', regions_geojson_url)
    departments_geojson = downloader.load_geojson('departments', departments_geojson_url)
    communes_geojson = downloader.load_geojson('communes', communes_geojson_url)

    regions_dict = build_regions_dict(regions_geojson)
    departments_dict = build_departments_dict(departments_geojson)
    communes_dict = build_communes_dict(communes_geojson)
    region_dept_commune_map = build_region_dept_commune_map(communes_dict, departments_dict)

    # Save the map to a JSON file
    output_path = 'data/region_dept_commune_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(region_dept_commune_map, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved region-department-commune map to {output_path}")

    # Optional: print a sample
    print(json.dumps(region_dept_commune_map, ensure_ascii=False, indent=2))
