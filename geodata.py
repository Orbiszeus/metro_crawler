import os
import osmnx as ox
import geopandas as gpd
import folium
import json
from geopy.geocoders import Nominatim
import googlemaps

# Methods for download and load geojson data
def download_geodata(city_name, tags, filename=None):
    """
    tags = {'amenity': 'cafe'}
    tags = {'amenity': 'restaurant'}
    tags = {'tourism': 'hotel'}
    """
    geodata = ox.geometries_from_place(city_name, tags)

    if geodata.empty:
        print("No geodata found.")
        return None
    if filename is not None:
        geodata.to_file(f"data/{filename}.geojson", driver='GeoJSON')

    return geodata


def load_geodata(filename):
    data = gpd.read_file(f"data/{filename}")
    return data


# Method for extract usefull data from geojson and store in json
def extract_points_data(data, category, properties=None):
    points_data = list()

    for idx, row in data.iterrows():
        row_data = dict()
        if row.geometry.geom_type == 'Point':
            coords = [row.geometry.y, row.geometry.x]
        elif row.geometry.geom_type == 'Polygon':
            coords = [row.geometry.centroid.y, row.geometry.centroid.x]
        else:
            continue

        name = row.get('name', None)

        if name is not None:
            row_data['name'] = name
            row_data['coordinates'] = coords
        else:
            continue

        if properties is not None:
            properties_list = dict()

            for prop in properties:
                _ = row.get(prop, None)

                if _ is not None:
                    properties_list[prop] = _

            if properties_list:
                row_data['properties'] = properties_list

        if row_data:
            points_data.append(row_data)

    if points_data:
        with open(f'data/{category}_data.json', 'w') as json_file:
            json.dump(points_data, json_file, indent=4)

    return points_data


# Method for get the useful data from json
def get_category_data(category):
    """
    Method for get the data from a category.

    Attributes:
        category (str): the category name. The categories available are:
                        bar
                        coffee
                        hotel
                        restaurants

    Example:
            >>> get_category_data('coffee')

    Returns:
        list(): returns a list of dictionaries with the category data with this shape:
                [
                    {
                        "name": "Arkaoda",
                        "coordinates": [
                            40.98659,
                            29.0265392
                        ]
                    },
                ]
    """
    try:
        with open(f'data/{category}_data.json', 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        return list()


# Methods for create folium markers and map
def create_folium_markers(data, color, icon, category=None):
    marker_list = list()
    group = None

    if category is not None:
        group = folium.FeatureGroup(name=category)

    for idx, row in data.iterrows():
        if row.geometry.geom_type == 'Point':
            coords = [row.geometry.y, row.geometry.x]
        elif row.geometry.geom_type == 'Polygon':
            coords = [row.geometry.centroid.y, row.geometry.centroid.x]
        else:
            continue

        name = row.get('name', 'Unnamed')
        address = row.get('addr:full', 'No Address Provided')

        popup_content = f"""
                        <strong>{name}</strong><br>
                        <p>{address}</p>
                        """

        _ = folium.Marker(
                location=coords,
                popup=folium.Popup(popup_content, max_width=400),
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
                )
        if group is not None:
            _.add_to(group)
        else:
            marker_list.append(_)

    if group is not None:
        marker_list.append(group)

    return marker_list


def create_popup_content(data):
    html_content = "<div style='width: 250px; max-height: 200px; overflow-y: auto;'>"

    for key, value in data.items():
        if key != 'coordinates':  # Excluir las coordenadas del popup
            if key == "Cafe Name" or key == "Rating":  # Para claves 'Cafe Name' y 'Rating', mostrar valores al lado
                html_content += f"<strong>{key}:</strong> {value}<br>"

            # Verificar si el valor es una lista (para el menú)
            if isinstance(value, list):
                if key == "Menu":
                    html_content += "<ul>"  # Lista HTML para el menú
                    for item in value:
                        html_content += "<li>"
                        for sub_key, sub_value in item.items():
                            html_content += f"<strong>{sub_key}:</strong> {sub_value}<br>"
                        html_content += "</li>"
                    html_content += "</ul>"

    html_content += "</div>"
    return html_content


def create_folium_markers_from_json(filename, color, icon, category=None):
    with open(f"data/{filename}", 'r') as f1:
        json_data = json.load(f1)

    marker_list = list()
    group = None

    if category is not None:
        group = folium.FeatureGroup(name=category)
    count = 0
    for data in json_data:
        coords = data['coordinates']
        count += 1
        popup_content = create_popup_content(data)

        _ = folium.Marker(
            location=coords,
            popup=folium.Popup(popup_content, max_width=400),
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        )
        if group is not None:
            _.add_to(group)
        else:
            marker_list.append(_)

    if group is not None:
        marker_list.append(group)
    print(count)
    return marker_list


def create_folium_map(markers, filename="",save=False):
    map_center = [41.0082, 28.9784]  # Coordinates for Istanbul
    m = folium.Map(location=map_center, zoom_start=12)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&hl=tr&x={x}&y={y}&z={z}',
        attr='Google Hybrid',
        name='Google Hybrid',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&hl=tr&x={x}&y={y}&z={z}',
        attr='Google Maps',
        name='Google Streets',
        overlay=False,
        control=True
    ).add_to(m)

    for marker in markers:
        marker.add_to(m)

    folium.LayerControl().add_to(m)

    map_html = m._repr_html_()

    if save:
        m.save(filename)

    return map_html


# Methods to get address from coordinates
def get_nominatim_address_from_coords(coordinates):
    """
        Given a pair of coordinates, return the address as a string.

        Args:
            coordinates(list): a pair of coordinates latitude and longitude.
                                [lat, lng]

        Example:
            >>> get_nominatim_address_from_coords([41.0033, 28.9777])

        Returns:
            str: The address corresponding to the coordinates.

        Raises:
            ValueError: If the address could not be found.
    """
    geolocator = Nominatim(user_agent="geoapiTestForTurkie")

    location = geolocator.reverse(coordinates, exactly_one=True)

    if location:
        return location.address
    else:
        raise ValueError("Address could not be found for the given coordinates")


def get_googlemaps_address_from_coords(coordinates):
    """
        Given a pair of coordinates, return the address as a string.

        Args:
            coordinates(list): a pair of coordinates latitude and longitude.
                                [lat, lng]

        Example:
            >>> get_googlemaps_address_from_coords([41.0033, 28.9777])

        Returns:
            str: The address corresponding to the coordinates.

        Raises:
            ValueError: If the address could not be found.
        """
    api_key = "AIzaSyDOwgj0fSYvgSNMXtWyxArmahvl-NPRQ00"
    gmaps = googlemaps.Client(key=api_key)

    reverse_geocode_result = gmaps.reverse_geocode(coordinates)

    if reverse_geocode_result:
        return reverse_geocode_result[0]['formatted_address']
    else:
        raise ValueError("Address could not be found for the given coordinates")


# Method for join data from two json using different keys
def join_data(file_1, file_2, join_value_1, join_value_2, filename):
    with open(file_1, 'r') as f1:
        json_1 = json.load(f1)

    with open(file_2, 'r') as f2:
        json_2 = json.load(f2)

    result = list()
    for data_1 in json_1:
        for data_2 in json_2:
            if data_1[join_value_1] == data_2[join_value_2]:
                combined_data = {**data_1, **data_2}
                result.append(combined_data)

    for item in result:
        item.pop(join_value_2, None)

    with open(f'{filename}.json', 'w') as f_out:
        json.dump(result, f_out, indent=4)


# if __name__ == "__main__":
#     city_name = "Beyoglu, Istanbul. Turkey"
#     data = load_geodata("Beyoglu, Istanbul. Turkey_restaurants.json.geojson")
#     extract_points_data(data, 'restaurants_Beyoglu', ["cuisine", "website"])
#
#     join_data('hotel_data.json', 'data/hotels_Beyoglu_data.json','Hotel Name', 'name',
#               'hotels_full_data')
#
#     join_data('cafe_data.json', 'data/coffee_data.json','Cafe Name', 'name',
#               'coffees_full_data')
