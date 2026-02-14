from model.sweet_model import sweet_collection, get_sweets

# Get all unique categories in the database
pipeline = [
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]

print("📊 All categories in database:")
print("=" * 50)
for result in sweet_collection.aggregate(pipeline):
    category = result['_id'] if result['_id'] else "No Category"
    count = result['count']
    print(f"{category}: {count} items")

print("\n" + "=" * 50)
print("\n🔍 Searching for potential Dairy/Dates items...")
print("=" * 50)

# Get all items and check for dairy/dates related items
all_items = get_sweets()

# Look for dairy-related items (dahi, paneer, milk, etc.)
dairy_keywords = ['dahi', 'paneer', 'milk', 'cream', 'kheer', 'misti']
potential_dairy = [s for s in all_items if any(keyword in s.get('name', '').lower() for keyword in dairy_keywords)]

print(f"\n🥛 Potential Dairy items ({len(potential_dairy)}):")
for item in potential_dairy:
    print(f"  - {item.get('name')} (Current category: {item.get('category')})")

# Look for dates-related items
dates_keywords = ['date', 'khajur', 'mazafati']
potential_dates = [s for s in all_items if any(keyword in s.get('name', '').lower() for keyword in dates_keywords)]

print(f"\n📅 Potential Dates items ({len(potential_dates)}):")
for item in potential_dates:
    print(f"  - {item.get('name')} (Current category: {item.get('category')})")
