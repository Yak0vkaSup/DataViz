"""
This module contains functions and classes for preprocessing real estate data,
including data loading, transformations, and geographic mapping.
"""


import os
import logging
import json

import pandas as pd

from config import DEPT_CODE_TO_REGION


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
        Removes rows with invalid or missing values in relevant fields.
        """
        logging.info("Calculating 'price_per_m2'...")
        self.df['price_per_m2'] = self.df['valeur_fonciere'] / self.df['surface_reelle_bati']

        initial_count = len(self.df)
        self.df = self.df[
            (self.df['price_per_m2'].notnull()) &
            (self.df['price_per_m2'] > 0) &
            (self.df['surface_reelle_bati'].notnull()) &
            (self.df['surface_reelle_bati'] > 0)
        ]
        removed = initial_count - len(self.df)
        logging.info(
            "Removed %d invalid records based on 'price_per_m2' and 'surface_reelle_bati'.",
            removed
        )

    def group_by_level(self, levels, column_names):
        """
        Group data by the specified levels and calculate the average price per square meter.

        Parameters:
            levels (list of str): The column names to group by.
            column_names (list of str): The names to assign to the grouping columns.

        Returns:
            pd.DataFrame: A DataFrame with the grouping columns and
            the average price per square meter.
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
                logging.error("Grouping level '%s' does not exist in the DataFrame.", level)
                raise KeyError(f"Grouping level '{level}' does not exist in the DataFrame.")

        logging.info("Grouping data by %s...", levels)
        df_grouped = self.df.groupby(levels)['price_per_m2'].mean().reset_index()
        df_grouped.columns = column_names + ['average_price_per_m2']
        logging.info("Grouped data by %s successfully.", levels)
        return df_grouped


class DataHandler:
    """
    Handles data loading and saving operations.
    """

    def __init__(self, input_dir='data', output_dir='data/cleaned'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self, filename):
        """
        Load data from a pickle file.

        Parameters:
            filename (str): The name of the pickle file to load.

        Returns:
            pd.DataFrame: The loaded DataFrame.
        """
        filepath = os.path.join(self.input_dir, filename)
        df = pd.DataFrame
        if not os.path.exists(filepath):
            logging.error("Data file %s  does not exist.", filepath)
            raise FileNotFoundError("Data file %s does not exist.", filepath)
        logging.info("Loading data from %s ...", filepath)
        try:
            df = pd.read_pickle(filepath)
            logging.info("Loaded data with %s records.", len(df))
        except Exception as e:
            logging.error("Error in data loading: %s", {e})
        return df

    def save_data(self, df, filename):
        """
        Save a DataFrame to a pickle file.

        Parameters:
            df (pd.DataFrame): The DataFrame to save.
            filename (str): The name of the pickle file to save to.
        """
        filepath = os.path.join(self.output_dir, filename)
        logging.info("Saving data to %s ...",filepath)
        try:
            df.to_pickle(filepath)
            logging.info("Data saved to %s successfully.", filepath)
        except Exception as e:
            logging.error("Data is not saved: Error - %s", {e})

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
        logging.error("Department column %s not found in DataFrame.", dept_col)
        raise KeyError("Department column %s not found in DataFrame.", dept_col)

    # Perform the mapping
    df['region'] = df[dept_col].map(DEPT_CODE_TO_REGION)

    # Log any unmapped departments
    missing_regions = df['region'].isnull().sum()
    if missing_regions > 0:
        logging.warning("%s records have missing region information.", missing_regions)

    return df

def extract_department_code(commune_code):
    """
    Extracts the department code from the commune's INSEE code.
    Rules:
    - Overseas departments: start with '97' -> use first three chars
    ('971', '972', '973', '974', '976')
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
    """
    Builds a dictionary mapping region codes to region names from a GeoJSON object.

    Parameters:
        regions_geojson (dict): A GeoJSON object containing region data.

    Returns:
        dict: A dictionary where keys are region codes and values are region names.
    """
    return {
        feature['properties']['code']: feature['properties']['nom']
        for feature in regions_geojson['features']
    }


def build_departments_dict(departments_geojson):
    """
    Builds a dictionary containing department details, including their name and associated region.

    Parameters:
        departments_geojson (dict): A GeoJSON object containing department data.

    Returns:
        dict: A dictionary where keys are department codes and values are dictionaries with:
              - 'name': The name of the department.
              - 'region_code': The region code (None in this case).
              - 'region_name': The name of the associated region.
    """
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
    """
    Builds a dictionary containing commune details, including their name
    and associated department code.

    Parameters:
        communes_geojson (dict): A GeoJSON object containing commune data.

    Returns:
        dict: A dictionary where keys are commune codes and values are dictionaries with:
              - 'name': The name of the commune.
              - 'department_code': The code of the associated department.
    """
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
    """
     Builds a hierarchical mapping of regions, departments, and communes.

     Parameters:
     communes_dict (dict): A dictionary of communes with their codes, names, and department codes.
     departments_dict (dict): A dictionary of departments with their codes, names, and region names.
     regions_dict (dict): A dictionary of regions with their codes and names.

     Returns:
         dict: A nested dictionary where regions contain departments, and
         departments contain communes.
    """
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

def create_region_dept_commune_map(input_dir='data/cleaned', output_dir='data/cleaned'):
    """
    Creates a hierarchical map of regions, departments, and communes, and saves it as a JSON file.

    Parameters:
        input_dir (str): The directory containing the input GeoJSON files.
        output_dir (str): The directory where the output JSON file will be saved.

    Returns:
        None
    """
    with open(input_dir+'/regions.geojson', 'r', encoding='utf-8') as file:
        regions_geojson = json.load(file)
    with open(input_dir+'/departments.geojson', 'r', encoding='utf-8') as file:
        departments_geojson = json.load(file)
    with open(input_dir+'/communes.geojson', 'r', encoding='utf-8') as file:
        communes_geojson = json.load(file)

    regions_dict = build_regions_dict(regions_geojson)
    departments_dict = build_departments_dict(departments_geojson)
    communes_dict = build_communes_dict(communes_geojson)
    region_dept_commune_map = build_region_dept_commune_map(
        communes_dict,
        departments_dict,
        regions_dict
    )

    output_path = output_dir+'/region_dept_commune_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(region_dept_commune_map, f, ensure_ascii=False, indent=2)
    logging.info("Saved region-department-commune map to %s", output_path)


def main():
    """
     Main entry point for the preprocessing pipeline.

     - Loads data from a pickle file.
     - Maps departments to their regions.
     - Preprocesses data (e.g., calculates price per square meter).
     - Groups data at various administrative levels (communes, departments, regions).
     - Saves the processed data.
     - Creates a hierarchical map of regions, departments, and communes.

     Returns:
         None
     """
    input_dir = 'data/cleaned'
    output_dir = 'data/cleaned'

    data_handler = DataHandler(input_dir=input_dir, output_dir=output_dir)

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

    create_region_dept_commune_map(input_dir=input_dir, output_dir=output_dir)

if __name__ == '__main__':
    main()
