"""
This module provides functionality to download, process, and manage real estate
data from specified URLs, including GeoJSON files for geographic boundaries.
"""

import os
import gzip
import shutil
import logging
import json
from urllib.request import urlopen
import requests
import pandas as pd
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataDownloader:
    """
    A class for downloading, unzipping, processing, and saving real estate data.

    Attributes:
        url (str): URL of the dataset to download.
        download_folder (str): Folder to save downloaded files.
        filename (str): Name of the downloaded file.
    """
    def __init__(self, url, download_folder='data/cleaned', filename='full.csv.gz'):
        """
        Initialize the DataDownloader with the URL and paths for files.

        Args:
            url (str): URL to download the data from.
            download_folder (str): Directory to save downloaded files.
            filename (str): Name of the file to be downloaded.
        """
        self.url = url
        self.filename = filename
        self.unzipped_filename = filename.replace('.gz', '')
        self.download_folder = download_folder
        self.pickle_filename = os.path.join(download_folder, 'full.pkl')

        # Ensure the download folder exists
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

    def download_file(self):
        """
        Download the file from the URL with a progress bar (tqdm).
        """
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
        """
        Unzip the downloaded .gz file.
        """
        with gzip.open(self.filename, 'rb') as f_in:
            with open(self.unzipped_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def load_csv_to_dataframe(self):
        """
        Load the unzipped CSV file into a pandas DataFrame.

        Returns:
            pd.DataFrame: Loaded DataFrame.
        """
        return pd.read_csv(self.unzipped_filename, low_memory=False)

    def save_dataframe_as_pickle(self, df):
        """
        Save a pandas DataFrame as a pickle file.

        Args:
            df (pd.DataFrame): DataFrame to save.
        """
        df.to_pickle(self.pickle_filename)
        logging.info("DataFrame saved as %s", self.pickle_filename)

    def clean_up(self):
        """
        Remove the downloaded and unzipped files.
        """
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.unzipped_filename):
            os.remove(self.unzipped_filename)
        logging.info("Temporary files deleted.")

    def load_geojson(self, name, url):
        """
        Load GeoJSON data from a file or download it if not available locally.

        Args:
            name (str): Name of the GeoJSON file (used for local saving).
            geojson_url (str): URL to download the GeoJSON file.

        Returns:
            dict: Loaded GeoJSON data.
        """
        data_path = os.path.join(self.download_folder, f'{name}.geojson')
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    geojson = json.load(f)
                logging.info("Successfully loaded GeoJSON data from %s", data_path)
                return geojson
            except Exception as e:
                logging.error("Failed to load GeoJSON data from %s: %s", data_path, e)
                return None
        else:
            try:
                with urlopen(url) as response:
                    geojson = json.load(response)
                # Save to local file
                os.makedirs(self.download_folder, exist_ok=True)
                with open(data_path, 'w', encoding='utf-8') as f:
                    json.dump(geojson, f)
                logging.info("Successfully downloaded and saved GeoJSON data to %s", data_path)
                return geojson
            except Exception as e:
                logging.error("Failed to download GeoJSON data from %s: %s", url, e)
                return None

    def run(self):
        """
        Execute the full data download, processing, and cleanup pipeline.
        """
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
    URL = 'https://files.data.gouv.fr/geo-dvf/latest/csv/2023/full.csv.gz'
    REGIONS_GEOJSON_URL = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'
    DEPARTMENTS_GEOJSON_URL = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson'
    COMMUNES_GEOJSON_URL = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson'

    downloader = DataDownloader(URL)
    downloader.run()
    regions_geojson = downloader.load_geojson('regions', REGIONS_GEOJSON_URL)
    departments_geojson = downloader.load_geojson('departments', DEPARTMENTS_GEOJSON_URL)
    communes_geojson = downloader.load_geojson('communes', COMMUNES_GEOJSON_URL)
