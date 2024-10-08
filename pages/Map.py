import streamlit as st
import streamlit.components.v1 as components
from geodata import (create_folium_markers, create_folium_map, restaurant_icon_generator, hotel_icon_generator,
                     coffee_icon_generator)
from repository import get_from_mongo
import time
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
        div[data-testid="stToolbar"] {visibility: hidden;} /* Hide the stToolbar */
    </style>
""", unsafe_allow_html=True)

if not st.session_state['authenticated']:
    st.subheader("You must log in to access this page.")
    st.stop()  # Stop the page from loading further

st.title("METRO ANALYST")
st.subheader("Dive into Our Interactive Map Featuring Top Restaurants Cafés, and Hotels!")


with st.spinner('Loading map...'):  
    time.sleep(10)
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

if not st.session_state['authenticated']:
    st.warning("Your session has expired. Please log in again!",  icon="⚠️")
