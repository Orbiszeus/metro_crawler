import requests
from curl_cffi import requests
import json
from urllib.parse import quote_plus

API_KEY = "AIzaSyDOwgj0fSYvgSNMXtWyxArmahvl-NPRQ00"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

async def hotel_serper_search(area):
    
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": f"{area} Agoda",
    "gl": "tr"
    })
    headers = {
    'X-API-KEY': '576de8f38665cad7feb185636d3d3754877a8e61',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    search_results = []
    
    for result in data['organic'][:1]:
        search_results.append(result['link'])
    
    return search_results

async def menu_serper_search(area):
    
    url = "https://google.serper.dev/search"
    
    payload_y = json.dumps({
    "q": f"{area} Yemeksepeti",
    "gl": "tr"
    })
    payload_g = json.dumps({
    "q": f"{area} Getir",
    "gl": "tr"
    })
    headers = {
    'X-API-KEY': '57f3e816568aee88361f0ec8bf46a98e121ac096',
    'Content-Type': 'application/json'
    }

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

def google_maps_search(search_query):
    encoded_query = quote_plus(search_query)
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={encoded_query}&key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    places = []
    for result in data['results']:
        place_info = {
            'name': result['name'],
            'address': result['formatted_address'],
            'location': result['geometry']['location'],
            'rating': result.get('rating', 'N/A')
        }
        places.append(place_info)
        print("There are " + str(len(places)) + " restaurants.")
    for place in places:
        print(place)
    return places
    