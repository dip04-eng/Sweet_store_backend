import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv(".env")

# Email Configuration
OUTLOOK_EMAIL = os.getenv("OUTLOOK_EMAIL")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD")
OUTLOOK_HOST = os.getenv("OUTLOOK_HOST", "smtp.office365.com")
OUTLOOK_PORT = int(os.getenv("OUTLOOK_PORT", 587))
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

def send_email_with_attachment(to_email, subject, body, attachment_path=None):
    """
    Send email with optional PDF attachment using Outlook SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (can be HTML)
        attachment_path: Path to PDF file to attach
    
    Returns:
        Boolean: True if successful, False otherwise
    """
    if not all([OUTLOOK_EMAIL, OUTLOOK_PASSWORD, OUTLOOK_HOST]):
        print("⚠️ Email credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = OUTLOOK_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'html'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='pdf')
                attachment.add_header('Content-Disposition', 'attachment', 
                                    filename=os.path.basename(attachment_path))
                msg.attach(attachment)
        
        # Connect to SMTP server
        server = smtplib.SMTP(OUTLOOK_HOST, OUTLOOK_PORT)
        server.starttls()
        server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def send_order_invoice_to_manager(order_data, pdf_path):
    """
    Send order invoice PDF to manager.
    
    Args:
        order_data: Dictionary containing order information
        pdf_path: Path to generated PDF invoice
    
    Returns:
        Boolean: True if successful, False otherwise
    """
    print(f"📧 send_order_invoice_to_manager called")
    print(f"   Manager Email: {MANAGER_EMAIL}")
    print(f"   PDF Path: {pdf_path}")
    print(f"   Order Data Keys: {order_data.keys() if order_data else 'None'}")
    
    if not MANAGER_EMAIL:
        print("⚠️ Manager email not configured")
        return False
    
    order_id = str(order_data.get('_id', 'N/A'))
    customer_name = order_data.get('customerName', 'Customer')
    total = order_data.get('total', 0)
    delivery_date = order_data.get('deliveryDate', 'N/A')
    
    print(f"   Order ID: {order_id}")
    print(f"   Customer: {customer_name}")
    
    subject = f"🔔 New Order #{order_id} - {customer_name}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #FFD700; padding: 20px; text-align: center;">
            <h1 style="color: #0D0D0D; margin: 0;">🍬 Sweet Store</h1>
        </div>
        
        <div style="padding: 20px;">
            <h2 style="color: #D2691E;">New Order Received!</h2>
            
            <p>A new order has been placed. Please find the details below:</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; background-color: #FFF8DC; font-weight: bold;">Order ID:</td>
                    <td style="padding: 10px; background-color: #FFFEF0;">{order_id}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #FFF8DC; font-weight: bold;">Customer:</td>
                    <td style="padding: 10px; background-color: #FFFEF0;">{customer_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #FFF8DC; font-weight: bold;">Mobile:</td>
                    <td style="padding: 10px; background-color: #FFFEF0;">{order_data.get('mobile', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #FFF8DC; font-weight: bold;">Total Amount:</td>
                    <td style="padding: 10px; background-color: #FFFEF0; font-size: 18px; font-weight: bold; color: #D2691E;">₹{total}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #FFF8DC; font-weight: bold;">Delivery Date:</td>
                    <td style="padding: 10px; background-color: #FFFEF0;">{delivery_date}</td>
                </tr>
            </table>
            
            <p style="background-color: #FFF8DC; padding: 15px; border-left: 4px solid #FFD700;">
                <strong>📎 Invoice Attached:</strong> Please find the detailed invoice PDF attached to this email.
            </p>
            
            <p style="margin-top: 30px; color: #666;">
                You can update the order status from the admin panel.
            </p>
        </div>
        
        <div style="background-color: #F5F5DC; padding: 15px; text-align: center; margin-top: 20px;">
            <p style="margin: 0; color: #666; font-size: 12px;">
                This is an automated notification from Sweet Store Management System
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email_with_attachment(MANAGER_EMAIL, subject, body, pdf_path)

def send_contact_form_to_manager(contact_data):
    """
    Send contact form submission to manager.
    
    Args:
        contact_data: Dictionary containing name, email, phone, message
    
    Returns:
        Boolean: True if successful, False otherwise
    """
    if not MANAGER_EMAIL:
        print("⚠️ Manager email not configured")
        return False
    
    name = contact_data.get('name', 'N/A')
    email = contact_data.get('email', 'N/A')
    phone = contact_data.get('phone', 'N/A')
    message = contact_data.get('message', 'N/A')
    
    subject = f"📧 New Contact Form Submission from {name}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #C41E3A; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">🍬 Mansoor Hotel & Sweets</h1>
        </div>
        
        <div style="padding: 20px;">
            <h2 style="color: #C41E3A;">New Contact Form Message</h2>
            
            <p>Someone has sent a message through the website contact form:</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr>
                    <td style="padding: 12px; background-color: #FFF8DC; font-weight: bold; width: 150px;">Name:</td>
                    <td style="padding: 12px; background-color: #FFFEF0;">{name}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; background-color: #FFF8DC; font-weight: bold;">Email:</td>
                    <td style="padding: 12px; background-color: #FFFEF0;"><a href="mailto:{email}">{email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 12px; background-color: #FFF8DC; font-weight: bold;">Phone:</td>
                    <td style="padding: 12px; background-color: #FFFEF0;">{phone}</td>
                </tr>
            </table>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #C41E3A; margin-bottom: 10px;">Message:</h3>
                <div style="background-color: #FFF8DC; padding: 20px; border-left: 4px solid #C41E3A; white-space: pre-wrap;">
{message}
                </div>
            </div>
            
            <p style="background-color: #FEF3E2; padding: 15px; border-left: 4px solid #C41E3A; margin-top: 20px;">
                <strong>💡 Action Required:</strong> Please respond to this inquiry at your earliest convenience.
            </p>
        </div>
        
        <div style="background-color: #F5F5DC; padding: 15px; text-align: center; margin-top: 20px;">
            <p style="margin: 0; color: #666; font-size: 12px;">
                This is an automated notification from Mansoor Hotel & Sweets Contact Form
            </p>
        </div>
    </body>
    </html>
    """
    
    print(f"📧 Sending contact form to manager: {MANAGER_EMAIL}")
    return send_email_with_attachment(MANAGER_EMAIL, subject, body)
