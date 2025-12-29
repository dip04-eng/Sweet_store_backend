"""
Test email and PDF generation
"""
from utils.pdf_generator import generate_order_pdf
from utils.email_service import send_order_invoice_to_manager
import os
from dotenv import load_dotenv

load_dotenv(".env")

def test_email_pdf():
    print("="*60)
    print("🧪 Testing Email & PDF System")
    print("="*60)
    
    outlook_email = os.getenv("OUTLOOK_EMAIL")
    manager_email = os.getenv("MANAGER_EMAIL")
    
    if not outlook_email:
        print("\n❌ OUTLOOK_EMAIL not found in .env file")
        return False
    
    print(f"\n✅ Outlook Email: {outlook_email}")
    print(f"✅ Manager Email: {manager_email}")
    
    # Test order data
    test_order = {
        '_id': 'TEST123',
        'customerName': 'Test Customer',
        'mobile': '+919876543210',
        'address': '123 Test Street, Test City',
        'orderDate': '2025-12-30',
        'deliveryDate': '2025-12-31',
        'total': 450,
        'items': [
            {
                'sweetName': 'Jalebi',
                'quantity': 0.5,
                'unit': 'kg',
                'price': 200
            },
            {
                'sweetName': 'Gulab Jamun',
                'quantity': 1,
                'unit': 'kg',
                'price': 250
            }
        ]
    }
    
    print("\n📄 Generating PDF invoice...")
    pdf_path = generate_order_pdf(test_order, "test_invoice.pdf")
    
    if not pdf_path:
        print("❌ PDF generation failed!")
        return False
    
    print(f"✅ PDF generated: {pdf_path}")
    
    print("\n📧 Sending email to manager...")
    result = send_order_invoice_to_manager(test_order, pdf_path)
    
    # Clean up
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"🗑️ Cleaned up: {pdf_path}")
    
    print("\n" + "="*60)
    print(f"📊 Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    print("="*60)
    
    if result:
        print(f"\n🎉 Email sent successfully!")
        print(f"Check your manager email: {manager_email}")
    else:
        print("\n❌ Email sending failed!")
    
    return result

if __name__ == "__main__":
    test_email_pdf()
