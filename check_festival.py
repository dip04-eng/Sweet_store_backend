from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
client = MongoClient(MONGO_URI)
db = client["sweet_store"]
sweet_collection = db["sweets"]

# Check all sweets and their isFestival status
print("\n📋 All Sweets in Database:")
print("="*60)
for sweet in sweet_collection.find():
    name = sweet.get('name', 'Unknown')
    is_festival = sweet.get('isFestival', 'NOT SET')
    print(f"Name: {name:20} | isFestival: {is_festival}")

print("\n" + "="*60)
print("\nTo update Phirni to be a festival sweet, run:")
print('sweet_collection.update_one({"name": "Phirni"}, {"$set": {"isFestival": True}})')
