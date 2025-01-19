import os
import numpy as np
import pandas as pd
import folium
from config import load_region_dept_commune_map
import json

base_path = os.path.abspath('data')

class ChoroplethMapGenerator:

    LEVEL_MAP = {
        "pays" : "region",
        "region": "departement",
        "departement": "commune"
    }
    ZOOM_START_MAP = {
        "pays": 6,         # Suitable zoom level for a country
        "region": 7,       # Suitable zoom level for a region
        "departement": 9 # Suitable zoom level for a department
    }
    def __init__(self, pickle_file, geojson_file, level):
        self.pickle_file =pickle_file
        self.geojson_file = geojson_file
        self.scale_dept_commune_map = load_region_dept_commune_map()
        self.scale_list = self.scale_dept_commune_map.keys()
        self.output_dir = os.path.join(base_path, f'cleaned/{level}s_maps/')
        self.level = level
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def load_grouped_data(pickle_filename):
        """
        Load the preprocessed DataFrame from a pickle file (grouped by commune, departement, or region).
        """
        return pd.read_pickle(pickle_filename)

    @staticmethod
    def add_price_to_geojson(df, geojson_data, geojson_key):
        """
        Add the average price per m² from the DataFrame to the GeoJSON file.
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
        latitudes = []
        longitudes = []
        for feature in geojson_data['features']:
            geom = feature['geometry']
            geom_type = geom['type']
            coords = geom['coordinates']

            if geom_type == 'Polygon':
                for ring in coords:
                    for coord in ring:
                        lon, lat = coord
                        latitudes.append(lat)
                        longitudes.append(lon)
            elif geom_type == 'MultiPolygon':
                for polygon in coords:
                    for ring in polygon:
                        for coord in ring:
                            lon, lat = coord
                            latitudes.append(lat)
                            longitudes.append(lon)
            else:
                continue

        if latitudes and longitudes:
            center_lat = np.mean(latitudes)
            center_lon = np.mean(longitudes)
            return center_lat, center_lon
        else:
            # Default center if no coordinates are found
            return 46.603354, 1.888334  # Center of France

    def display_scale_list(self, scale_name):
        region_departement = self.scale_dept_commune_map.get(scale_name)
        print('scaleName : ', scale_name)
        scale = "departments"
        if not region_departement:
            print(f"Region '{scale_name}' not found in the data.")
            return []

        min_scale = region_departement.get(scale, {})
        if not min_scale:
            print(f"No departments found in the region '{scale_name}'.")
            return []

        print(f"Departments in {scale_name}:")
        return [dept_info.get('code', 'N/A') for dept_info in min_scale.values()]

    def create_choropleth_map(self, df, geojson_data, geojson_key, level, map_filename=None):
        """
        Create a choropleth map showing the average price per square meter by the specified level,
        using a logarithmic scale to handle wide ranges of values.
        """
        code = 'code'
        zoom_start = self.ZOOM_START_MAP.get(level, 8)
        if self.LEVEL_MAP[self.level] in df.columns:
            if(self.LEVEL_MAP[self.level]=="region"):
                df = df.rename(columns={self.LEVEL_MAP[self.level]: 'nom'})
                code = 'nom'
                print('code : ',code)
            else : df = df.rename(columns={self.LEVEL_MAP[self.level]: 'code'})
        df['log_price_per_m2'] = np.log1p(df['average_price_per_m2'])
        print("123 : ", df.head())
        print('code : ', code)
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
                aliases=[self.LEVEL_MAP[self.level]+' :', 'price per m²:'],
                localize=True,
                sticky=False,
                labels=True,
                style=("background-color: white; color: black; font-weight: bold;"),
            )
        ).add_to(price_map)
        map_filename = map_filename or 'price_per_m2_choropleth_map.html'
        price_map.save(map_filename)
        print(f"Map has been saved as {map_filename}")

    def create_choropleth_map_per_region_department(self, df, geojson_data, geojson_key, level):
        if (level == "pays"):
            df_region_departments = df[df['region'].isin(self.scale_list)]
            geojson_filtered = geojson_data
            geojson_key = 'nom'
            map_filename = os.path.join(self.output_dir,
                                        f'price_per_m2_region_choropleth_map.html')
            self.create_choropleth_map(df, geojson_filtered, geojson_key, level,
                                       map_filename)
        else :
            for scale in self.scale_list:
                region_departments = self.display_scale_list(scale)
                if not region_departments:
                    continue

                if (level == "region"):

                    df_region_departments = df[df['departement'].isin(region_departments)]
                    geojson_filtered = {
                        'type': 'FeatureCollection',
                        'features': [
                            feature for feature in geojson_data['features']
                            if feature['properties'][geojson_key] in region_departments
                        ]
                    }
                    print(df_region_departments.head())
                    if not df_region_departments.empty and geojson_filtered['features']:
                        map_filename = os.path.join(self.output_dir,
                                                                             f'price_per_m2_{scale.replace(" ", "_")}_choropleth_map.html')
                        self.create_choropleth_map(df_region_departments, geojson_filtered, geojson_key, level,
                                                   map_filename)

                elif (level == "departement"):
                    for department_code in region_departments:
                        df_region_departments = df[df['commune'].str.startswith(department_code)]
                        geojson_filtered = {
                            'type': 'FeatureCollection',
                            'features': [
                                feature for feature in geojson_data['features']
                                if feature['properties'][geojson_key].startswith(department_code)
                            ]
                        }
                        if not df_region_departments.empty and geojson_filtered['features']:
                            map_filename = os.path.join(self.output_dir,
                                                        f'price_per_m2_per_department_{department_code.replace(" ", "_")}_choropleth_map.html')
                            self.create_choropleth_map(df_region_departments, geojson_filtered, geojson_key, level, map_filename)
                        else:
                            print(f"No data for department {department_code}, skipping...")





    def generate_maps(self):
        df_grouped = self.load_grouped_data(self.pickle_file)
        level = self.level
        with open(self.geojson_file, 'r', encoding='utf-8')as f:
            geojson_data = json.load(f)
        self.create_choropleth_map_per_region_department(df_grouped,geojson_data,geojson_key='code', level=level)

