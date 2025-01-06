import pandas as pd
import folium
import numpy as np
import os
import json

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
        code = feature['properties'][geojson_key]
        # Add the price to the feature s properties
        feature['properties']['average_price_per_m2'] = df_dict.get(code, None)

    return geojson_data

def create_choropleth_map(df, geojson_file, level, geojson_key, map_filename=None):
    """
    Create a choropleth map showing the average price per square meter by the specified level,
    using a logarithmic scale to handle wide ranges of values.
    """
    if 'commune' in df.columns:
        df = df.rename(columns={'commune': 'code'})

    center_lat, center_lon = 46.603354, 1.888334  # Center of France

    # Initialize the map
    price_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

    # Add the average price per m² to the GeoJSON data
    geojson_data = add_price_to_geojson(df, geojson_file, geojson_key)

    # Apply logarithmic transformation to the prices to compress the scale
    df['log_price_per_m2'] = np.log1p(df['average_price_per_m2'])

    # Define custom thresholds for color scaling based on logarithmic values
    thresholds = [df['log_price_per_m2'].min(), df['log_price_per_m2'].quantile(0.25),
                  df['log_price_per_m2'].quantile(0.5),
                  df['log_price_per_m2'].quantile(0.75), df['log_price_per_m2'].max()]

    # Create the choropleth map with logarithmic values
    choropleth = folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=df,
        columns=['code', 'log_price_per_m2'],
        key_on=f'feature.properties.{geojson_key}',
        fill_color='YlOrRd',  # Color scale from yellow to red
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Log of Price per m² (€)',
        threshold_scale=thresholds  # Custom thresholds based on the logarithmic scale
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

    # Save the map as an HTML file
    if map_filename is None:
        map_filename = f'price_per_m2_{level}_log_choropleth_map.html'
    price_map.save(map_filename)
    print(f"Map has been saved as {map_filename}")

    return map_filename



def extract_departments(df, geojson_file):
    """
    Extract unique department codes and optionally their names from the DataFrame or GeoJSON.
    """

    # Extract department names from GeoJSON
    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    departments = []
    for feature in geojson_data['features']:
        department_code = feature['properties']['code'][:2]
        nom = feature['properties']['nom']
        if not any(d['code'] == department_code for d in departments):
            departments.append({'code': department_code, 'name': nom})

    print(f"Found {len(departments)} departments")
    return departments
def save_departments_list(departments, output_file):
    """
    Save the list of departments to a JSON file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(departments, f, indent=2, ensure_ascii=False)
    print(f"Department list saved to {output_file}")

def create_choropleth_map_per_department(df, geojson_file, departments, geojson_key):
    """
    Create and save a separate choropleth map for each department.
    """
    # Ensure output directory exists
    output_dir = os.path.abspath('data/department_maps')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Maps will be saved in: {output_dir}")

    # Load the GeoJSON data once
    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)


    for department in departments:
        department_code = department['code']

        # Filter DataFrame for the department
        df_department = df[df['commune'].str.startswith(department_code)]

        # Filter GeoJSON features for the department
        geojson_filtered = {
            'type': 'FeatureCollection',
            'features': [
                feature for feature in geojson_data['features']
                if feature['properties'][geojson_key].startswith(department_code)
            ]
        }

        if not df_department.empty and geojson_filtered['features']:
            # Create the map for the department
            map_filename = os.path.join(output_dir, f'price_per_m2_department_{department_code}.html')
            create_choropleth_map(df_department, geojson_filtered, level='department', geojson_key=geojson_key, map_filename=map_filename)
        else:
            print(f"No data for department {department_code}, skipping...")



def main():
    pickle_filename = os.path.join('data', 'prix_m2_par_commune.pkl')
    geojson_filename = os.path.join('data', 'communes.geojson')
    geojson_filename_departements = os.path.join('data','departments.geojson')

    df_grouped = load_grouped_data(pickle_filename)


    # Load the GeoJSON file for departments
    with open(geojson_filename, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Create a choropleth map using 'code' to group by departments
    create_choropleth_map(df_grouped, geojson_data, 'communes', 'code')

    departments = extract_departments(df_grouped, geojson_filename_departements)
    save_departments_list(departments, 'departments.json')

    create_choropleth_map_per_department(df_grouped, geojson_filename, departments, geojson_key='code')


if __name__ == '__main__':
    main()