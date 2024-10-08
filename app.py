from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel, Field
import crawler 
import repository 
import search_engine
import geodata
import pandas as pd
import json 
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://metrocrawler-production.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    area: str = Field(default=None, description="The area to search for restaurants")
    restaurant: str = Field(default=None, description="The specific restaurant to search for")
    
class HotelCrawlRequest(BaseModel):
    hotel_area: str = Field(default=None, description="The area to search for hotels")
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection established.")
    while True:
        data = await websocket.receive_text()
        logging.info(f"Received message: {data}")
        await websocket.send_text(f"Message received: {data}")

@app.post("/crawl_hotels")
async def hotel_crawl_api(hotel_area: str):
    try:
        if not hotel_area:
            raise HTTPException(status_code=400, detail="Hotel area is required")
        search_url = f"https://www.agoda.com/tr-tr/city/{hotel_area}-tr.html"
        hotels = geodata.get_category_data('hotels_Beyoglu')    
        for hotel in hotels:
            if repository.check_hotel_exists(hotel["name"]):
                continue
            if "name" in hotel:
                serper_y_results = await search_engine.hotel_serper_search(hotel["name"])
                for url in serper_y_results:
                    current_hotel = hotel["name"]
                    if "agoda" not in url:
                        continue
                    if "agoda.com" in url and "/tr-tr/" not in url:
                        url = url.replace("agoda.com", "agoda.com/tr-tr")
                    await crawler.hotel_crawler(url, current_hotel, is_single=True) # "is_single" parameter means only crawling one hotel page 
        results = repository.get_from_mongo("hotel")
        if not results:
            raise HTTPException(status_code=404, detail="No data found in MongoDB")
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
    
@app.post("/crawl_menu")
async def crawler_endpoint(request: CrawlRequest):
    try:
        restaurant = ""
        if request.area:
            restaurant += request.area
        elif request.restaurant:
            restaurant += request.restaurant 
              
        if repository.check_restaurant_exists(restaurant):
            try:
                menu_items = repository.get_restaurant_data(restaurant, "restaurants")
                menu_items_list = json.loads(json.dumps(menu_items, ensure_ascii=False))  
                df_json = pd.DataFrame(menu_items_list) 
                if not df_json.empty:
                    return {"dataframe": df_json.to_json(orient='split'),
                            "url": "This was crawled from getir"}
                else:
                    return {"error": "Crawling failed"}  
            except Exception as e:
                print(f"Exception: {e}")
                
        '''Single restaurant crawler from command line'''
        serper_y_results = await search_engine.menu_serper_search(restaurant, company="g")
        for url in serper_y_results:
            df_json = await crawler.g_crawler(url, restaurant, category="restaurant")
            if not df_json.empty:
                return {"dataframe": df_json,
                        "url": url}
            else:
                return {"error": "Crawling failed"}
            
        # restaurants = geodata.get_category_data('restaurants')   
        # coffee_shops = geodata.get_category_data('coffee')   


        # for rest in restaurants:
        #     if repository.check_restaurant_exists(rest["name"]):
        #         continue
        #     if "name" in rest:
        #         serper_y_results = await search_engine.menu_serper_search(rest["name"], company="g")
        #         for url in serper_y_results:
        #             df_json = await crawler.g_crawler(url, rest["name"], "restaurant") 
        #             # if df_json:
        #             #     return {"dataframe": df_json,
        #             #             "url": url}
        #             # else:
        #             #     return {"error": "Crawling failed"}
        # repository.get_from_mongo("restaurant")

        # for cafe in coffee_shops:
        #     if repository.check_cafe_exists(cafe["name"]):
        #         continue
        #     if "name" in cafe:
        #         serper_y_results = await search_engine.menu_serper_search(cafe["name"], company="g")
        #         for url in serper_y_results:
        #             await crawler.g_crawler(url, cafe["name"], "cafe") 
        # repository.get_from_mongo("cafes")       
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
    
    return {"message": "Crawling completed successfully"}
