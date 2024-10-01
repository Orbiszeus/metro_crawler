from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import crawler 
import repository 
import search_engine
import geodata

app = FastAPI()

class CrawlRequest(BaseModel):
    area: str = Field(default=None, description="The area to search for restaurants")
    restaurant: str = Field(default=None, description="The specific restaurant to search for")
    
class HotelCrawlRequest(BaseModel):
    hotel_area: str = Field(default=None, description="The area to search for hotels")

@app.post("/crawl_hotels")
async def hotel_crawl_api(hotel_area: str):
    try:
        if not hotel_area:
            raise HTTPException(status_code=400, detail="Hotel area is required")
        search_url = f"https://www.agoda.com/tr-tr/city/{hotel_area}-tr.html"
        hotels = geodata.get_category_data('hotel')    
        for hotel in hotels:
            if "name" in hotel:
                serper_y_results = await search_engine.hotel_serper_search(hotel["name"])
                for url in serper_y_results:
                    await crawler.hotel_crawler(url, is_single=True) # "is_single" parameter means only crawling one hotel page 
        results = repository.get_from_mongo()
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
        restaurants = geodata.get_category_data('restaurants')    
        for rest in restaurants:
            if "name" in rest:
                serper_y_results = await search_engine.menu_serper_search(rest["name"], company="g")
                for url in serper_y_results:
                    df_json = await crawler.g_crawler(url, rest) 
                    # if df_json:
                    #     return {"dataframe": df_json,
                    #             "url": url}
                    # else:
                    #     return {"error": "Crawling failed"}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")