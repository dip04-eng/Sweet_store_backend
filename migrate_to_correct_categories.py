from model.sweet_model import sweet_collection, clear_sweets_cache

print("🔄 Moving items to correct categories...")
print("=" * 50)

# Move Dahi and Paneer items from Decorate to Dairy
dairy_items = [
    'Dahi (दही)',
    'Dahi (दही) - 5 KG', 
    'Dahi (दही) - 10Kg',
    'Misti Dahi( मिष्टी दही)',
    'Paneer (पनीर)',
    'Special Paneer(स्पेशल पनीर)',
    'Kheer Dahi(खीर दही)'
]

dairy_result = sweet_collection.update_many(
    {'name': {'$in': dairy_items}},
    {'$set': {'category': 'Dairy'}}
)
print(f'✅ Moved {dairy_result.modified_count} items to Dairy category')
for item in dairy_items:
    print(f'   - {item}')

print()

# Move dates-related items to Dates category
dates_result = sweet_collection.update_one(
    {'name': 'MAZAFATI'},
    {'$set': {'category': 'Dates'}}
)
print(f'✅ Moved {dates_result.modified_count} item to Dates category')
print(f'   - MAZAFATI')

# Clear cache to reflect changes
clear_sweets_cache()

print("\n" + "=" * 50)
print("✨ Category migration completed successfully!")
print("=" * 50)

# Show summary
from model.sweet_model import get_sweets
all_items = get_sweets()

dairy = [s for s in all_items if s.get('category') == 'Dairy']
dates = [s for s in all_items if s.get('category') == 'Dates']
decorate = [s for s in all_items if s.get('category') == 'Decorate']

print(f"\n📊 Summary:")
print(f"   Dairy: {len(dairy)} items")
print(f"   Dates: {len(dates)} items")
print(f"   Decorate: {len(decorate)} items (baskets & containers)")
