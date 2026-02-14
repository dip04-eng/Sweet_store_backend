from model.sweet_model import sweet_collection

# Update all items with category "Other" to "Decorate"
result = sweet_collection.update_many(
    {'category': 'Other'}, 
    {'$set': {'category': 'Decorate'}}
)

print(f'✅ Updated {result.modified_count} items from "Other" to "Decorate"')

# Show the updated items
from model.sweet_model import get_sweets
decorate_items = [s for s in get_sweets() if s.get('category') == 'Decorate']
print(f'\n📦 Items now in Decorate category:')
for item in decorate_items:
    print(f"  - {item.get('name')}")
