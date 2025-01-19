import os
import logging
from src.utils.generate_map import ChoroplethMapGenerator
from src.utils.preprocess_data import main as preprocess_main
from src.utils.get_data import DataDownloader


base_path = os.path.abspath('./data')


def make_map(pickle_file, geojson_file, destination):
    generator = ChoroplethMapGenerator(pickle_file, geojson_file, destination)
    generator.generate_maps()


def main():
    url = 'https://files.data.gouv.fr/geo-dvf/latest/csv/2023/full.csv.gz'
    regions_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'
    departments_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson'
    communes_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson'

    # Download data
    downloader = DataDownloader(url)
    downloader.run()  # Download, unzip, clean, and save as pickle

    # Download GeoJSON files
    downloader.load_geojson('regions', regions_geojson_url)
    downloader.load_geojson('departments', departments_geojson_url)
    downloader.load_geojson('communes', communes_geojson_url)

    # Preprocess data
    preprocess_main()

    # Generate maps
    make_map(
        os.path.join(base_path, 'cleaned', 'prix_m2_par_departement.pkl'),
        os.path.join(base_path, 'cleaned', 'departments.geojson'),
        "region"
    )
    make_map(
        os.path.join(base_path, 'cleaned', 'prix_m2_par_commune.pkl'),
        os.path.join(base_path, 'cleaned', 'communes.geojson'),
        "departement"
    )
    make_map(
        os.path.join(base_path, 'cleaned', 'prix_m2_par_region.pkl'),
        os.path.join(base_path, 'cleaned', 'regions.geojson'),
        "pays"
    )

    logging.info("Data preparation completed.")


if __name__ == "__main__":

    if not os.path.exists(os.path.join(base_path, 'cleaned', 'full_with_region.pkl')):
        logging.info("Data not found. Running data preparation...")
        main()
        from src.app import create_app
        logging.info("Launching app...")
        app = create_app()
        app.run_server(debug=False)
    else :
        from src.app import create_app
        logging.info("Launching app...")
        app = create_app()
        app.run_server(debug=False)
