import os
from src.utils.generate_map import ChoroplethMapGenerator

base_path = os.path.abspath('./data')


def make_map(pickle_file,geojson_file, destination):
    generator = ChoroplethMapGenerator(pickle_file, geojson_file, destination)
    generator.generate_maps()

if __name__ == "__main__":

    make_map(os.path.join(base_path, 'prix_m2_par_departement.pkl'),os.path.join(base_path, 'departments.geojson'),"region")
    make_map(os.path.join(base_path, 'prix_m2_par_commune.pkl'),os.path.join(base_path, 'communes.geojson'),"departement")