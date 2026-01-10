from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model.sweet_model import add_sweet, get_sweets, remove_sweet, get_sweet_by_id
from model.order_model import place_order, get_orders, get_daily_summary, update_order_status, edit_order
from utils.pdf_generator import generate_order_pdf, generate_orders_statement_pdf
from utils.email_service import send_order_invoice_to_manager, send_contact_form_to_manager
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv(".env")

app = Flask(__name__)

# Configure CORS to allow requests from frontend and handle large responses
CORS(app, 
     origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "https://server.uemcseaiml.org", "https://sweet-store-frontend-ten.vercel.app"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     expose_headers=["Content-Type", "Content-Disposition"],
     supports_credentials=True,
     max_age=3600
)

# Increase max content length to handle large base64 images (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/server-date", methods=["GET"])
def get_server_date():
    """Get current server date in YYYY-MM-DD format."""
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 Server date requested: {current_date}")
    return jsonify({"date": current_date})

@app.route("/sweets", methods=["GET"])
def fetch_sweets():
    """Get all available sweets with complete image data.
    Returns full base64 image strings without truncation.
    """
    category = request.args.get("category")
    sweets = get_sweets(category)
    
    # Log response size for debugging
    if sweets:
        print(f"📤 Returning {len(sweets)} sweet(s) to frontend")
        # Log details of first sweet for verification
        if len(sweets) > 0 and sweets[0].get('image'):
            print(f"   First sweet: {sweets[0].get('name')}")
            print(f"   Unit: {sweets[0].get('unit')}")
            print(f"   Image length: {len(sweets[0].get('image', ''))} chars")
            print(f"   Has valid base64: {str(sweets[0].get('image', '')).startswith('data:image/')}")
    
    return jsonify(sweets)

@app.route("/place_order", methods=["POST"])
def new_order():
    """
    Place a new order.
    Now includes delivery date support.
    """
    data = request.get_json()
    
    print("\n" + "="*60)
    print("📝 NEW ORDER RECEIVED")
    print("="*60)
    
    if not data or "items" not in data:
        print("❌ Invalid order data: missing 'items' field")
        return jsonify({"error": "Invalid order data. 'items' field is required."}), 400
    
    items = data.get("items", [])
    
    if not items:
        print("❌ Empty order: no items provided")
        return jsonify({"error": "Order must contain at least one item"}), 400
    
    # Validate required date fields
    if "orderDate" not in data or not data.get("orderDate"):
        print("❌ Missing required field: orderDate")
        return jsonify({"error": "Order date is required"}), 400
    
    if "deliveryDate" not in data or not data.get("deliveryDate"):
        print("❌ Missing required field: deliveryDate")
        return jsonify({"error": "Delivery date is required"}), 400
    
    print(f"📅 Order Date: {data.get('orderDate')}")
    print(f"📅 Delivery Date: {data.get('deliveryDate')}")
    
    print(f"\n📦 Order Details:")
    print(f"   Customer: {data.get('customerName', 'Unknown')}")
    print(f"   Total Items: {len(items)}")
    print(f"   Total Amount: ₹{data.get('total', 0)}")
    
    for item in items:
        if not item.get("sweetId"):
            error_msg = f"Missing sweetId for item: {item.get('sweetName', 'Unknown')}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Validate quantity: required and must be >= 1
        if "quantity" not in item:
            error_msg = f"Missing quantity for item: {item.get('sweetName', 'Unknown')}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        try:
            quantity = float(item.get("quantity", 0))
            if quantity < 1:
                error_msg = f"Quantity must be at least 1 for item: {item.get('sweetName', 'Unknown')}"
                print(f"❌ {error_msg}")
                return jsonify({"error": error_msg}), 400
        except (ValueError, TypeError):
            error_msg = f"Invalid quantity for item: {item.get('sweetName', 'Unknown')}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
    
    print("\n💾 Saving order to database...")
    try:
        order_result = place_order(data)
        print("✅ Order saved successfully!")
        print(f"Order ID: {order_result.get('_id')}")
        
        # Generate PDF invoice and send to manager
        print("\n📧 Generating invoice and sending to manager...")
        try:
            order_id = str(order_result.get('_id'))
            pdf_filename = f"invoice_{order_id}.pdf"
            
            print(f"   Generating PDF: {pdf_filename}...")
            pdf_path = generate_order_pdf(order_result, pdf_filename)
            
            if pdf_path:
                print(f"   PDF created at: {pdf_path}")
                print(f"   Sending email to manager...")
                email_result = send_order_invoice_to_manager(order_result, pdf_path)
                
                if email_result:
                    print(f"   ✅ Email sent successfully!")
                else:
                    print(f"   ❌ Email sending failed!")
                
                # Clean up PDF file after sending
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    print(f"   🗑️ Cleaned up temporary PDF: {pdf_filename}")
            else:
                print(f"   ❌ PDF generation failed!")
                
        except Exception as email_error:
            print(f"❌ Email notification error: {str(email_error)}")
            import traceback
            traceback.print_exc()
            # Don't fail the order if email fails
        
        print("="*60 + "\n")
        return jsonify({
            "message": "Order placed successfully! 🎉",
            "orderDate": data.get("orderDate"),
            "deliveryDate": data.get("deliveryDate"),
            "total": data.get("total"),
            "customerName": data.get("customerName")
        }), 201
    except Exception as e:
        error_msg = f"Failed to save order: {str(e)}"
        print(f"❌ {error_msg}")
        print("="*60 + "\n")
        return jsonify({"error": error_msg}), 500

# ---------- ADMIN ROUTES ----------

@app.route("/admin/add_sweet", methods=["POST"])
def admin_add_sweet():
    """Add a new sweet to the inventory.
    Accepts base64 image strings and stores them without modification.
    Supports optional existingSweetId: if provided, use its details unless overridden by payload.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Category is always required
    if "category" not in data or not str(data.get("category", "")).strip():
        return jsonify({"error": "Missing required field: category"}), 400

    # Validate unit field if provided
    if "unit" in data:
        unit_value = str(data.get("unit", "")).strip().lower()
        if unit_value not in ["piece", "kg"]:
            return jsonify({"error": "Invalid unit. Must be 'piece' or 'kg'"}), 400
    
    # Validate image format if provided (accept from 'image', 'image_url', or 'imageUrl')
    image_data = data.get("image") or data.get("image_url") or data.get("imageUrl")
    if image_data:
        if not isinstance(image_data, str):
            return jsonify({"error": "Image must be a string"}), 400
        if not image_data.startswith('data:image/'):
            return jsonify({"error": "Invalid image format. Must be a base64 data URI starting with 'data:image/'"}), 400
        print(f"📸 Received image - Length: {len(image_data)} characters")

    existing_id = data.get("existingSweetId")
    base = {}

    if existing_id:
        found = get_sweet_by_id(existing_id)
        if not found:
            return jsonify({"error": "Existing sweet not found"}), 404
        base = {
            "name": found.get("name", ""),
            "rate": found.get("rate", 0),
            "description": found.get("description", ""),
            "image": found.get("image") or found.get("image_url") or found.get("imageUrl") or "",
            "unit": found.get("unit", "kg"),
        }
        # Merge with overrides from the request body
        payload = {
            "name": data.get("name", base["name"]),
            "rate": data.get("rate", base["rate"]),
            "description": data.get("description", base["description"]),
            "image": data.get("image") or data.get("image_url") or data.get("imageUrl") or base["image"],
            "category": data.get("category"),
            "unit": data.get("unit", base["unit"]),
        }
    else:
        # For manual entry, require name and rate
        for field in ["name", "rate"]:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        # Normalize image field name to 'image'
        payload = dict(data)
        if "image_url" in payload or "imageUrl" in payload:
            payload["image"] = payload.get("image") or payload.get("image_url") or payload.get("imageUrl")

    try:
        add_sweet(payload)
        return jsonify({"message": "Sweet added successfully", "sweet": payload.get("name")}), 201
    except ValueError as e:
        # Handle validation errors (e.g., invalid image format)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to add sweet: {str(e)}"}), 500

@app.route("/admin/remove_sweet", methods=["DELETE"])
def admin_remove_sweet():
    """Remove a sweet from the inventory."""
    name = request.args.get("name")
    
    if not name:
        return jsonify({"error": "Sweet name is required"}), 400
    
    try:
        remove_sweet(name)
        return jsonify({"message": f"Sweet '{name}' removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to remove sweet: {str(e)}"}), 500

@app.route("/admin/orders", methods=["GET"])
def admin_orders():
    """Get all orders with optional delivery date filtering."""
    try:
        orders = get_orders()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch orders: {str(e)}"}), 500

@app.route("/admin/daily_summary", methods=["GET"])
def admin_summary():
    """Get daily sales summary."""
    try:
        summary = get_daily_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch daily summary: {str(e)}"}), 500

# ----- ORDER ADMIN UPDATES -----

@app.route("/admin/update_order_status", methods=["PUT"])
def admin_update_order_status():
    """U
        # Send SMS notification to customer about status change
        customer_phone = updated.get('mobile', '')
        if customer_phone:
            print(f"\n📱 Sending status update SMS to customer...")
            send_order_status_update(
                customer_phone=customer_phone,
                order_id=order_id,
                status=status
            )
        
        pdate status of an order by orderId."""
    # Accept JSON, form, or query params but require BOTH orderId and status
    data = request.get_json(silent=True) or {}
    if not data and request.form:
        data = request.form.to_dict()

    order_id = (
        data.get("orderId")
        or data.get("_id")
        or data.get("id")
        or request.args.get("orderId")
        or request.args.get("_id")
        or request.args.get("id")
    )
    raw_status = data.get("status") or request.args.get("status")

    if not order_id or not raw_status:
        return jsonify({"error": "Missing required fields: orderId and status"}), 400

    status_lc = str(raw_status).strip().lower()
    if status_lc not in ("delivered", "cancelled"):
        return jsonify({"error": "Invalid status. Allowed values: Delivered or Cancelled"}), 400
    status = "Delivered" if status_lc == "delivered" else "Cancelled"

    try:
        updated = update_order_status(order_id, status)
        if not updated:
            return jsonify({"error": "Order not found"}), 404
        success_msg = "Order marked as Delivered" if status == "Delivered" else "Order Cancelled"
        return jsonify({"message": success_msg, "order": updated}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update order status: {str(e)}"}), 500


@app.route("/admin/edit_order/<order_id>", methods=["PUT"])
def admin_edit_order(order_id):
    """Edit fields of an order by ID. Only provided fields are updated."""
    data = request.get_json() or {}
    try:
        updated = edit_order(order_id, data)
        if not updated:
            return jsonify({"error": "Order not found"}), 404
        return jsonify({"message": "Order updated successfully", "order": updated}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to edit order: {str(e)}"}), 500

@app.route("/admin/fix-festival-sweets", methods=["POST"])
def fix_festival_sweets():
    """Update specific sweets to mark them as festival sweets."""
    from model.sweet_model import sweet_collection
    
    if sweet_collection is None:
        return jsonify({"error": "Database not connected"}), 500
    
    # Get the sweet name from request
    data = request.get_json() or {}
    sweet_name = data.get("sweetName", "")
    
    if not sweet_name:
        return jsonify({"error": "sweetName is required"}), 400
    
    # Update the sweet to be a festival sweet
    result = sweet_collection.update_one(
        {"name": sweet_name},
        {"$set": {"isFestival": True}}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": f"Sweet '{sweet_name}' not found"}), 404
    
    return jsonify({
        "message": f"✅ '{sweet_name}' is now a Festival sweet!",
        "matched": result.matched_count,
        "modified": result.modified_count
    }), 200


@app.route("/admin/download_statement", methods=["POST", "OPTIONS"])
def admin_download_statement():
    """Generate and download a PDF statement for filtered orders."""
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    try:
        data = request.get_json() or {}
        orders = data.get('orders', [])
        filters = data.get('filters', {})
        
        if not orders:
            return jsonify({"error": "No orders provided"}), 400
        
        print(f"\n📥 Statement download requested")
        print(f"   Orders count: {len(orders)}")
        print(f"   Filters: {filters}")
        
        # Generate PDF
        pdf_bytes = generate_orders_statement_pdf(orders, filters)
        
        if not pdf_bytes:
            return jsonify({"error": "Failed to generate PDF"}), 500
        
        # Create BytesIO buffer for sending
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        
        # Generate filename with current date
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"orders_statement_{date_str}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ Statement download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate statement: {str(e)}"}), 500


@app.route("/contact", methods=["POST", "OPTIONS"])
def submit_contact_form():
    """Handle contact form submissions and send email to manager."""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract contact data
        contact_data = {
            'name': data.get('name', '').strip(),
            'email': data.get('email', '').strip(),
            'phone': data.get('phone', '').strip() or 'Not provided',
            'message': data.get('message', '').strip()
        }
        
        print(f"📧 Contact form submission received from: {contact_data['name']}")
        
        # Send email to manager
        email_sent = send_contact_form_to_manager(contact_data)
        
        if email_sent:
            print(f"✅ Contact form email sent successfully to manager")
            return jsonify({
                "success": True,
                "message": "Thank you! Your message has been sent successfully. We'll get back to you soon."
            }), 200
        else:
            print(f"⚠️ Failed to send contact form email")
            return jsonify({
                "success": False,
                "message": "Message received but email notification failed. We'll still review your message."
            }), 200
            
    except Exception as e:
        print(f"❌ Contact form error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to process contact form: {str(e)}"}), 500


if __name__ == "__main__":
    # Get host and port from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    
    print(f"🚀 Starting server on http://{host}:{port}")
    
    # Disable auto-reloader on Windows to avoid intermittent WinError 10038 during restarts
    app.run(host=host, port=port, debug=True, use_reloader=False)