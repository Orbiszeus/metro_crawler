import streamlit as st
import requests
import streamlit.components.v1 as components
import json
import time
import os
from geodata import load_geodata, create_folium_markers, create_folium_map, create_folium_markers_from_json

# Set up Streamlit page configuration
st.set_page_config(page_title="Hotel Analyst", layout="wide")
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

if not st.session_state['authenticated']:
    st.subheader("You must log in to access this page.")
    st.stop()  # Stop the page from loading further

st.title("Test")
st.subheader("Map concept test")

bars = load_geodata("istanbul_bar.geojson")
restaurants = load_geodata("istanbul_restaurants.geojson")
coffee = load_geodata("istanbul_coffee.geojson")
hotels = load_geodata("istanbul_hotel.geojson")

markers = list()

# markers.extend(create_folium_markers(bars, "orange", "beer", "Bar"))
# markers.extend(create_folium_markers(coffee, "blue", "coffee", "Coffee"))
# markers.extend(create_folium_markers(hotels, "red", "bed", "Hotel"))
# markers.extend(create_folium_markers(restaurants, "green", "cutlery", "Restaurant"))
#markers.extend(create_folium_markers_from_json('restaurant_full_data.json', "green", "cutlery", "Restaurant"))
markers.extend(create_folium_markers_from_json("coffees_full_data.json", "blue", "coffee", "Coffee"))

map_html = create_folium_map(markers)

# Generate the HTML content with the API key dynamically
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Key Locations</title>
    <style>
        #map {{
            height: 100%;
            width: 100%;
        }}
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="map">
    {map_html}
    </div>
    
</body>
</html>
"""

# Render the HTML content in Streamlit
components.html(html_content, height=600)

