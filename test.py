from src.config import load_region_dept_commune_map
import folium
import numpy as np
import os
import json
from department import add_price_to_geojson,load_grouped_data
region_dept_commune_map = load_region_dept_commune_map()
regionsList = region_dept_commune_map.keys()

def create_choropleth_map_per_region(df, geojson_file, regions, geojson_key):
    """
    Create a choropleth map showing the average price per square meter by region,
    using a logarithmic scale to handle wide ranges of values.
    """
    output_dir = os.path.abspath('data/regions_maps')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Maps will be saved in: {output_dir}")

    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    for region in regions:
        departments = display_departments(region_dept_commune_map, region)
        if not departments:
            print(f"No departments found for region {region}, skipping...")
            continue
        department_codes = departments
        df_region = df[df['departement'].isin(department_codes)]
        print(df_region.head())

        # Filter GeoJSON features for the region's departments
        geojson_filtered = {
            'type': 'FeatureCollection',
            'features': [
                feature for feature in geojson_data['features']
                if feature['properties'][geojson_key] in department_codes
            ]
        }

        if not df_region.empty and geojson_filtered['features']:
            map_filename = os.path.join(output_dir, f'price_per_m2_{region.replace(" ", "_")}_choropleth_map.html')
            create_choropleth_map(
                df=df_region,
                geojson_file=geojson_filtered,
                level='region',
                geojson_key=geojson_key,
                map_filename=map_filename
            )
        else:
            print(f"No data available for region '{region}', skipping...")


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

def create_choropleth_map(df, geojson_file, level, geojson_key, map_filename=None):
    """
    Create a choropleth map showing the average price per square meter by the specified level,
    using a logarithmic scale to handle wide ranges of values.
    """
    if 'departement' in df.columns:
        df = df.rename(columns={'departement': 'code'})


    center_lat, center_lon = calculate_geojson_center(geojson_file)

    # Initialize the map
    price_map = folium.Map(location=[center_lat, center_lon], zoom_start=8)

    # Add the average price per m² to the GeoJSON data
    geojson_data = add_price_to_geojson(df, geojson_file, geojson_key)

    # Apply logarithmic transformation to the prices to compress the scale
    df['log_price_per_m2'] = np.log1p(df['average_price_per_m2'])
    print(df.head())

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





def display_departments(data, region_name):
    region = data.get(region_name)
    departmentsList = []
    if not region:
        print(f"Region '{region_name}' not found in the data.")
        return

    departments = region.get('departments', {})
    if not departments:
        print(f"No departments found in the region '{region_name}'.")
        return

    print(f"Departments in {region_name}:")
    for dept_name, dept_info in departments.items():

        dept_code = dept_info.get('code', 'N/A')
        departmentsList.append(dept_code)
    print(departmentsList)
    return departmentsList




def main():
    pickle_filename = os.path.join('data', 'prix_m2_par_departement.pkl')
    geojson_filename = os.path.join('data', 'departments.geojson')

    df_grouped = load_grouped_data(pickle_filename)

    # Load the GeoJSON file for departments
    with open(geojson_filename, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)



    # Create a choropleth map using 'code' to group by departments
    create_choropleth_map(df_grouped, geojson_data, 'departement', 'code')


    create_choropleth_map_per_region(df_grouped, geojson_filename, regionsList, geojson_key='code')


if __name__ == '__main__':
    main()




