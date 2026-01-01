from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
client = MongoClient(MONGO_URI)
db = client["sweet_store"]
sweet_collection = db["sweets"]

print("\n🔍 Checking current sweets...")
all_sweets = list(sweet_collection.find())
print(f"Found {len(all_sweets)} sweets in database")

if len(all_sweets) == 0:
    print("\n⚠️ Database is empty! Please add sweets through the admin panel.")
else:
    print("\n📋 Current Sweets:")
    print("="*80)
    for sweet in all_sweets:
        name = sweet.get('name', 'Unknown')
        is_festival = sweet.get('isFestival', False)
        category = sweet.get('category', 'Unknown')
        print(f"Name: {name:20} | Category: {category:15} | isFestival: {is_festival}")

    # Update Phirni to be festival sweet
    print("\n🔄 Updating Phirni to be a Festival sweet...")
    result = sweet_collection.update_one(
        {"name": "Phirni"}, 
        {"$set": {"isFestival": True}}
    )
    
    if result.matched_count > 0:
        print(f"✅ Updated {result.modified_count} document(s)")
    else:
        print("❌ Phirni not found in database")
    
    # Show updated status
    print("\n📋 Updated Sweets:")
    print("="*80)
    for sweet in sweet_collection.find():
        name = sweet.get('name', 'Unknown')
        is_festival = sweet.get('isFestival', False)
        category = sweet.get('category', 'Unknown')
        status = "🎉 FESTIVAL" if is_festival else "🍬 Regular"
        print(f"{status} | Name: {name:20} | Category: {category}")

print("\n✅ Done! Please refresh your website to see the changes.")
