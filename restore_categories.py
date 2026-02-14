from model.sweet_model import sweet_collection, get_sweets

# Update breakfast -> Dairy
breakfast_result = sweet_collection.update_many(
    {'category': {'$regex': '^breakfast$', '$options': 'i'}}, 
    {'$set': {'category': 'Dairy'}}
)
print(f'✅ Updated {breakfast_result.modified_count} items from "breakfast" to "Dairy"')

# Update lunch -> Dates
lunch_result = sweet_collection.update_many(
    {'category': {'$regex': '^lunch$', '$options': 'i'}}, 
    {'$set': {'category': 'Dates'}}
)
print(f'✅ Updated {lunch_result.modified_count} items from "lunch" to "Dates"')

# Show the updated items
all_items = get_sweets()
dairy_items = [s for s in all_items if s.get('category') == 'Dairy']
dates_items = [s for s in all_items if s.get('category') == 'Dates']

print(f'\n📦 Items now in Dairy category ({len(dairy_items)}):')
for item in dairy_items:
    print(f"  - {item.get('name')}")

print(f'\n📦 Items now in Dates category ({len(dates_items)}):')
for item in dates_items:
    print(f"  - {item.get('name')}")
