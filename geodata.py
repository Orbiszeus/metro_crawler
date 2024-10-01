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
def extract_points_data(data, category):
    points_data = list()

    for idx, row in data.iterrows():
        if row.geometry.geom_type == 'Point':
            coords = [row.geometry.y, row.geometry.x]
        elif row.geometry.geom_type == 'Polygon':
            coords = [row.geometry.centroid.y, row.geometry.centroid.x]
        else:
            continue

        name = row.get('name', False)

        if name:
            points_data.append({
                "name": name,
                "coordinates": coords
            })

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
