from pymongo import MongoClient
import certifi
import json 

# connection = "mongodb+srv://baris_ozdizdar:ZhcyQqCIwQMS8M29@metroanalyst.thli7ie.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE&connectTimeoutMS=60000&socketTimeoutMS=60000&appName=MetroAnalyst"


try:
    client = MongoClient("mongodb+srv://baris_ozdizdar:ZhcyQqCIwQMS8M29@metroanalyst.thli7ie.mongodb.net/?retryWrites=true&w=majority&ssl=true&connectTimeoutMS=60000&socketTimeoutMS=60000&appName=MetroAnalyst")
    print("Mongo connection successfulls")
except Exception as e:
    print("Connection error: ", e)

db = client["MetroAnalyst"]
hotel_collection = db["hotels"]
restaurants_collection = db["restaurants"]
cafes_collection = db['cafes']


def get_from_mongo(collection_name, save_file=True):
    if collection_name == "hotel":
        collection = hotel_collection
        output_file = "hotel_data.json"

    elif collection_name == "restaurant":
        collection = restaurants_collection
        output_file = "restaurant_data.json"

    elif collection_name == "cafe":
        collection = cafes_collection
        output_file = "cafe_data.json"

    else:
        return None

    cursor = collection.find({}, {'_id': 0})
    results = list(cursor)

    if save_file:
        with open(output_file, "w", encoding="utf-8") as file:
            documents_json = json.dumps(results, ensure_ascii=False, indent=4)
            file.write(documents_json)

    return results

def insert_menu_to_db(menu_items,restaurant_name, rating, category):
    menu_items_json = json.dumps(menu_items, ensure_ascii=False, indent=4)   
    menu_items_list = json.loads(menu_items_json) 
    
    if category == "restaurant":
    #Inserting items into MongoDB
        restaurant_data = {
        "Restaurant Name": restaurant_name,
        "Rating" : rating,
        "Menu": menu_items_list,
        }
        result = restaurants_collection.insert_one(restaurant_data)
        (f"Document inserted with ID: {result.inserted_id}")

    if category == "cafe":
        restaurant_data = {
        "Cafe Name": restaurant_name,
        "Rating" : rating,
        "Menu": menu_items_list,
        }
        result = cafes_collection.insert_one(restaurant_data)
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

def check_cafe_exists(cafe_name):
    # Assuming your collection is named 'hotels'
    hotel = hotel_collection.find_one({"Cafe Name": cafe_name})
    if hotel:
        return True  
    else:
        return False


def update_coordinates(collection_name):
    collection = db[collection_name]
    documents = collection.find({"coordinates": {"$exists": True}})

    for doc in documents:
        if isinstance(doc['coordinates'], dict) and 'latitude' in doc['coordinates'] and 'longitude' in doc['coordinates']:
            latitude = doc['coordinates']['latitude']
            longitude = doc['coordinates']['longitude']

            new_coordinates = [latitude, longitude]

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"coordinates": new_coordinates}}
            )


def join_json_to_mongo(json_file, collection_name, join_field_1, join_field_2):
    collection = db[collection_name]

    with open(json_file, 'r') as f1:
        json_data = json.load(f1)

    for item in json_data:
        name_in_json = item.pop(join_field_1, None)

        if name_in_json is not None:
            mongo_doc = collection.find_one({join_field_2: name_in_json})

            if mongo_doc:
                update_data = {
                    "$set": item
                }

                collection.update_one({"_id": mongo_doc["_id"]}, update_data)

'''@Returns a specific restaurant menu data if is present in mongo'''
def get_restaurant_data(place_name, collection_name):

    if collection_name == "cafes":
        cursor = db[collection_name].find({"Cafe Name": place_name})
        return [doc['Menu'] for doc in cursor]
    
    if collection_name == "restaurants":
        cursor = db[collection_name].find({"Restaurant Name" : place_name})
        return [doc['Menu'] for doc in cursor]
    
if __name__ == "__main__":
    print(get_restaurant_data("Binbir Tadım Döner", "restaurants"))