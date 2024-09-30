from pymongo import MongoClient
import certifi
import json 

connection = "mongodb+srv://baris_ozdizdar:ZhcyQqCIwQMS8M29@metroanalyst.thli7ie.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE&appName=MetroAnalyst"
client = MongoClient(connection, tlsCAFile=certifi.where())

db = client["MetroAnalyst"]
hotel_collection = db["hotels"]
restaurants_collection = db["restaurants"]

def get_from_mongo(collection_name):
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

def insert_menu_to_db(menu_items,restaurant_name, rating):
    menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)   
    menu_items_list = json.loads(menu_items_json) 
    
    #Inserting items into MongoDB
    restaurant_data = {
    "Restaurant Name": restaurant_name,
    "Rating" : rating,
    "Menu": menu_items_list,
    }
    result = restaurants_collection.insert_one(restaurant_data)
    (f"Document inserted with ID: {result.inserted_id}")

def check_restaurant_exists(restaurant_name):
    # Assuming your collection is named 'restaurants'
    restaurant = restaurants_collection.find_one({"Restaurant Name": restaurant_name})
    
    if restaurant:
        return True 
    else:
        return False  
    
def check_hotel_exists(hotel_name):
    # Assuming your collection is named 'hotels'
    hotel = hotel_collection.find_one({"Hotel Name": hotel_name})
    if hotel:
        return True  
    else:
        return False 