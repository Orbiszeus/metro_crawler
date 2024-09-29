import osmnx as ox
import geopandas as gpd
import folium


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
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Hybrid',
        name='Google Hybrid',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
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
