"""
This module provides functionality to generate choropleth maps for real estate
data, showing the average price per square meter at various geographic levels.
"""

import os
import logging
import json
import numpy as np
import pandas as pd
import folium

from config import load_region_dept_commune_map

base_path = os.path.abspath('data')


class ChoroplethMapGenerator:
    """
    A class for generating choropleth maps based on geographic and real estate data.
    """

    LEVEL_MAP = {
        "pays": "region",
        "region": "departement",
        "departement": "commune"
    }
    ZOOM_START_MAP = {
        "pays": 6,  # Suitable zoom level for a country
        "region": 7,  # Suitable zoom level for a region
        "departement": 9  # Suitable zoom level for a department
    }

    def __init__(self, pickle_file, geojson_file, level):
        """
         Initialize the ChoroplethMapGenerator with data and configurations.

         Args:
             pickle_file (str): Path to the pickle file containing grouped data.
             geojson_file (str): Path to the GeoJSON file for geographic data.
             level (str): Geographic level for the map (e.g., "region", "departement").
         """
        self.pickle_file = pickle_file
        self.geojson_file = geojson_file
        self.scale_dept_commune_map = load_region_dept_commune_map()
        self.scale_list = self.scale_dept_commune_map.keys()
        self.output_dir = os.path.join(base_path, f'cleaned/{level}s_maps/')
        self.level = level
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def load_grouped_data(pickle_filename):
        """
        Load the preprocessed DataFrame from a pickle file.

        Args:
            pickle_filename (str): Path to the pickle file.

        Returns:
            pd.DataFrame: The loaded DataFrame.
        """
        return pd.read_pickle(pickle_filename)

    @staticmethod
    def add_price_to_geojson(df, geojson_data, geojson_key):
        """
        Add the average price per square meter from the DataFrame to the GeoJSON data.

        Args:
            df (pd.DataFrame): DataFrame containing price data.
            geojson_data (dict): GeoJSON data to modify.
            geojson_key (str): Key to match between the DataFrame and GeoJSON.

        Returns:
            dict: Updated GeoJSON data with price information.
        """

        # Convert the DataFrame to a dictionary for easy lookup
        df_dict = df.set_index(geojson_key)['average_price_per_m2'].to_dict()

        # Loop through each feature in the GeoJSON file and add the price per m²
        for feature in geojson_data['features']:
            code = feature['properties'][geojson_key]
            # Add the price to the feature's properties if the department exists in the DataFrame
            feature['properties']['average_price_per_m2'] = df_dict.get(code, None)

        return geojson_data

    @staticmethod
    def calculate_geojson_center(geojson_data):
        """
        Calculate the geographic center (centroid) of the given GeoJSON features.

        Parameters:
        - geojson_data (dict): A GeoJSON FeatureCollection.

        Returns:
        - tuple: (latitude, longitude) of the centroid.
        """
        latitudes, longitudes = [], []
        for feature in geojson_data['features']:
            geom = feature['geometry']
            coords = geom['coordinates']

            if geom['type'] == 'Polygon':
                latitudes, longitudes = ChoroplethMapGenerator._extract_polygon_coords(coords, latitudes, longitudes)
            elif geom['type'] == 'MultiPolygon':
                latitudes, longitudes = ChoroplethMapGenerator._extract_multipolygon_coords(coords, latitudes,
                                                                                            longitudes)

        if latitudes and longitudes:
            return np.mean(latitudes), np.mean(longitudes)
        else:
            return 46.603354, 1.888334  # Default to the center of France

    @staticmethod
    def _extract_polygon_coords(coords, latitudes, longitudes):
        """
        Extract coordinates from a Polygon geometry.
        """
        for ring in coords:
            for lon, lat in ring:
                latitudes.append(lat)
                longitudes.append(lon)
        return latitudes, longitudes

    @staticmethod
    def _extract_multipolygon_coords(coords, latitudes, longitudes):
        """
        Extract coordinates from a MultiPolygon geometry.
        """
        for polygon in coords:
            for ring in polygon:
                for lon, lat in ring:
                    latitudes.append(lat)
                    longitudes.append(lon)
        return latitudes, longitudes

    def display_scale_list(self, scale_name):
        """
        Display the list of scales (e.g., departments) for a given region.

        Args:
            scale_name (str): Name of the region.

        Returns:
            list: List of department codes in the region.
        """
        region_departement = self.scale_dept_commune_map.get(scale_name)
        scale = "departments"
        if not region_departement:
            logging.info("Region %s not found in the data.", scale_name)
            return []

        min_scale = region_departement.get(scale, {})
        if not min_scale:
            logging.info("No departments found in the region %s.", scale_name)
            return []

        logging.info("Departments in %s:", scale_name)
        return [dept_info.get('code', 'N/A') for dept_info in min_scale.values()]

    def create_choropleth_map(self, df, geojson_data, geojson_key, level, map_filename=None):
        """
        Create a choropleth map showing the average price per square meter by the specified level,
        using a logarithmic scale to handle wide ranges of values.
        Args:
            df (pd.DataFrame): DataFrame containing price data.
            geojson_data (dict): GeoJSON data for the map.
            geojson_key (str): Key to match between the DataFrame and GeoJSON.
            level (str): Geographic level for the map.
            map_filename (str, optional): Output filename for the map. Defaults to None.
        """
        code = 'code'
        zoom_start = self.ZOOM_START_MAP.get(level, 8)
        if self.LEVEL_MAP[self.level] in df.columns:
            if self.LEVEL_MAP[self.level] == "region":
                df = df.rename(columns={self.LEVEL_MAP[self.level]: 'nom'})
                code = 'nom'
            else:
                df = df.rename(columns={self.LEVEL_MAP[self.level]: 'code'})
        df['log_price_per_m2'] = np.log1p(df['average_price_per_m2'])
        center_lat, center_lon = self.calculate_geojson_center(geojson_data)
        geojson_data = self.add_price_to_geojson(df, geojson_data, geojson_key)
        thresholds = [
            df['log_price_per_m2'].min(), df['log_price_per_m2'].quantile(0.25),
            df['log_price_per_m2'].quantile(0.5),
            df['log_price_per_m2'].quantile(0.75),
            df['log_price_per_m2'].max()
        ]
        price_map = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
        folium.Choropleth(
            geo_data=geojson_data,
            name='choropleth',
            data=df,
            columns=[code, 'log_price_per_m2'],
            key_on=f'feature.properties.{geojson_key}',
            fill_color='YlOrRd',  # Color scale from yellow to red
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Log of Price per m² (€)',
            threshold_scale=thresholds  # Custom thresholds based on the logarithmic scale
        ).add_to(price_map)

        folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                'fillColor': '#ffffff00',
                'color': 'transparent',
                'weight': 0,
                'fillOpacity': 0,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[code, 'average_price_per_m2'],
                aliases=[self.LEVEL_MAP[self.level] + ' :', 'price per m²:'],
                localize=True,
                sticky=False,
                labels=True,
                style=("background-color: white; color: black; font-weight: bold;"),
            )
        ).add_to(price_map)
        map_filename = map_filename or 'price_per_m2_choropleth_map.html'
        price_map.save(map_filename)
        logging.info("Map has been saved as %s", map_filename)

    def create_choropleth_map_per_region_department(self, df, geojson_data, geojson_key, level):
        """
        Generate and save choropleth maps for specified regions or departments.
        """
        if level == "pays":
            self._create_country_map(df, geojson_data, geojson_key, level)
        elif level == "region":
            self._create_region_maps(df, geojson_data, geojson_key)
        elif level == "departement":
            self._create_department_maps(df, geojson_data, geojson_key)

    def _create_country_map(self, df, geojson_data, geojson_key, level):
        """
        Create a country-level map.
        """
        df_region_departments = df[df['region'].isin(self.scale_list)]
        geojson_filtered = geojson_data
        geojson_key = 'nom'
        map_filename = os.path.join(self.output_dir, 'price_per_m2_region_choropleth_map.html')
        self.create_choropleth_map(df_region_departments, geojson_filtered, geojson_key, level, map_filename)

    def _create_region_maps(self, df, geojson_data, geojson_key):
        """
        Create maps for each region.
        """
        for scale in self.scale_list:
            region_departments = self.display_scale_list(scale)
            if not region_departments:
                continue

            df_region_departments = df[df['departement'].isin(region_departments)]
            geojson_filtered = self._filter_geojson_by_departments(geojson_data, geojson_key, region_departments)

            if not df_region_departments.empty and geojson_filtered['features']:
                map_filename = os.path.join(self.output_dir,
                                            f'price_per_m2_{scale.replace(" ", "_")}_choropleth_map.html')
                self.create_choropleth_map(df_region_departments, geojson_filtered, geojson_key, "region", map_filename)

    def _create_department_maps(self, df, geojson_data, geojson_key):
        """
        Create maps for each department.
        """
        for scale in self.scale_list:
            region_departments = self.display_scale_list(scale)
            if not region_departments:
                continue

            for department_code in region_departments:
                #We need to filter the geojson if the commune start with the 'code' and strictly equal
                df_region_departments = df[df['commune'].str.startswith(department_code)]
                geojson_filtered = {
                    'type': 'FeatureCollection',
                    'features': [
                        feature for feature in geojson_data['features']
                        if feature['properties'][geojson_key].startswith(department_code)
                    ]
                }
                if not df_region_departments.empty and geojson_filtered['features']:
                    map_filename = os.path.join(
                        self.output_dir,
                        f'price_per_m2_per_department_'
                        f'{department_code.replace(" ", "_")}'
                        f'_choropleth_map.html')
                    self.create_choropleth_map(df_region_departments,
                                               geojson_filtered,
                                               geojson_key,
                                               "departement",
                                               map_filename)

    def _filter_geojson_by_departments(self, geojson_data, geojson_key, department_codes):
        """
        Filter GeoJSON data to include only specified department codes.
        """
        return {
            'type': 'FeatureCollection',
            'features': [
                feature for feature in geojson_data['features']
                if feature['properties'][geojson_key] in department_codes
            ]
        }

    def generate_maps(self):
        """
        Generate choropleth maps based on the data and configuration.
        """
        df_grouped = self.load_grouped_data(self.pickle_file)
        level = self.level
        with open(self.geojson_file, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        self.create_choropleth_map_per_region_department(df_grouped,
                                                         geojson_data,
                                                         geojson_key='code',
                                                         level=level)
