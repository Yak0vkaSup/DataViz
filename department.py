import pandas as pd
import folium
import numpy as np
import os
import json
from src.config import load_region_dept_commune_map

region_dept_commune_map = load_region_dept_commune_map()

def load_grouped_data(pickle_filename):
    """
    Load the preprocessed DataFrame from a pickle file (grouped by commune, departement, or region).
    """
    return pd.read_pickle(pickle_filename)

def add_price_to_geojson(df, geojson_data, geojson_key):
    """
    Add the average price per m² from the DataFrame to the GeoJSON file.
    """

    # Convert the DataFrame to a dictionary for easy lookup
    df_dict = df.set_index(geojson_key)['average_price_per_m2'].to_dict()

    # Loop through each feature in the GeoJSON file and add the price per m²
    for feature in geojson_data['features']:
        department_code = feature['properties'][geojson_key]
        # Add the price to the feature's properties if the department exists in the DataFrame
        feature['properties']['average_price_per_m2'] = df_dict.get(department_code, None)

    return geojson_data

def create_choropleth_map(df, geojson_file, level, geojson_key):
    """
    Create a choropleth map showing the average price per square meter by the specified level,
    using a logarithmic scale to handle wide ranges of values.
    """

    for region in region_dept_commune_map.keys():
        departments = region_dept_commune_map[region]['departments']
        for department in departments:
            if 'departement' in df.columns:
                df = df.rename(columns={'departement': 'code'})
            center_lat, center_lon = 46.603354, 1.888334

            # Initialize the map
            price_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

            # Add the average price per m² to the GeoJSON data
            geojson_data = add_price_to_geojson(df, geojson_file, geojson_key)
            df['log_price_per_m2'] = np.log1p(df['average_price_per_m2'])

            thresholds = [df['log_price_per_m2'].min(), df['log_price_per_m2'].quantile(0.25),
                          df['log_price_per_m2'].quantile(0.5),
                          df['log_price_per_m2'].quantile(0.75), df['log_price_per_m2'].max()]

            choropleth = folium.Choropleth(
                geo_data=geojson_data,
                name='choropleth',
                data=df,
                columns=['code', 'log_price_per_m2'],
                key_on=f'feature.properties.{geojson_key}',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Log of Price per m² (€)',
                threshold_scale=thresholds
            ).add_to(price_map)

            # Add tooltips that show the actual price per m² when hovering over a department
            folium.GeoJson(
                geojson_data,
                style_function=lambda feature: {
                    'fillColor': '#ffffff00',
                    'color': 'transparent',
                    'weight': 0,
                    'fillOpacity': 0,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['code', 'average_price_per_m2'],
                    aliases=['Department:', 'Price per m²:'],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style=("background-color: white; color: black; font-weight: bold;"),
                )
            ).add_to(price_map)

            map_filename = f'price_per_m2_{level}_log_choropleth_map.html'
            price_map.save(map_filename)
            print(f"Map has been saved as {map_filename}")

            return map_filename

def create_choropleth_map_per_region(df, geojson_file, departments, geojson_key):
    """
    Create and save a separate choropleth map for each department.
    """

    output_dir = os.path.abspath('data/department_maps')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Maps will be saved in: {output_dir}")

    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)


    for department in departments:
        department_code = department['code']

        df_department = df[df['commune'].str.startswith(department_code)]

        geojson_filtered = {
            'type': 'FeatureCollection',
            'features': [
                feature for feature in geojson_data['features']
                if feature['properties'][geojson_key].startswith(department_code)
            ]
        }

        if not df_department.empty and geojson_filtered['features']:
            map_filename = os.path.join(output_dir, f'price_per_m2_department_{department_code}.html')
            create_choropleth_map(df_department, geojson_filtered, level='department', geojson_key=geojson_key, map_filename=map_filename)
        else:
            print(f"No data for department {department_code}, skipping...")



def main():

    pickle_filename = os.path.join('data', 'prix_m2_par_departement.pkl')
    geojson_filename = os.path.join('data', 'departments.geojson')
    df_grouped = load_grouped_data(pickle_filename)
    print(df_grouped.head())

    with open(geojson_filename, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    create_choropleth_map(df_grouped, geojson_data, 'departement', 'code')

if __name__ == '__main__':
    main()
