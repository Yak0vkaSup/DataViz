import pandas as pd
import os
import logging
from src.config import DEPT_CODE_TO_REGION
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataPreprocessor:
    """
    Handles data preprocessing tasks such as calculating price per square meter and grouping data.
    """
    def __init__(self, dataframe):
        self.df = dataframe

    def calculate_price_per_m2(self):
        """
        Calculate the price per square meter for each transaction.
        """
        logging.info("Calculating 'price_per_m2'...")
        self.df['price_per_m2'] = self.df['valeur_fonciere'] / self.df['surface_reelle_bati']

        # Remove rows with missing or zero values in price, surface, or location
        initial_count = len(self.df)
        self.df = self.df[
            (self.df['price_per_m2'].notnull()) &
            (self.df['price_per_m2'] > 0) &
            (self.df['surface_reelle_bati'].notnull()) &
            (self.df['surface_reelle_bati'] > 0)
        ]
        removed = initial_count - len(self.df)
        logging.info(f"Removed {removed} invalid records based on 'price_per_m2' and 'surface_reelle_bati'.")

    def group_by_level(self, levels, column_names):
        """
        Group data by the specified levels and calculate the average price per square meter.

        Parameters:
            levels (list of str): The column names to group by (e.g., ['commune', 'type_local']).
            column_names (list of str): The names to assign to the grouping columns in the output DataFrame.

        Returns:
            pd.DataFrame: A DataFrame with the grouping columns and the average price per square meter.
        """
        if not isinstance(levels, list):
            levels = [levels]
        if not isinstance(column_names, list):
            column_names = [column_names]

        if len(levels) != len(column_names):
            logging.error("The number of levels and column_names must match.")
            raise ValueError("The number of levels and column_names must match.")

        for level in levels:
            if level not in self.df.columns:
                logging.error(f"Grouping level '{level}' does not exist in the DataFrame.")
                raise KeyError(f"Grouping level '{level}' does not exist in the DataFrame.")

        logging.info(f"Grouping data by {levels}...")
        df_grouped = self.df.groupby(levels)['price_per_m2'].mean().reset_index()
        df_grouped.columns = column_names + ['average_price_per_m2']
        logging.info(f"Grouped data by {levels} successfully.")
        return df_grouped


class DataHandler:
    """
    Handles data loading and saving operations.
    """

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def load_data(self, filename):
        """
        Load data from a pickle file.

        Parameters:
            filename (str): The name of the pickle file to load.

        Returns:
            pd.DataFrame: The loaded DataFrame.
        """
        filepath = os.path.join(self.data_dir, filename)
        df = pd.DataFrame
        if not os.path.exists(filepath):
            logging.error(f"Data file '{filepath}' does not exist.")
            raise FileNotFoundError(f"Data file '{filepath}' does not exist.")
        logging.info(f"Loading data from '{filepath}'...")
        try:
            df = pd.read_pickle(filepath)
            logging.info(f"Loaded data with {len(df)} records.")
        except Exception as e:
            logging.error(f"Error in data loading: {e}")
        return df

    def save_data(self, df, filename):
        """
        Save a DataFrame to a pickle file.

        Parameters:
            df (pd.DataFrame): The DataFrame to save.
            filename (str): The name of the pickle file to save to.
        """
        filepath = os.path.join(self.data_dir, filename)
        logging.info(f"Saving data to '{filepath}'...")
        try:
            df.to_pickle(filepath)
            logging.info(f"Data saved to '{filepath}' successfully.")
        except Exception as e:
            logging.error(f"Data is not saved: Error - {e}")

def map_departments_to_regions(df, dept_col='code_departement'):
    """
    Maps department codes in the DataFrame to their corresponding regions.

    Parameters:
        df (pd.DataFrame): The DataFrame containing department codes.
        dept_col (str): The column name for department codes.

    Returns:
        pd.DataFrame: The DataFrame with an additional 'region' column.
    """
    if dept_col not in df.columns:
        logging.error(f"Department column '{dept_col}' not found in DataFrame.")
        raise KeyError(f"Department column '{dept_col}' not found in DataFrame.")

    # Perform the mapping
    df['region'] = df[dept_col].map(DEPT_CODE_TO_REGION)

    # Log any unmapped departments
    missing_regions = df['region'].isnull().sum()
    if missing_regions > 0:
        logging.warning(f"{missing_regions} records have missing region information.")

    return df

def extract_department_code(commune_code):
    """
    Extracts the department code from the commune's INSEE code.
    Rules:
    - Overseas departments: start with '97' -> use first three chars ('971', '972', '973', '974', '976')
    - Corsica: '2A' or '2B'
    - Else: first two chars
    """
    if commune_code.startswith('97'):
        # Pas metropole
        return commune_code[:3]

    if commune_code.startswith('2A') or commune_code.startswith('2B'):
        # Corse
        return commune_code[:2]

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


def build_region_dept_commune_map(communes_dict, departments_dict, regions_dict):
    inverted_regions = {name: code for code, name in regions_dict.items()}

    region_dept_commune_map = {}

    for ccode, cinfo in communes_dict.items():
        dept_code = cinfo['department_code']
        commune_name = cinfo['name']
        dept_info = departments_dict.get(dept_code)

        if dept_info:
            region_name = dept_info['region_name']
            dept_name = dept_info['name']
            region_code = inverted_regions.get(region_name, None)

            if region_name not in region_dept_commune_map:
                region_dept_commune_map[region_name] = {
                    'code': region_code,
                    'departments': {}
                }

            if dept_name not in region_dept_commune_map[region_name]['departments']:
                region_dept_commune_map[region_name]['departments'][dept_name] = {
                    'code': dept_code,
                    'communes': []
                }

            region_dept_commune_map[region_name]['departments'][dept_name]['communes'].append({
                'code': ccode,
                'name': commune_name
            })

    for region_name, rdata in region_dept_commune_map.items():
        for dept_name, ddata in rdata['departments'].items():
            ddata['communes'].sort(key=lambda x: x['name'])

    return region_dept_commune_map

def create_region_dept_commune_map():
    with open('data/regions.geojson', 'r', encoding='utf-8') as file:
        regions_geojson = json.load(file)
    with open('data/departments.geojson', 'r', encoding='utf-8') as file:
        departments_geojson = json.load(file)
    with open('data/communes.geojson', 'r', encoding='utf-8') as file:
        communes_geojson = json.load(file)

    regions_dict = build_regions_dict(regions_geojson)
    departments_dict = build_departments_dict(departments_geojson)
    communes_dict = build_communes_dict(communes_geojson)
    region_dept_commune_map = build_region_dept_commune_map(communes_dict, departments_dict, regions_dict)

    output_path = 'data/region_dept_commune_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(region_dept_commune_map, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved region-department-commune map to {output_path}")


def main():
    data_handler = DataHandler(data_dir='data')

    data = data_handler.load_data('full.pkl')

    data = map_departments_to_regions(data, dept_col='code_departement')

    # Initialize DataPreprocessor and preprocess data
    preprocessor = DataPreprocessor(data)
    preprocessor.calculate_price_per_m2()

    df_by_commune = preprocessor.group_by_level(
        levels=['code_commune', 'type_local'],
        column_names=['commune', 'type_local']
    )
    df_by_departement = preprocessor.group_by_level(
        levels=['code_departement', 'type_local'],
        column_names=['departement', 'type_local']
    )
    df_by_region = preprocessor.group_by_level(
        levels=['region', 'type_local'],
        column_names=['region', 'type_local']
    )

    data_handler.save_data(df_by_commune, 'prix_m2_par_commune.pkl')
    data_handler.save_data(df_by_departement, 'prix_m2_par_departement.pkl')
    data_handler.save_data(df_by_region, 'prix_m2_par_region.pkl')
    data_handler.save_data(data, 'full_with_region.pkl')

    create_region_dept_commune_map()

if __name__ == '__main__':
    main()