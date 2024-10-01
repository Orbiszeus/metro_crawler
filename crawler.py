import json
import pandas as pd
from seleniumbase import SB
import uvicorn
import re
import os 
import json
import pandas as pd
import asyncio
import repository 
import search_engine
import geodata

GOOGLE_MAPS_QUERY = "https://www.google.com/maps/search/?api=1&query={}&query_place_id={}"
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

async def get_hotel_item(sb, name):
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
        sb.click("css selector", "button[class='BtnPair__RejectBtn']")
        sb.sleep(3)
        # hotel_name_elements = sb.find_elements("css selector", "h2[data-selenium='hotel-header-name'], p[data-selenium='hotel-header-name']")
        # if hotel_name_elements:
        #     hotel_name = hotel_name_elements[0].text
        #     print("Hotel Name: " + str(hotel_name))
        hotel_name = name
        existing_hotel = repository.hotel_collection.find_one({"Hotel Name": hotel_name})
        if existing_hotel:
            print(f"Hotel '{hotel_name}' already exists in the database.")
            return 
    except:
        hotel_name = "N/A"
    try:
        hotel_location = sb.find_element("css selector", "span[data-selenium='hotel-address-map']").text
    except:
        hotel_location = "N/A"

    try:
        sb.sleep(2)
        hotel_rating = sb.find_element("css selector", "span[class='sc-jrAGrp sc-kEjbxe fzPhrN ehWyCi']").text
        if hotel_rating == "":
            hotel_rating = sb.find_element("css selector", "span[class='af4c3-af4c3-box af4c3-m-none af4c3-mr-xs']").text
        print("Rating: " + hotel_rating)
    except:
        hotel_rating = "N/A"
    sb.sleep(2)
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
                    print("Room with breakfast:" + str(rooms_with_breakfast_number))
                    break
    except:
        rooms_with_breakfast_number = "0"

    try:
        parent_restaurant_count = sb.find_element("css selector", "div[data-element-name='about-hotel-useful-info']")
        all_divs = parent_restaurant_count.find_elements("css selector", "div.Box-sc-kv6pi1-0.hRUYUu")
        print("Number of hotel useful information is: " + len(all_divs))
        for div in all_divs:
            label_span = div.find_element("css selector", "span.Spanstyled__SpanStyled-sc-16tp9kb-0.gwICfd.kite-js-Span ")
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
            print("Breakfast Types: ", breakfast_types_list)        
        # all_divs = parent_restaurant_details.find_elements("css selector", "div.Box-sc-kv6pi1-0.dtSdUZ")
            # for div in parent_restaurant_details:
            try:
                restaurant_divs = sb.find_elements("css selector", "div[data-element-name='restaurants-on-site']")
                if restaurant_divs:
                    for rests in restaurant_divs:
                        try:
                            restaurant_name = rests.find_element("css selector", "h5[class='sc-jrAGrp sc-kEjbxe bmFdwl kGfVSb']").text
                            print("Restaurant name: " + str(restaurant_name))
                        except:
                            restaurant_name = "Otelin içerisinde restoran bulunmuyor."
                        try:
                            pattern = r'Mutfak:(.*)'
                            kitchen_name = rests.find_element("css selector", "span[class='Spanstyled__SpanStyled-sc-16tp9kb-0 gwICfd kite-js-Span ']").text
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
                        print(facility_restaurant_details)
                        all_facility_restaurant_details.append(facility_restaurant_details)
            except:
                print("No restaurant details are present.")
                # break
            facility_restaurant_details["Breakfast Options"] =  breakfast_types_list
    except Exception as e:
        print(e)

    latitude, longitude = await search_engine.get_coordinates(hotel_location)

    return {
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

async def hotel_crawler(url, hotel_name, is_single):
    hotel_items = []
    with SB(uc=True, headless=True) as sb:
        sb.driver.uc_open_with_reconnect(url, 10) 
        try:
            if is_single:
                print("Page Title: " + sb.get_title())
                sb.click("css selector", "div[class='SearchboxBackdrop']")
                hotel_item = await get_hotel_item(sb, hotel_name)
                result = repository.hotel_collection.insert_one(hotel_item)
                print(f"Document inserted with ID: {result.inserted_id}")

            if not is_single:
                sb.sleep(3)
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
                            sb.sleep(1)
                            try:
                                sb.click_nth_visible_element("div[data-element-name='PropertyCardBaseJacket'] a", index + 1)
                            except:
                                continue
                            hotel_item = await get_hotel_item(sb)
                            result = repository.hotel_collection.insert_one(hotel_item)
                            print(f"Document inserted with ID: {result.inserted_id}")
                            sb.sleep(1)
                            sb.driver.switch_to.window(first_tab_handle)
                        if (sb.is_element_present("css selector", "button[id='paginationNext']")):
                            sb.click("css selector", "button[id='paginationNext']") 
                        else: # Breaking out of the while loop as there is no more next page to crawl 
                            break 
        except Exception as e:
            print(f"Exception: {e}")
    return repository.get_from_mongo("hotel")

async def extract_menu_item(sb):
    '''Helper function that extracts the common restaurant menu items'''
    menu_items = []
    try:    
        all_items = sb.find_elements("div[class='sc-be09943-2 gagwGV']")
        item_number = len(all_items)

        if item_number == 0: 
            print("Empty Page")
            return "Empty Page"

        print("Total item in the page is " + str(item_number))
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

async def g_crawler(url, restaurant_name):
    menu_items = []
    with SB(uc=True, headless=True, incognito=True) as sb:
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
            menu_items = await extract_menu_item(sb)
            if menu_items == "Empty Page":
                serper_y_results = await search_engine.menu_serper_search(restaurant_name, company="y")
                for url in serper_y_results:
                    await y_crawler(url, restaurant_name)
            try:
                restaurant_rating = sb.find_element("css selector", "span[class='style__Text-sc-__sc-1nwjacj-0 jbOUDC sc-e4ee1871-10 dZyWue']").text
            except:
                restaurant_rating = "No rating found."

            menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)  
            menu_items_list = json.loads(menu_items_json)  
            df = pd.DataFrame(menu_items_list) 
            repository.insert_menu_to_db(menu_items, restaurant_name, restaurant_rating)
            repository.get_from_mongo("restaurant")
            return df.to_json(orient='split')          
        except Exception as e:
            print(f"Exception in Getir Crawler:  {e}")

def y_crawler(url, restaurant_name):
    menu_items = []
    with SB(uc=True, headless=True, incognito=True) as sb:
        sb.driver.uc_open_with_reconnect(url, 6)       
        try:
            print("Locale Code: " +str(sb.get_locale_code()))
            # print(sb.save_screenshot_to_logs(name=None, selector=None, by="css selector"))
            print("Page title: " + str(sb.get_title()))
            sb.sleep(3)
            sb.uc_gui_handle_cf()
            sb.sleep(5)
            if sb.is_element_present("div.bds-c-modal__content-window"): #closing the closed hours pop-up
                sb.click("button[data-testid='dialogue-cancel-cta']")
            sb.sleep(5)
            try:
                sb.execute_script("UC_UI.denyAllConsents().then(UC_UI.closeCMP);") #closing the cookies
            except:
                print("Cookies couldn't denied/accepted.")
            print("Crawling a single page.")
            if sb.is_element_present("iframe[title*='recaptcha']"):
                print("Recatptha!!!")  
            all_items = sb.find_elements("li[data-testid='menu-product']")
            for li in all_items:
                product_name = li.find_element("css selector", "[data-testid='menu-product-name']").text
                sb.sleep(0.3)
                print("Product Name: " + product_name)
                product_description = li.find_element("css selector", "[data-testid='menu-product-description']").text
                sb.sleep(0.3)
                print("Product Description: " + product_description)
                product_price = li.find_element("css selector", "[data-testid='menu-product-price']").text            
                sb.sleep(0.1)
                print("Product Price: " + product_price)

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
            #Inserting items to Mongo
            restaurant_data = {
            "Restaurant Name": restaurant_name,
            "Menu": menu_items_list}
            result = repository.restaurants_collection.insert_one(restaurant_data)
            (f"Document inserted with ID: {result.inserted_id}")
            df = pd.DataFrame(menu_items_list)
        except Exception as e:
            print(f"Exception : {e}")
    return df.to_json(orient='split')   

async def main():
    config = uvicorn.Config("app:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()
     
if __name__ == "__main__":
    asyncio.run(main())
