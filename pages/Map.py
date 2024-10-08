import streamlit as st
import streamlit.components.v1 as components
from geodata import (create_folium_markers, create_folium_map, restaurant_icon_generator, hotel_icon_generator,
                     coffee_icon_generator)
from repository import get_from_mongo
import websocket
import threading
import json 

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

ws = None
def on_message(ws, message):
    st.write(f"Received: {message}")

def on_error(ws, error):
    st.write(f"Error: {error}")

def on_close(ws):
    st.write("WebSocket closed")

def on_open(ws):
    st.write("WebSocket connection opened")

def run_websocket():
    global ws
    ws = websocket.WebSocketApp(
        "ws://0.0.0.0:8000/ws",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()

threading.Thread(target=run_websocket, daemon=True).start()

st.title("METRO ANALYST")
st.subheader("Map for Metro Analyst")

hotels = get_from_mongo("hotel", False)
restaurants = get_from_mongo("restaurant", False)
coffee = get_from_mongo("cafe", False)

total_markers_rest = len(restaurants)
total_markers_cafe = len(coffee)
total_markers_hotels = len(hotels)

markers = list()

markers.extend(create_folium_markers(hotels, "red", "bed", "Hotel", hotel_icon_generator))
markers.extend(create_folium_markers(restaurants, "green", "cutlery", "Restaurant", restaurant_icon_generator))
markers.extend(create_folium_markers(coffee, "blue", "coffee", "Coffee", coffee_icon_generator))

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

st.write("Total restaurant number: " + str(total_markers_rest))
st.write("Total hotel number: " + str(total_markers_hotels))
st.write("Total coffee shop number: " + str(total_markers_cafe))
