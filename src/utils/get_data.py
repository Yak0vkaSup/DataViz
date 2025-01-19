import requests
import gzip
import shutil
import os
import pandas as pd
import logging
from tqdm import tqdm
import json
from urllib.request import urlopen

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataDownloader:
    def __init__(self, url, download_folder='data/cleaned', filename='full.csv.gz'):
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

    def load_geojson(self, name, url):
        data_path = os.path.join(self.download_folder, f'{name}.geojson')
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
                with urlopen(url) as response:
                    geojson = json.load(response)
                # Save to local file
                os.makedirs(self.download_folder, exist_ok=True)
                with open(data_path, 'w', encoding='utf-8') as f:
                    json.dump(geojson, f)
                logging.info(f"Successfully downloaded and saved GeoJSON data to {data_path}")
                return geojson
            except Exception as e:
                logging.error(f"Failed to download GeoJSON data from {url}: {e}")
                return None

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
