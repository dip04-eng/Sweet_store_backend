"""
Test order placement with email - simulates real order
"""
import requests
import json

# Backend URL
BACKEND_URL = "http://127.0.0.1:5000"

# Test order data (same structure as frontend sends)
order_data = {
    "customerName": "Test Customer",
    "mobile": "9876543210",
    "address": "123 Test Street",
    "orderDate": "2025-12-30",
    "deliveryDate": "2025-12-31",
    "preference": "No preference",
    "items": [
        {
            "sweetId": "test123",
            "sweetName": "Jalebi",
            "quantity": 0.5,
            "unit": "kg",
            "price": 200
        },
        {
            "sweetId": "test456",
            "sweetName": "Gulab Jamun",
            "quantity": 1,
            "unit": "kg",
            "price": 250
        }
    ],
    "total": 350
}

print("="*60)
print("🧪 Testing Real Order Placement with Email")
print("="*60)
print(f"\nSending order to: {BACKEND_URL}/place_order")
print(f"Customer: {order_data['customerName']}")
print(f"Total: ₹{order_data['total']}")

try:
    response = requests.post(
        f"{BACKEND_URL}/place_order",
        json=order_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("\n✅ Order placed successfully!")
        print("Check the backend terminal for email sending logs.")
        print("Check manager email: mdasif1592003@gmail.com")
    else:
        print("\n❌ Order placement failed!")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("="*60)
