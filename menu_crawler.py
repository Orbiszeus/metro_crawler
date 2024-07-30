import requests
import logging
import json
import pandas as pd
from seleniumbase import SB
from curl_cffi import requests
from typing import Union
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
import uvicorn
from tempfile import NamedTemporaryFile
from uuid import uuid4
import re
from pymongo import MongoClient
from geopy.geocoders import GoogleV3

GOOGLE_MAPS_QUERY = "https://www.google.com/maps/search/?api=1&query={}&query_place_id={}"
client = MongoClient("mongodb+srv://baris_ozdizdar:ZhcyQqCIwQMS8M29@metroanalyst.thli7ie.mongodb.net/?retryWrites=true&w=majority&appName=MetroAnalyst")
db = client["MetroAnalyst"]
collection = db["hotels"]

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def hotel_serper_search(area):
    
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

def menu_serper_search(area):
    
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": f"{area} Getir",
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
        
app = FastAPI()

class CrawlRequest(BaseModel):
    area: str = Field(default=None, description="The area to search for restaurants")
    restaurant: str = Field(default=None, description="The specific restaurant to search for")
    
class HotelCrawlRequest(BaseModel):
    hotel_area: str = Field(default=None, description="The area to search for hotels")
    
import json
import pandas as pd
import re

def hotel_crawler(url):
    hotel_items = []
    with SB(uc=True, headless=False, locale_code="tr") as sb:
        sb.driver.uc_open_with_reconnect(url, 6) #https://www.agoda.com/tr-tr/city/istanbul-tr.html, "https://www.agoda.com/tr-tr/search?guid=4a629c25-e506-4dc2-a52d-4115ad9d7e0a&asq=bFdTL9llP7BZ4SejwwejB5ufa9Vwpz6XltTHq4n%2B9gP1PvdgVUVP68h57eVdQuv8IBrWFTqhW1dpLL7MGGZsqdrUrlVV3J13je9wZFHCpgF8S1ZjjN6usSxp30jSYO1wDhV5i2ciNve1U0UDxqZpvG0t3c82nJ%2Fp%2B0GXkwK5hQ9JypyOe2O9exnn65L2OXGBvVuYmacm%2FIy%2BM6q24efrgMj%2BxG%2F0EXyqEpLKdlme8IQ%3D&city=14932&tick=638572309229&locale=tr-tr&ckuid=981c775b-5dc7-43e2-82ae-be18bc5e2172&prid=0&gclid=CjwKCAjw4_K0BhBsEiwAfVVZ_9c3umlL-ft78T3009NtrOi0kFobyntGsmCG8InezITfHbX1-R16jhoCelQQAvD_BwE&currency=EUR&correlationId=706f3aa0-09ca-4108-821d-b5370a3368b1&analyticsSessionId=-8095943469502461136&pageTypeId=8&realLanguageId=32&languageId=32&origin=ES&stateCode=GC&cid=1922882&tag=c4254dc2-e34a-491c-9db8-aeb463b931f1&userId=981c775b-5dc7-43e2-82ae-be18bc5e2172&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=1&currencyCode=EUR&htmlLanguage=tr-tr&cultureInfoName=tr-tr&machineName=am-pc-4i-geo-web-user-5cb49677b6-4xg9g&trafficGroupId=5&sessionId=3ny4d4ulutjgj3zwzvmai1zj&trafficSubGroupId=122&aid=82361&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&browserFamily=Chrome&cdnDomain=agoda.net&checkIn=2024-07-31&checkOut=2024-08-01&rooms=1&adults=2&children=0&priceCur=EUR&los=1&textToSearch=%C4%B0stanbul&travellerType=1&familyMode=off&ds=MbFpC8913MUisoKd&brands=14&productType=-1&sort=reviewAll
        try:
            sb.sleep(3)
            sb.uc_gui_handle_cf()

            sb.click("button[data-element-name='search-button']")  # This will take us to the list of hotels
            sb.sleep(5)
            first_tab_handle = sb.driver.current_window_handle
            hotel_counter = 0
            # sb.click("span[aria-label='Marriott']")
            sb.sleep(4)
            # sb.scroll_to_bottom()
            sb.slow_scroll_to("css selector", "button[id='paginationNext']")
            sb.sleep(5)
            #TODO: Add the page by page crawling by clicking "next"
            grid_items = sb.find_elements("div[data-element-name='PropertyCardBaseJacket']")
            total_grid_item = len(grid_items)
            print("Total grid number: " + str(total_grid_item))
            if grid_items:
                for index, item in enumerate(grid_items):
                    hotel_items = []
                    sb.sleep(4)
                    try:
                        sb.click_nth_visible_element("div[data-element-name='PropertyCardBaseJacket'] a", index + 1)
                    except:
                        continue
                    # sb.click_nth_visible_element("a[class='PropertyCard__Link']", index + 1)
                    sb.sleep(5)
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
                        sb.sleep(3)
                        parent_restaurant_details = sb.find_element("css selector", "div[id='abouthotel-restaurant']")
                        if parent_restaurant_details:
                            try:
                                breakfast_details = sb.find_element("css selector", "ul[data-element-name='breakfast-options']")
                                breakfast_options_lis = breakfast_details.find_elements("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.gwICfd.kite-js-Span")
                                for breakfast_types in breakfast_options_lis:
                                    breakfast_types_list.append(breakfast_types.text)
                            except:
                                breakfast_types = "Otelin içerisinde kahvaltı içeriği bilgisi yer almıyor."                            
                                
                            all_divs = parent_restaurant_details.find_elements("css selector", "div.Box-sc-kv6pi1-0.dtSdUZ")
                            for div in all_divs:
                                try:
                                     restaurant_name = div.find_element("css selector", "h5.sc-jrAGrp.sc-kEjbxe.bmFdwl.kGfVSb").text
                                except : 
                                    restaurant_name = "Otelin içerisinde restoran yer almıyor."
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
                                    "Kitchen": kitchen_name,
                                    "Menu" : "A la carte"
                                }
                                all_facility_restaurant_details.append(facility_restaurant_details)
                                break
                            facility_restaurant_details["Breakfast Options"] =  breakfast_types_list
                            
                    except Exception as e:
                        print(e)
                        
                    latitude, longitude = get_coordinates(hotel_location)
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

                    result = collection.insert_one(hotel_item)
                    print(f"Document inserted with ID: {result.inserted_id}")

                    """Converting array object into an excel format"""
                    # hotel_items.append(hotel_item)
                    # hotel_json = json.dumps(hotel_items, ensure_ascii=False, indent=4)
                    # print(hotel_json)
                    # hotel_items_list = json.loads(hotel_json)
                    # df = pd.DataFrame(hotel_items_list)
                    # excel_file = f'{hotel_name}_HOTEL_ANALYSIS.xlsx'
                    # df.to_excel(excel_file, index=False)
                    sb.sleep(1)
                    sb.driver.switch_to.window(first_tab_handle)   
        except Exception as e:
            print(f"Exception: {e}")
    return get_from_mongo()

def get_from_mongo():
    cursor = collection.find({}, {'_id': 0}) 
    documents = list(cursor)
    documents_json = json.dumps(documents, ensure_ascii=False, indent=4)
    output_file = "hotel_data.json"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(documents_json)
    client.close()
    
def get_coordinates(address):
    geolocator = GoogleV3(api_key="AIzaSyAJujPg1wWosbbLfj7-cpEoPHCy5mSnjDM")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None, None
    
def menu_crawler(url, is_area):
    menu_items = []
    with SB(uc=True, headless=False, locale_code="tr") as sb:
        sb.driver.uc_open_with_reconnect(url, 6)    
        try:
            sb.sleep(3)
            sb.uc_gui_handle_cf()
            sb.sleep(5)
            if sb.is_element_present("div.bds-c-modal__content-window"): #closing the closed hours pop-up
                sb.click("button[data-testid='dialogue-cancel-cta']")
            sb.sleep(5)
            if not is_area:
                sb.execute_script("UC_UI.denyAllConsents().then(UC_UI.closeCMP);") #closing the cookies
            sb.sleep(5)   
            if is_area:
                grid_items = sb.find_elements("div.bds-c-grid-item.vendor")
                for index, item in enumerate(grid_items):
                    menu_items = []
                    print(len(sb.get_attribute(selector="div.bds-c-grid-item.vendor:nth-child(" + str(index + 1) + ") a", attribute="href", by="css selector")))
                    sb.click_nth_visible_element("div.bds-c-grid-item.vendor a", index)
                    
                    if sb.is_element_present("iframe[title*='recaptcha']"):
                        print("Recaptha!!")  
                    all_items = sb.find_elements("li[data-testid='menu-product']")
                    sb.sleep(1)
                    for li in all_items:
                        product_name = li.find_element("css selector", "[data-testid='menu-product-name']").text
                        sb.sleep(3)
                        product_description = li.find_element("css selector", "[data-testid='menu-product-description']").text
                        sb.sleep(3)
                        product_price = li.find_element("css selector", "[data-testid='menu-product-price']").text            
                        menu_item = {
                            "Menu Item": product_name,
                            "Menu Ingredients": product_description,
                            "Price": product_price
                        }
                        if product_name == "Poşet":
                            continue
                        menu_items.append(menu_item)
                    menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)   
                    menu_items_list = json.loads(menu_items_json) 
                    df = pd.DataFrame(menu_items_list)
                    title = sb.get_title()
                    excel_file = f'{title}_menu.xlsx'
                    df.to_excel(excel_file, index=False)
                    sb.go_back()
                    if sb.is_element_present("iframe[title*='recaptcha']"):
                        print("Recaptha!!")      
            
            else:
                
                if sb.is_element_present("iframe[title*='recaptcha']"):
                    print("Recatptha!!!")  
                all_items = sb.find_elements("li[data-testid='menu-product']")
                for li in all_items:
                    product_name = li.find_element("css selector", "[data-testid='menu-product-name']").text
                    sb.sleep(3)
                    product_description = li.find_element("css selector", "[data-testid='menu-product-description']").text
                    sb.sleep(3)
                    product_price = li.find_element("css selector", "[data-testid='menu-product-price']").text            
                    menu_item = {
                        "Menu Item": product_name,
                        "Menu Ingredients": product_description,
                        "Price": product_price
                    }
                    if product_name == "Poşet":
                        continue
                    menu_items.append(menu_item)
                menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)   
                menu_items_list = json.loads(menu_items_json) 
                df = pd.DataFrame(menu_items_list)
                title = sb.get_title()
                excel_file = f'{title}_menu.xlsx'
                df.to_excel(excel_file, index=False)
                sb.go_back()
                sb.sleep(5)                            
                        
        except Exception as e:
            print(f"Exception : {e}")
            logging.info("No CAPTCHA iframe found, assuming automatic verification")
    return menu_items  

@app.post("/crawl_menu")
def crawler_endpoint(request: CrawlRequest):
    area = ""
    is_area = True
    if request.area:
        area += request.area
    elif request.restaurant:
        area += request.restaurant    
        is_area = False
        
    serper_y_results = menu_serper_search(area)
    for url in serper_y_results:
        # menu_crawler(url, is_area)
        g_crawler(url, is_area)
        
@app.post("/crawl_hotels")
def hotel_crawl_api(hotel_area):
    # hotel_serper_results = hotel_serper_search("İstanbul")
    # for url in hotel_serper_results:
    if hotel_area:
        
        search_url = f"https://www.agoda.com/tr-tr/city/{hotel_area}-tr.html"
        hotel_crawler(search_url)      
    return get_from_mongo()  

# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     id = uuid4()
#     vertexAI = vertex_pdf_ai.VertexAI()
#     # Save the uploaded file to a temporary location
#     with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
#         temp_file.write(file.file.read())
#         temp_file_path = temp_file.name

#     # Read the PDF content
#     with open(temp_file_path, "rb") as f:
#         pdf_content = f.read()

#     # Call the asynchronous function
#     result = await process_uploaded_pdf(temp_file_path, pdf_content, id)
    
#     # Define source and destination URIs for OCR
#     gcs_source_uri = result["gsc_uri"]
#     gcs_destination_uri = f"gs://file-storage23/output/{id}/"

#     # Perform OCR on the uploaded PDF
#     ocr_text = async_detect_document(gcs_source_uri, gcs_destination_uri)
#     vertexAI.ask_gemini(ocr_text, gcs_source_uri)
    
#     return {"ocr_text": ocr_text, "gsc_uri": gcs_source_uri, "document_id": str(id)}

#TODO: using wait attributes when gathering selectors
def g_crawler(url, is_area):
    menu_items = []
    if not is_area: 
        with SB(uc=True, headless=False) as sb:
            sb.driver.uc_open_with_reconnect(url, 6)
            try:
                sb.uc_gui_handle_cf()
                sb.sleep(3)
                sb.click("button[aria-label='Tümünü Reddet']")
                sb.sleep(3)
                all_items = sb.find_elements("div[class='sc-be09943-2 gagwGV']")
                for item in all_items:
                    product_name = item.find_element("css selector", "h4[class='style__Title4-sc-__sc-1nwjacj-5 jrcmhy sc-be09943-0 bpfNyi']").text
                    sb.sleep(2)
                    try:
                        product_description = item.find_element("css selector", "p[contenteditable='false']").text
                    except:
                        product_description = "No description for this product."
                    sb.sleep(2)
                    product_price = item.find_element("css selector", "span[class='style__Text-sc-__sc-1nwjacj-0 jbOUDC sc-be09943-5 kA-DgzG']").text
                    sb.sleep(2)
                    menu_item = {
                        "Menu Item": product_name,
                        "Menu Ingredients": product_description,
                        "Price": product_price
                    }
                    if product_name == "Poşet":
                        continue
                    menu_items.append(menu_item)
                menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)   
                menu_items_list = json.loads(menu_items_json) 
                df = pd.DataFrame(menu_items_list)
                title = sb.get_title()
                excel_file = f'{title}_getir_menu.xlsx'
                df.to_excel(excel_file, index=False)                    
                sb.get_page_source()
                sb.save_page_source("getir_source")
            except Exception as e:
                print(f"Exception in Getir Crawler:  {e}")
    
                
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
     
if __name__ == "__main__":
    main()
