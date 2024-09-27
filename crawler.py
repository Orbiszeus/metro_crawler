import requests
import logging
import json
import pandas as pd
from seleniumbase import SB
from curl_cffi import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import re
from pymongo import MongoClient
from geopy.geocoders import GoogleV3
import os 
import pdb
import json
import pandas as pd
import re
import certifi
import asyncio
from selenium.webdriver.common.keys import Keys

GOOGLE_MAPS_QUERY = "https://www.google.com/maps/search/?api=1&query={}&query_place_id={}"
connection = "mongodb+srv://baris_ozdizdar:ZhcyQqCIwQMS8M29@metroanalyst.thli7ie.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE&appName=MetroAnalyst"
client = MongoClient(connection, tlsCAFile=certifi.where())

app = FastAPI()

db = client["MetroAnalyst"]
hotel_collection = db["hotels"]
restaurants_collection = db["restaurants"]

api_key = os.getenv('GOOGLE_MAPS_API_KEY')

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

class CrawlRequest(BaseModel):
    area: str = Field(default=None, description="The area to search for restaurants")
    restaurant: str = Field(default=None, description="The specific restaurant to search for")
    
class HotelCrawlRequest(BaseModel):
    hotel_area: str = Field(default=None, description="The area to search for hotels")


async def hotel_crawler(url):
    hotel_items = []
    with SB(uc=True, headless=False) as sb:
        sb.driver.uc_open_with_reconnect(url, 10) 
        try:
            sb.sleep(5)
            # sb.uc_gui_handle_cf() --> this method is used only if there is CF involved
            print("Locale code:" + str(sb.get_locale_code()))
            print(sb.get_title())
            sb.click("button[data-element-name='search-button']")
            sb.sleep(5)
            first_tab_handle = sb.driver.current_window_handle
            hotel_counter = 0 #number of hotels we want to crawl on single go.
            sb.sleep(1)
            current_url = sb.get_current_url()
            if "tr-tr" not in current_url:
                try:
                    sb.click("div[data-element-name='language-container-selected-language']")
                    sb.click("div[data-value='tr-tr']")
                    sb.sleep(5)           
                except:
                    print("Language change to Turkish is not working!") 
            try:
                sb.sleep(2)
                sb.scroll_to("css selector", "button[id='paginationNext']")
                sb.sleep(2)
                sb.scroll_to_bottom()
            except:
                print("One page search or scroll failed.")
            sb.sleep(1)
            #TODO: Add the page by page crawling by clicking "next"
            #While (True), then --> when the loops it will click next
            #There will be always a grid until there is no more "click next button"
            #There will be an infinitive loop
            while (True): 
                try:   
                    sb.scroll_to("css selector", "button[id='paginationNext']")
                    sb.sleep(2)
                    sb.scroll_to_bottom()
                except:
                    print("One page search or scroll failed.")
                sb.sleep(2)
                grid_items = sb.find_elements("div[data-element-name='PropertyCardBaseJacket']")
                total_grid_item = len(grid_items)
                print("Total grid number: " + str(total_grid_item))
                if grid_items:
                    for index, item in enumerate(grid_items):
                        hotel_items = []
                        sb.sleep(1)
                        try:
                            sb.click_nth_visible_element("div[data-element-name='PropertyCardBaseJacket'] a", index + 1)
                        except:
                            continue
                        sb.sleep(4)
                        all_facility_restaurant_details = []
                        hotel_name = ""
                        hotel_location = ""
                        hotel_rating = ""
                        restaurant_in_hotel_count = "0"
                        total_room_number = "0"
                        breakfast_price = "0 EUR"
                        total_bar_number = "0"
                        rooms_with_breakfast_number = "0"
                        breakfast_types_list = []
                        try:
                            hotel_name_elements = sb.find_elements("css selector", "h2[data-selenium='hotel-header-name'], p[data-selenium='hotel-header-name']")
                            if hotel_name_elements:
                                hotel_name = hotel_name_elements[0].text
                                print("Hotel Name: " + str(hotel_name))
                            existing_hotel = hotel_collection.find_one({"Hotel Name": hotel_name})
                            if existing_hotel:
                                print(f"Hotel '{hotel_name}' already exists in the database.")
                                continue
                        except:
                            hotel_name = "N/A"
                        try:
                            hotel_location = sb.find_element("css selector", "span[data-selenium='hotel-address-map']").text
                        except:
                            hotel_location = "N/A"

                        try:
                            hotel_rating = sb.find_element("css selector", "span[class='sc-jrAGrp sc-kEjbxe fzPhrN ehWyCi']").text
                        except:
                            hotel_rating = "N/A"

                        try:
                            parent_breakfasts_room_count = sb.find_element("css selector", "div[data-selenium='RoomGridFilter-filterGroup']")
                            all_divs = parent_breakfasts_room_count.find_elements("css selector", "div.Box-sc-kv6pi1-0.hRUYUu")
                            for div in all_divs:
                                label_span = div.find_element("css selector", "div.Box-sc-kv6pi1-0.dSOQsp")
                                if label_span.text == "Kahvaltı dahil":
                                    number_span = div.find_element("css selector", "div.Box-sc-kv6pi1-0.jJvGxG")
                                    rooms_with_breakfast_number_raw = number_span.text
                                    pattern = r'\((\d+)\)'
                                    match = re.search(pattern, rooms_with_breakfast_number_raw)
                                    if match:
                                        rooms_with_breakfast_number = match.group(1)
                                        break
                        except:
                            rooms_with_breakfast_number = "0"

                        try:
                            parent_restaurant_count = sb.find_element("css selector", "div[data-element-name='about-hotel-useful-info']")
                            all_divs = parent_restaurant_count.find_elements("css selector", "div.Box-sc-kv6pi1-0.hRUYUu")
                            for div in all_divs:
                                label_span = div.find_element("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.gwICfd")
                                if label_span.text == "Restoran Sayısı":
                                    try:
                                        number_span = div.find_element("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.kkSkZk")
                                        restaurant_in_hotel_count = number_span.text
                                        print("Restaurant Count: " + restaurant_in_hotel_count)
                                    except:
                                        restaurant_in_hotel_count = "0"
                                        
                                if label_span.text == "Oda Sayısı":
                                    try:
                                        number_span = ""
                                        number_span += div.find_element("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.kkSkZk").text
                                        if len(number_span) == 0:
                                            pattern = r"toplam (\d+) oda seçeneği mevcut:"
                                            
                                            number_span += div.find_element("css selector", "span.RoomGrid-titleCounterNormal > span").text
                                            match = re.search(pattern, number_span)
                                            if match:
                                                number = match.group(1)
                                                total_room_number = str(number)
                                                
                                        total_room_number = number_span
                                        print("Room Count: " + total_room_number)
                                    except:
                                        total_room_number = "0"
                                        
                                if label_span.text == "Bar/loca sayısı":
                                    try:        
                                        number_span = div.find_element("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.kkSkZk")
                                        total_bar_number = number_span.text
                                        print("Bar Count: " + total_bar_number)
                                    except:
                                        total_bar_number = "0"
                                        
                                if label_span.text == "Kahvaltı Ücreti (oda fiyatına dahil değilse)":
                                    try:
                                        number_span = div.find_element("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.kkSkZk")
                                        breakfast_price = number_span.text
                                        print("Breakfast Price: " + breakfast_price)
                                    except:
                                        breakfast_price = "0"
                        except Exception as e:
                            print(e)

                        try:
                            sb.sleep(2)
                            parent_restaurant_details = sb.find_elements("css selector", "div[id='abouthotel-restaurant']")
                            if parent_restaurant_details:
                                try:
                                    breakfast_details = sb.find_element("css selector", "ul[data-element-name='breakfast-options']")
                                    breakfast_options_lis = breakfast_details.find_elements("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.gwICfd.kite-js-Span")
                                    for breakfast_types in breakfast_options_lis:
                                        breakfast_types_list.append(breakfast_types.text)
                                except:
                                    breakfast_types = "Otelin içerisinde kahvaltı içeriği bilgisi yer almıyor."                            
                                    
                            # all_divs = parent_restaurant_details.find_elements("css selector", "div.Box-sc-kv6pi1-0.dtSdUZ")
                                # for div in parent_restaurant_details:
                                try:
                                    restaurant_divs = sb.find_elements("css selector", "div[data-element-name='restaurants-on-site']")
                                    if restaurant_divs:
                                        for rests in restaurant_divs:
                                            try:
                                                restaurant_in_hotel_count += 1
                                                restaurant_name = rests.find_element("css selector", "h5.sc-jrAGrp.sc-kEjbxe.bmFdwl.kGfVSb").text
                                            except:
                                                restaurant_name = "Otelin içerisinde restoran bulunmuyor."
                                            try:
                                                pattern = r'Mutfak:(.*)'
                                                kitchen_name = div.find_element("css selector", "div.a9733-box.a9733-fill-inherit.a9733-text-inherit.a9733-items-center.a9733-inline-flex").text
                                                match = re.search(pattern, kitchen_name)
                                                if match:
                                                    kitchen_name = match.group(1).strip()
                                                else:
                                                    print("No match found")
                                            except: 
                                                kitchen_name = "Mutfak bilgisi içeriği yer almıyor."
                                    
                                            facility_restaurant_details = {
                                                "Restaurant Name": restaurant_name,
                                                "Kitchen": kitchen_name + " Mutfağı",
                                                "Menu" : "A la carte"
                                            }
                                            all_facility_restaurant_details.append(facility_restaurant_details)
                                except:
                                    print("No restaurant details are present.")
                                    # break
                                facility_restaurant_details["Breakfast Options"] =  breakfast_types_list
                        except Exception as e:
                            print(e)

                        latitude, longitude = await get_coordinates(hotel_location)

                        hotel_item = {
                            "Hotel Name": hotel_name,
                            "Hotel Rating": hotel_rating,
                            "Hotel Location": hotel_location,
                            "Total Room Number": total_room_number,
                            "Total Restaurant Number": restaurant_in_hotel_count,
                            "Total Bar Number": total_bar_number,
                            "Breakfast Price" : breakfast_price,
                            "Total Number of Rooms with Breakfast": rooms_with_breakfast_number,
                            "Menu and Restaurant Details: " : all_facility_restaurant_details,
                            "coordinates" : {
                                "latitude" : latitude if latitude is not None else 0.0,
                                "longitude": longitude if longitude is not None else 0.0
                            }
                        }
                        
                        result = hotel_collection.insert_one(hotel_item)
                        print(f"Document inserted with ID: {result.inserted_id}")
                        sb.sleep(1)
                        sb.driver.switch_to.window(first_tab_handle)
                    if (sb.is_element_present("css selector", "button[id='paginationNext']")):
                        sb.click("css selector", "button[id='paginationNext']") 
                    else: # Breaking out of the while loop as there is no more next page to crawl 
                        break 
        except Exception as e:
            print(f"Exception: {e}")
    return get_from_mongo("hotel")

async def get_from_mongo(collection_name):
    output_file = ""
    if collection_name == "hotel":
        cursor = hotel_collection.find({}, {'_id': 0}) 
        documents = list(cursor)
        documents_json = json.dumps(documents, ensure_ascii=False, indent=4)
        output_file += "hotel_data.json"

    if collection_name == "restaurant":
        cursor = restaurants_collection.find({}, {'_id': 0}) 
        documents = list(cursor)
        documents_json = json.dumps(documents, ensure_ascii=False, indent=4)
        output_file += "restaurant_data.json"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(documents_json)
    # client.close()
    
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

@app.post("/crawl_menu")
async def crawler_endpoint(request: CrawlRequest):
    try:
        area = ""
        is_area = True
        if request.area:
            area += request.area
        elif request.restaurant:
            area += request.restaurant    
            is_area = False
        serper_y_results = await menu_serper_search(area)
        for url in serper_y_results:
            # df_json = await y_crawler(url, is_area, area)
            df_json = await g_crawler(url, is_area, area)
            if df_json:
                return {"dataframe": df_json,
                        "url": url}
            else:
                return {"error": "Crawling failed"}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
    
@app.post("/crawl_hotels")
async def hotel_crawl_api(hotel_area: str):
    try:
        if not hotel_area:
            raise HTTPException(status_code=400, detail="Hotel area is required")
        search_url = f"https://www.agoda.com/tr-tr/city/{hotel_area}-tr.html"
        await hotel_crawler(search_url)
        results = await get_from_mongo()
        if not results:
            raise HTTPException(status_code=404, detail="No data found in MongoDB")
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")


async def extract_menu_single(sb):
    '''Helper function that extracts the common restaurant menu items'''
    menu_items = []
    try:    
        all_items = sb.find_elements("div[class='sc-be09943-2 gagwGV']")
        print(len(all_items))
        for item in all_items:
            product_name = item.find_element("css selector", "h4[class='style__Title4-sc-__sc-1nwjacj-5 jrcmhy sc-be09943-0 bpfNyi']").text
            print("Product Name: ", str(product_name))
            try:
                product_description = item.find_element("css selector", "p[contenteditable='false']").text
                print("Product Description: ", str(product_description))
            except:
                product_description = "No description for this product."
            product_price = item.find_element("css selector", "span[class='style__Text-sc-__sc-1nwjacj-0 jbOUDC sc-be09943-5 kA-DgzG']").text
            print("Product Price: ", str(product_price))
            menu_item = {
                "Menu Item": product_name,
                "Menu Ingredients": product_description,
                "Price": product_price
            }
            if product_name == "Poşet":
                continue
            menu_items.append(menu_item)
    except Exception as e:
        print(f"Exception in {e}")
    return menu_items

async def extract_menu_region(sb):
    '''Helper function that extracts the whole region's menu items one by one'''
    menu_items = []
    try:
        all_items = sb.find_elements("div[class='sc-be09943-2 jfdgrR']")
        print(len(all_items))
        for item in all_items:
            product_name = item.find_element("css selector", "h4[class='style__Title4-sc-__sc-1nwjacj-5 bMNcXd sc-be09943-0 xeZxm']").text
            print("Product Name: ", str(product_name))
            try:
                product_description = item.find_element("css selector", "p[class='style__ParagraphText-sc-__sc-1nwjacj-9 iWEpdE']").text
                print("Product Description: ", str(product_description))
            except:
                product_description = "No description for this product."
            product_price = item.find_element("css selector", "span[class='style__Text-sc-__sc-1nwjacj-0 iwTTHJ sc-be09943-5 dBiRKe']").text
            print("Product Price: ", str(product_price))
            menu_item = {
            "Menu Item": product_name,
            "Menu Ingredients": product_description,
            "Price": product_price
                        }
            if product_name == "Poşet":
                continue
            menu_items.append(menu_item)          
        print(menu_items)
    except Exception as e:
        print(f"Exception in {e}")
    return menu_items

async def insert_menu_to_db(menu_items, latitude, longitude, restaurant_name, rating):
    menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)   
    menu_items_list = json.loads(menu_items_json) 
    
    #Inserting items into MongoDB
    restaurant_data = {
    "Restaurant Name": restaurant_name,
    "Rating" : rating,
    "Menu": menu_items_list,
    "coordinates" : {
        "latitude" : latitude if latitude is not None else 0.0,
        "longitude": longitude if longitude is not None else 0.0
    }
    }
    result = restaurants_collection.insert_one(restaurant_data)
    (f"Document inserted with ID: {result.inserted_id}")

#TODO: We can add /marka + {restaurant_name} to gather all the rests
async def g_crawler(url, is_area, restaurant_name):
    menu_items = []
    if is_area: #if we are crawling restaurants inside the whole region      
        url = "https://getir.com/yemek/"
    with SB(uc=True, headless=True) as sb:
        sb.driver.uc_open_with_reconnect(url, 10)
        try:
            print("Trying to open: " + str(url))
            print("Reached: " + str(sb.get_title()))
            print("Locale code:" + str(sb.get_locale_code()))
            # sb.uc_gui_click_captcha() #clicking CF turnstile 
            try:
                sb.click("button[aria-label='Tümünü Reddet']")
                print("Clicked Cookies.")
            except Exception as e:
                print("Cannot reject/accept cookies or ", e)

            if is_area: # Statement is only true when there is an area that will be crawlerd
                try:
                    print(f"Starting locating {restaurant_name}..")
                    sb.click("button[aria-label='Find Location']")
                    # sb.click("css selector", "input[type='text']")
                    sb.sleep(3)
                    sb.type('input[class="style__Input-sc-__sc-1wqqe47-4 eWUYjb react-autosuggest__input"]',f"{restaurant_name}/Kadiköy, İstanbul")
                    sb.sleep(3)
                    # sb.driver.uc_gui_press_key(Keys.SPACE) --> PyAutoGUI that presses keys if needed 
                    sb.click("li[id='react-autowhatever-1--item-0']")
                    sb.click("div[kind='primary']")
                    # sb.click("button.style__Button-sc-__sc-6ivys6-0.eGRCCQ:nth-of-type(1)")
                    sb.sleep(1)
                    sb.click("button[aria-label='Step Button']") #accept address  
                    sb.click("button[aria-label='Save Button']") #save address
                    sb.click("button[type='button']") #agree button 
                    sb.sleep(1)
                    sb.click("div[class='style__Wrapper-sc-__sc-6ivys6-1 GDAK style__Close-sc-__sc-vk2nyz-5 fsISSX']") #changing language (being forced)
                    sb.click("div[class='style__Wrapper-sc-__sc-6ivys6-1 BpZxo style__OkButton-sc-__sc-vk2nyz-8 ezpKor']") #agreeing on the final location and language
                    sb.sleep(3)
                    grid_restaurants = sb.find_elements("css selector", "div[class='sc-128155de-12 bEAREJ']")
                    sb.scroll_to("css selector", "button[class='style__Button-sc-__sc-6ivys6-0 hqQsnw']")
                    sb.sleep(3)
                    for index, item in enumerate(grid_restaurants):
                        sb.sleep(1)
                        sb.click_nth_visible_element("div.sc-128155de-12.bEAREJ a", index)
                        sb.sleep(1)
                        print("Now crawling restaurant: " + sb.find_element("css selector", "h1[class='style__Title1-sc-__sc-1nwjacj-2 hIkhWh sc-e4ee1871-2 gnsGCg']").text)
                        menu_items = await extract_menu_region(sb)
                        restaurant_location = sb.find_element("css selector", "h1[data-testid='title']").text
                        result = re.search(r'\((.*?)\)', restaurant_location)
                        if result:
                            restaurant_location = result.group(1) + " ,İstanbul, Türkiye"
                            print("Restaurant address" + restaurant_location)
                        latitude, longitude = await get_coordinates(restaurant_location)
                        print("Restaurant coordinates: " + str(latitude, longitude))
                        restaurant_rating = sb.find_element("css selector", "span[class='style__Text-sc-__sc-1nwjacj-0 jbOUDC sc-e4ee1871-10 dZyWue']").text
                        await insert_menu_to_db(menu_items, latitude, longitude, restaurant_name , restaurant_rating)
                        sb.go_back()
                except Exception as e:
                    print(f"Exception: {e}")   

            restaurant_location = sb.find_element("css selector", "h1[data-testid='title']").text
            result = re.search(r'\((.*?)\)', restaurant_location)
            if result:
                restaurant_location = result.group(1) + " ,İstanbul, Türkiye"
            latitude, longitude = await get_coordinates(restaurant_location)
            restaurant_rating = sb.find_element("css selector", "span[class='style__Text-sc-__sc-1nwjacj-0 jbOUDC sc-e4ee1871-10 dZyWue']").text
            if not is_area:
                menu_items = await extract_menu_single(sb)
                menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)  
                menu_items_list = json.loads(menu_items_json)  
                df = pd.DataFrame(menu_items_list) 
                await insert_menu_to_db(menu_items, latitude, longitude, restaurant_name, restaurant_rating)
            await get_from_mongo("restaurant")
            return df.to_json(orient='split')                  
        except Exception as e:
            print(f"Exception in Getir Crawler:  {e}")
    
                
async def main():
    config = uvicorn.Config("crawler:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()
     
if __name__ == "__main__":
    asyncio.run(main())
