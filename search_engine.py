import requests
import json
from urllib.parse import quote_plus
import time 
from geopy.geocoders import GoogleV3

API_KEY = "AIzaSyDOwgj0fSYvgSNMXtWyxArmahvl-NPRQ00"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

async def hotel_serper_search(area):
    
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": f"Agoda İstanbul {area} ",
    "gl": "tr"
    })
    headers = {
    'X-API-KEY': '57f3e816568aee88361f0ec8bf46a98e121ac096',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    search_results = []
    
    for result in data['organic'][:1]:
        search_results.append(result['link'])
    
    return search_results

async def menu_serper_search(area, company):

    url = "https://google.serper.dev/search"
    headers = {
    'X-API-KEY': '57f3e816568aee88361f0ec8bf46a98e121ac096',
    'Content-Type': 'application/json'
    } 
    if company == "g":
 
        payload_g = json.dumps({
        "q": f"{area} Getir",
        "gl": "tr"
        })
        response = requests.request("POST", url, headers=headers, data=payload_g)
        
        data = response.json()
        search_results = []
        first_two_items = data["organic"][:2]

        for index, item in enumerate(first_two_items, 1):
            if "marka" in item.get('link'):
                print(f"  Link: {item.get('link')}")
                continue
            else:
                search_results.append(item.get('link'))
            
        return search_results
    
    if company == "y":
        payload_y = json.dumps({
        "q": f"{area} Yemeksepeti",
        "gl": "tr"
        })
        response = requests.request("POST", url, headers=headers, data=payload_y)
        data = response.json()
        search_results = []

        for result in data['organic'][:1]:
            search_results.append(result['link'])

        return search_results
    
async def get_coordinates(address):
    geolocator = GoogleV3(api_key="AIzaSyCA8FOwQt4JhWVrLzJVJaJqbEwQgTLpRvM")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None, None
    
def google_maps_search(search_query):
    encoded_query = quote_plus(search_query)
    base_url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={encoded_query}&key={API_KEY}'
    places = []

    url = base_url
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            # Extract place information
            for result in data.get('results', []):
                place_info = {
                    'name': result.get('name'),
                    'address': result.get('formatted_address'),
                    'location': result.get('geometry', {}).get('location'),
                    'rating': result.get('rating', 'N/A')
                }
                places.append(place_info)

            # Check if there is a next_page_token for more results
            next_page_token = data.get('next_page_token')
            if next_page_token:
                # Google requires a short delay before requesting the next page
                time.sleep(2)  # Delay to allow token activation
                url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={next_page_token}&key={API_KEY}'
            else:
                break
        else:
            print(f"Error fetching data: {response.status_code}")
            break

    print(f"There are {len(places)} results found.")
    for place in places:
        print(place)
    
    return places
    