from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import ssl
import re
import time

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    # Fallback to local Mongo for development so endpoints don't 500 when env is missing
    MONGO_URI = "mongodb://127.0.0.1:27017"
    print("⚠️ MONGO_URI not set; falling back to local MongoDB at mongodb://127.0.0.1:27017")

# Force legacy OpenSSL provider for compatibility with MongoDB Atlas
os.environ['OPENSSL_CONF'] = ''

# Create SSL context with legacy settings
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

# Simple in-memory cache for sweets (reduces MongoDB calls)
_sweets_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 60  # Cache for 60 seconds
}

# MongoDB connection with optimized settings for faster response
try:
    mongo_kwargs = {
        "serverSelectionTimeoutMS": 10000,  # Reduced from 30s to 10s
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 20000,
        "maxPoolSize": 10,  # Connection pooling
        "minPoolSize": 1,
        "maxIdleTimeMS": 45000,
        "retryWrites": True,
        "w": "majority",
    }
    # Enable TLS only for SRV (Atlas) URIs or when explicitly provided in URI
    if MONGO_URI.startswith("mongodb+srv://"):
        mongo_kwargs["tls"] = True
        # Optionally allow invalid certs via env toggle (default False)
        if os.getenv("MONGO_TLS_ALLOW_INVALID", "false").lower() in ("1", "true", "yes"):                
            mongo_kwargs["tlsAllowInvalidCertificates"] = True
    # IMPORTANT: Do not set tlsInsecure and tlsAllowInvalidCertificates together
    client = MongoClient(MONGO_URI, **mongo_kwargs)
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
except Exception as e:
    print(f"⚠️ MongoDB connection error: {e}")
    client = None

db = client["sweet_store"] if client is not None else None
sweet_collection = db["sweets"] if db is not None else None


def clear_sweets_cache():
    """Clear the sweets cache to force fresh data on next request."""
    global _sweets_cache
    _sweets_cache["data"] = None
    _sweets_cache["timestamp"] = 0
    print("🗑️ Sweets cache cleared")


def add_sweet(data):
    """Add a new sweet to the database, including category and normalized fields.
    Accepts and stores base64 image strings without modification.
    """
    if sweet_collection is None:
        raise RuntimeError("Database not connected: cannot add sweet")

    # Normalize inputs and coerce types
    try:
        rate_val = float(data.get("rate", 0) or 0)
    except (ValueError, TypeError):
        rate_val = 0

    # Validate and normalize unit field
    unit_input = data.get("unit", "Kg").strip().lower()
    if unit_input in ["kg", "kilogram"]:
        unit = "Kg"
    elif unit_input == "piece":
        unit = "piece"
    else:
        unit = "Kg"  # Default to 'Kg' if invalid

    # Accept image from multiple keys: image, image_url, or imageUrl
    image_data = data.get("image") or data.get("image_url") or data.get("imageUrl") or ""
    
    # Validate base64 image format if image is provided
    if image_data:
        if not isinstance(image_data, str):
            raise ValueError("Image must be a string")
        if not image_data.startswith('data:image/'):
            raise ValueError("Invalid image format. Must be a base64 data URI starting with 'data:image/'")
        print(f"📸 Storing image for '{data.get('name', 'Unknown')}' - Length: {len(image_data)} characters")
        print(f"   Image starts with: {image_data[:50]}...")
    else:
        print(f"⚠️ No image provided for '{data.get('name', 'Unknown')}'")

    is_festival = bool(data.get("isFestival", False))
    print(f"🟡 add_sweet: isFestival received = {data.get('isFestival')}, stored = {is_festival}")
    doc = {
        "name": data.get("name", "").strip(),
        "rate": rate_val,
        "description": data.get("description", ""),
        # Store as 'image' field to match common frontend expectations
        "image": image_data,
        "category": data.get("category", "").strip(),
        "unit": unit,
        "isFestival": is_festival,
    }

    result = sweet_collection.insert_one(doc)
    print(f"✅ Sweet '{doc['name']}' added successfully with ID: {result.inserted_id}")
    clear_sweets_cache()  # Clear cache when new sweet is added

def get_sweets(category: str | None = None):
    """Get sweets from the database with optional category filter.
    Includes '_id' (as string) and ensures 'category' in the result.
    Returns complete image field without modification.
    Uses in-memory caching to reduce database calls.
    """
    global _sweets_cache
    
    if sweet_collection is None:
        print("⚠️ Database not connected; returning empty sweets list")
        return []
    
    current_time = time.time()
    
    # Check cache for requests without category filter
    if not category and _sweets_cache["data"] is not None:
        cache_age = current_time - _sweets_cache["timestamp"]
        if cache_age < _sweets_cache["ttl"]:
            print(f"⚡ Returning cached sweets ({len(_sweets_cache['data'])} items, age: {cache_age:.1f}s)")
            return _sweets_cache["data"]
    
    start_time = time.time()
    
    query = {}
    if category:
        # Case-insensitive CONTAINS match for robustness (e.g., "din" matches "Dinner")
        cat = str(category).strip()
        if cat:
            query["category"] = re.compile(re.escape(cat), re.IGNORECASE)
    docs = list(sweet_collection.find(query))
    
    db_time = time.time() - start_time
    print(f"⏱️ Database query took {db_time:.2f}s for {len(docs)} items")
    
    # Backfill category and unit for older records, normalize image field
    for d in docs:
        if d.get("_id") is not None:
            d["_id"] = str(d["_id"])
        if "category" not in d:
            d["category"] = "Uncategorized"
        if "unit" not in d:
            d["unit"] = "Kg"  # Default to 'Kg' for backward compatibility
        if "isFestival" not in d:
            d["isFestival"] = False  # Default to False for backward compatibility

        # --- Ensure 'price' field is always present ---
        # If 'price' is missing but 'rate' exists, use 'rate' as 'price'
        if "price" not in d or d["price"] is None:
            if "rate" in d and d["rate"] is not None:
                d["price"] = d["rate"]

        # Normalize image field: ensure 'image' field exists
        # Support legacy records that may have 'image_url' or 'imageUrl'
        if "image" not in d:
            d["image"] = d.get("image_url") or d.get("imageUrl") or ""

        # Log image info for debugging (only first sweet to avoid spam)
        if docs.index(d) == 0 and d.get("image"):
            print(f"📸 Returning sweet '{d.get('name')}' - Image length: {len(d['image'])} characters")
    
    # Cache the result (only for non-filtered queries)
    if not category:
        _sweets_cache["data"] = docs
        _sweets_cache["timestamp"] = current_time
        print(f"💾 Cached {len(docs)} sweets")
    
    return docs

def get_sweet_by_id(id_str: str):
    """Fetch a single sweet by its ObjectId string. Returns dict or None.
    Returns complete image field without modification.
    """
    if sweet_collection is None:
        return None
    try:
        oid = ObjectId(id_str)
    except Exception:
        return None
    doc = sweet_collection.find_one({"_id": oid})
    if not doc:
        return None
    # Normalize id to string for callers
    doc["_id"] = str(doc["_id"]) if doc.get("_id") is not None else None
    # Backfill unit for backward compatibility
    if "unit" not in doc:
        doc["unit"] = "Kg"
    
    # Normalize image field: ensure 'image' field exists
    # Support legacy records that may have 'image_url' or 'imageUrl'
    if "image" not in doc:
        doc["image"] = doc.get("image_url") or doc.get("imageUrl") or ""
    
    return doc

def remove_sweet(name=None, sweet_id=None):
    """Remove a sweet from the database by name or id."""
    if sweet_collection is None:
        raise RuntimeError("Database not connected: cannot remove sweet")
    if sweet_id:
        from bson import ObjectId
        try:
            oid = ObjectId(sweet_id)
        except Exception:
            print(f"❌ Invalid sweet_id: {sweet_id}")
            return False
        result = sweet_collection.delete_one({"_id": oid})
        print(f"🟢 remove_sweet: deleted by id {sweet_id}, deleted count: {result.deleted_count}")
        if result.deleted_count > 0:
            clear_sweets_cache()  # Clear cache when sweet is removed
        return result.deleted_count > 0
    elif name:
        result = sweet_collection.delete_one({"name": name})
        print(f"🟢 remove_sweet: deleted by name '{name}', deleted count: {result.deleted_count}")
        if result.deleted_count > 0:
            clear_sweets_cache()  # Clear cache when sweet is removed
        return result.deleted_count > 0
    else:
        print("❌ remove_sweet: no id or name provided")
        return False

def update_sweet(sweet_id, data):
    """Update an existing sweet in the database."""
    if sweet_collection is None:
        raise RuntimeError("Database not connected: cannot update sweet")
    
    try:
        # Convert string ID to ObjectId
        if isinstance(sweet_id, str):
            sweet_id = ObjectId(sweet_id)
        
        # Prepare update data
        update_data = {}
        
        # Update basic fields if provided
        if "name" in data:
            update_data["name"] = data["name"]
        # Handle price update - store as 'rate' to match add_sweet and frontend
        if "price" in data:
            update_data["rate"] = float(data["price"])
        if "unit" in data:
            update_data["unit"] = data["unit"]
        if "category" in data:
            update_data["category"] = data["category"]
        if "image" in data:
            update_data["image"] = data["image"]
        
        # Update the sweet
        result = sweet_collection.update_one(
            {"_id": sweet_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise ValueError("Sweet not found or no changes made")
        
        clear_sweets_cache()  # Clear cache when sweet is updated
        return True
        
    except Exception as e:
        print(f"❌ Error updating sweet: {e}")
        raise e
