import os
from src.utils.generate_map import ChoroplethMapGenerator
from src.utils.preprocess_data import main as preprocess_main
from src.utils.get_data import DataDownloader
from src.app import create_app

base_path = os.path.abspath('./data')


def make_map(pickle_file,geojson_file, destination):
    generator = ChoroplethMapGenerator(pickle_file, geojson_file, destination)
    generator.generate_maps()

if __name__ == "__main__":
    url = 'https://files.data.gouv.fr/geo-dvf/latest/csv/2023/full.csv.gz'
    regions_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'
    departments_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson'
    communes_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson'


    # downloader = DataDownloader(url)
    # downloader.run()  # Download, unzip, clean, and save as pickle
    #
    # downloader.load_geojson('regions', regions_geojson_url)
    # downloader.load_geojson('departments', departments_geojson_url)
    # downloader.load_geojson('communes', communes_geojson_url)
    #
    # preprocess_main()
    #
    # make_map(os.path.join(base_path,'cleaned', 'prix_m2_par_departement.pkl'),os.path.join(base_path,'cleaned', 'departments.geojson'),"region")
    # make_map(os.path.join(base_path,'cleaned', 'prix_m2_par_commune.pkl'),os.path.join(base_path,'cleaned', 'communes.geojson'),"departement")
    # make_map(os.path.join(base_path,'cleaned', 'prix_m2_par_region.pkl'),os.path.join(base_path,'cleaned', 'regions.geojson'),"pays")

    print("Launching app...")
    app = create_app()
    app.run_server(debug=False)