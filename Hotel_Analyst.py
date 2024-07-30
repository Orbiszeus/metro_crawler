import streamlit as st
import requests
import streamlit.components.v1 as components
import json
import time
import os

# Set up Streamlit page configuration
st.set_page_config(page_title="Hotel Analyst", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

# Set the title and subtitle
st.title("AI Analysts for Hotels")
st.subheader("Please choose your hotel area.")

# Function to run the menu crawler script
api_key = os.getenv('GOOGLE_MAPS_API_KEY')  # Read API key from environment variable

# Create a form
with st.form(key='my_form'):  
    hotel_area_opt = ["Istanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Çanakkale"]
    hotel_area = st.selectbox("", hotel_area_opt, index=0)
    submit_button = st.form_submit_button(label='Submit')

    if submit_button: 
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        percent_complete = 0
        increment = 1

        while percent_complete < 100:
            time.sleep(0.1)  
            percent_complete += increment
            my_bar.progress(min(percent_complete, 100), text=progress_text)
            if percent_complete % 10 == 0:
                response = requests.post(f"http://0.0.0.0:8000/crawl_hotels?hotel_area={hotel_area}")
                my_bar.progress(percent_complete, text="Operation completed.")
                if response.status_code == 200:
                    data = response.json()
                    percent_complete = 100 
                    my_bar.progress(percent_complete, text="Operation completed.")
                    break
        time.sleep(1)
        my_bar.empty()            

        if response.status_code == 200:
            data = response.json()
            st.write("Crawling Hotels..")
        else:
            st.write("An error occurred. Please try again.")

# Read hotel data from JSON file
json_file_path = 'hotel_data.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
    hotel_data = json.load(file)

hotel_data_json = json.dumps(hotel_data)

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
    <div id="map"></div>
    <script type="text/javascript">
        var hotelData = {hotel_data_json};

        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 10,
                center: {{ lat: 41.059, lng: 28.97927 }}
            }});
            
            if (!hotelData || hotelData.length === 0) {{
                console.log("No hotel data available.");
                return;
            }}

            var validData = hotelData.filter(place => place['Total Room Number'] && place.coordinates &&
                typeof place.coordinates.latitude === 'number' && 
                !isNaN(place.coordinates.latitude) &&
                typeof place.coordinates.longitude === 'number' && 
                !isNaN(place.coordinates.longitude))
                .map(place => {{
                    return {{
                        ...place,
                        'Total Room Number': Number(place['Total Room Number']) || 0
                    }};
                }});

            if (validData.length === 0) {{
                console.log("No valid hotel data available.");
                return;
            }}

            var maxRooms = Math.max(...validData.map(place => place['Total Room Number']));
            console.log("Max Rooms:", maxRooms);

            if (isNaN(maxRooms) || maxRooms === 0) {{
                console.log("Invalid maxRooms value.");
                return;
            }}

            validData.forEach(place => {{
                if (place.coordinates && 
                    typeof place.coordinates.latitude === 'number' && 
                    !isNaN(place.coordinates.latitude) &&
                    typeof place.coordinates.longitude === 'number' && 
                    !isNaN(place.coordinates.longitude)) {{
                    
                    var numberOfRooms = place['Total Room Number'] || 0;
                    var radius = scaleRadius(numberOfRooms/5, maxRooms);

                    var circle = new google.maps.Circle({{
                        map: map,
                        radius: radius,
                        fillColor: '#FF0000',
                        fillOpacity: 0.35,
                        strokeColor: '#FF0000',
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        center: {{ lat: place.coordinates.latitude, lng: place.coordinates.longitude }}
                    }});
                    
                    var infoWindow = new google.maps.InfoWindow();
                    circle.addListener('click', function () {{
                        var contentString = generateContentString(place);
                        infoWindow.setContent(contentString);
                        infoWindow.setPosition(circle.getCenter());
                        infoWindow.open(map);
                    }});
                }} else {{
                    console.log("Invalid coordinates for place:", place);
                }}
            }});
        }}

        function scaleRadius(numberOfRooms, maxRooms) {{
            var maxRadius = 2000;
            var minRadius = 500;
            return minRadius + (numberOfRooms / maxRooms) * (maxRadius - minRadius);
        }}

        function generateContentString(place) {{
            var content = '<div><strong>' + (place['Hotel Name'] || 'No Name') + '</strong><br>';

            for (var key in place) {{
                if (place.hasOwnProperty(key) && key !== 'coordinates') {{
                    var value = place[key];
                    
                    if (Array.isArray(value)) {{
                        content += '<div><strong>' + key + ':</strong><ul>';
                        value.forEach(item => {{
                            if (typeof item === 'object') {{
                                content += '<li><div><strong>Details:</strong><br>' + formatObject(item) + '</div></li>';
                            }} else {{
                                content += '<li>' + item + '</li>';
                            }}
                        }});
                        content += '</ul></div><br>';
                    }} else if (typeof value === 'object') {{
                        content += '<div><strong>' + key + ':</strong><br>' + formatObject(value) + '</div><br>';
                    }} else {{
                        content += '<div><strong>' + key + ':</strong> ' + value + '</div><br>';
                    }}
                }}
            }}

            content += '</div>';
            return content;
        }}

        function formatObject(obj) {{
            var formatted = '';
            for (var prop in obj) {{
                if (obj.hasOwnProperty(prop)) {{
                    var value = obj[prop];
                    
                    if (Array.isArray(value)) {{
                        formatted += '<div><strong>' + prop + ':</strong><ul>';
                        value.forEach(item => {{
                            formatted += '<li>' + (typeof item === 'object' ? formatObject(item) : item) + '</li>';
                        }});
                        formatted += '</ul></div>';
                    }} else if (typeof value === 'object') {{
                        formatted += '<div><strong>' + prop + ':</strong><br>' + formatObject(value) + '</div>';
                    }} else {{
                        formatted += '<div><strong>' + prop + ':</strong> ' + value + '</div>';
                    }}
                }}
            }}
            return formatted;
        }}
    </script>
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDOwgj0fSYvgSNMXtWyxArmahvl-NPRQ00&callback=initMap&libraries=places">
    </script>
</body>
</html>
"""

# Render the HTML content in Streamlit
components.html(html_content, height=600)

