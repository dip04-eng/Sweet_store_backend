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
# Support multiple manager emails (comma-separated)
MANAGER_EMAILS_STR = os.getenv("MANAGER_EMAIL", "")
MANAGER_EMAIL = MANAGER_EMAILS_STR  # Keep for backward compatibility
MANAGER_EMAILS = [email.strip() for email in MANAGER_EMAILS_STR.split(',') if email.strip()]

def send_email_with_attachment(to_email, subject, body, attachment_path=None):
    """
    Send email with optional PDF attachment using Outlook SMTP.
    
    Args:
        to_email: Recipient email address (string) or list of email addresses
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
        
        # Handle multiple recipients
        if isinstance(to_email, list):
            msg['To'] = ', '.join(to_email)
            recipients = to_email
        else:
            msg['To'] = to_email
            recipients = [to_email]
        
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
    Send order invoice PDF to all manager emails.
    
    Args:
        order_data: Dictionary containing order information
        pdf_path: Path to generated PDF invoice
    
    Returns:
        Boolean: True if successful, False otherwise
    """
    print(f"📧 send_order_invoice_to_manager called")
    print(f"   Manager Emails: {MANAGER_EMAILS}")
    print(f"   PDF Path: {pdf_path}")
    print(f"   Order Data Keys: {order_data.keys() if order_data else 'None'}")
    
    if not MANAGER_EMAILS:
        print("⚠️ Manager email not configured")
        return False
    
    # Get sequential order ID
    order_number = order_data.get('orderNumber', None)
    if order_number:
        order_id = f"{order_number:04d}"  # Format as 0001, 0002, etc.
    else:
        order_id = str(order_data.get('_id', 'N/A'))  # Fallback to MongoDB ID
    
    customer_name = order_data.get('customerName', 'Customer')
    total = order_data.get('total', 0)
    
    # Format delivery date as dd-mm-yyyy
    delivery_date = order_data.get('deliveryDate', 'N/A')
    if delivery_date != 'N/A':
        try:
            from datetime import datetime
            date_obj = datetime.strptime(str(delivery_date).split('T')[0], '%Y-%m-%d')
            delivery_date = date_obj.strftime('%d-%m-%Y')
        except:
            pass
    
    items = order_data.get('items', [])
    
    print(f"   Order ID: {order_id}")
    print(f"   Customer: {customer_name}")
    
    subject = f"🔔 New Order #{order_id} - {customer_name}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="bacKground-color: #FFD700; padding: 20px; text-align: center;">
            <h1 style="color: #0D0D0D; margin: 0;">🍬 Mansoor Hotel & Sweets</h1>
        </div>
        
        <div style="padding: 20px;">
            <h2 style="color: #D2691E;">New Order Received!</h2>
            
            <p>A new order has been placed. Please find the details below:</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; bacKground-color: #FFF8DC; font-weight: bold;">Order ID:</td>
                    <td style="padding: 10px; bacKground-color: #FFFEF0;">{order_id}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; bacKground-color: #FFF8DC; font-weight: bold;">Customer:</td>
                    <td style="padding: 10px; bacKground-color: #FFFEF0;">{customer_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; bacKground-color: #FFF8DC; font-weight: bold;">Mobile:</td>
                    <td style="padding: 10px; bacKground-color: #FFFEF0;">{order_data.get('mobile', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; bacKground-color: #FFF8DC; font-weight: bold;">Total Amount:</td>
                    <td style="padding: 10px; bacKground-color: #FFFEF0; font-size: 18px; font-weight: bold; color: #D2691E;">₹{total}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; bacKground-color: #FFF8DC; font-weight: bold;">Delivery Date:</td>
                    <td style="padding: 10px; bacKground-color: #FFFEF0;">{delivery_date}</td>
                </tr>
            </table>
            
            <h3 style="color: #D2691E; margin-top: 30px;">Order Items:</h3>
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0; border: 1px solid #ddd;">
                <thead>
                    <tr style="bacKground-color: #D2691E; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Sweet Name</th>
                        <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Quantity</th>
                        <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">{item.get('sweetName', 'N/A')}</td>
                        <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{item.get('quantity', 0)} {item.get('unit', 'Kg')}</td>
                        <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">₹{item.get('price', 0)}</td>
                    </tr>
                    ''' for item in items])}
                </tbody>
            </table>
            
            <p style="bacKground-color: #FFF8DC; padding: 15px; border-left: 4px solid #FFD700;">
                <strong>📎 Invoice Attached:</strong> Please find the detailed invoice PDF attached to this email.
            </p>
            
            <p style="margin-top: 30px; color: #666;">
                You can update the order status from the admin panel.
            </p>
        </div>
        
        <div style="bacKground-color: #F5F5DC; padding: 15px; text-align: center; margin-top: 20px;">
            <p style="margin: 0; color: #666; font-size: 12px;">
                This is an automated notification from Sweet Store Management System
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email_with_attachment(MANAGER_EMAILS, subject, body, pdf_path)

def send_contact_form_to_manager(contact_data):
    """
    Send contact form submission to all manager emails.
    
    Args:
        contact_data: Dictionary containing name, email, phone, message
    
    Returns:
        Boolean: True if successful, False otherwise
    """
    if not MANAGER_EMAILS:
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
        <div style="bacKground-color: #C41E3A; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">🍬 Mansoor Hotel & Sweets</h1>
        </div>
        
        <div style="padding: 20px;">
            <h2 style="color: #C41E3A;">New Contact Form Message</h2>
            
            <p>Someone has sent a message through the website contact form:</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr>
                    <td style="padding: 12px; bacKground-color: #FFF8DC; font-weight: bold; width: 150px;">Name:</td>
                    <td style="padding: 12px; bacKground-color: #FFFEF0;">{name}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; bacKground-color: #FFF8DC; font-weight: bold;">Email:</td>
                    <td style="padding: 12px; bacKground-color: #FFFEF0;"><a href="mailto:{email}">{email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 12px; bacKground-color: #FFF8DC; font-weight: bold;">Phone:</td>
                    <td style="padding: 12px; bacKground-color: #FFFEF0;">{phone}</td>
                </tr>
            </table>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #C41E3A; margin-bottom: 10px;">Message:</h3>
                <div style="bacKground-color: #FFF8DC; padding: 20px; border-left: 4px solid #C41E3A; white-space: pre-wrap;">
{message}
                </div>
            </div>
            
            <p style="bacKground-color: #FEF3E2; padding: 15px; border-left: 4px solid #C41E3A; margin-top: 20px;">
                <strong>💡 Action Required:</strong> Please respond to this inquiry at your earliest convenience.
            </p>
        </div>
        
        <div style="bacKground-color: #F5F5DC; padding: 15px; text-align: center; margin-top: 20px;">
            <p style="margin: 0; color: #666; font-size: 12px;">
                This is an automated notification from Mansoor Hotel & Sweets Contact Form
            </p>
        </div>
    </body>
    </html>
    """
    
    print(f"📧 Sending contact form to managers: {MANAGER_EMAILS}")
    return send_email_with_attachment(MANAGER_EMAILS, subject, body)

def send_sales_report_to_manager(date, sales_data, orders, pdf_bytes):
    """
    Send next day sales report PDF to all manager emails.
    
    Args:
        date: Report date string (YYYY-MM-DD format)
        sales_data: Dictionary containing sales summary
        orders: List of orders for the date
        pdf_bytes: PDF file as bytes
    
    Returns:
        Boolean: True if successful, False otherwise
    """
    if not MANAGER_EMAILS:
        print("⚠️ Manager email not configured")
        return False
    
    try:
        from datetime import datetime
        # Format date for display
        try:
            date_obj = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d %B %Y')
        except:
            formatted_date = date
        
        total_orders = len(orders)
        total_revenue = sales_data.get('totalRevenue', 0)
        total_paid = sales_data.get('totalPaid', 0)
        total_due = sales_data.get('totalDue', 0)
        
        subject = f"📊 Sales Report for {formatted_date} - Mansoor Hotel & Sweets"
        
        # Create HTML body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #C41E3A; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">🍬 Mansoor Hotel & Sweets</h1>
                <p style="color: #FFD700; margin: 5px 0 0 0; font-size: 14px;">Daily Sales Report</p>
            </div>
            
            <div style="padding: 20px;">
                <h2 style="color: #C41E3A;">Sales Report for {formatted_date}</h2>
                
                <p>Dear Manager,</p>
                <p>Please find below the sales summary for the next day's orders:</p>
                
                <div style="background-color: #FFF8DC; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #C41E3A; margin-top: 0;">📈 Summary</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Total Orders:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right; font-size: 18px; color: #C41E3A;">{total_orders}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Total Revenue:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right; font-size: 18px; color: #008000;">₹{total_revenue:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Total Paid:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right; font-size: 16px; color: #008000;">₹{total_paid:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold;">Total Due:</td>
                            <td style="padding: 10px; text-align: right; font-size: 16px; color: #DC143C;">₹{total_due:,.2f}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #FEF3E2; padding: 15px; border-left: 4px solid #FFD700; margin: 20px 0;">
                    <p style="margin: 0;"><strong>📎 Detailed Report Attached:</strong></p>
                    <p style="margin: 10px 0 0 0;">A comprehensive PDF report with all order details is attached to this email for your review.</p>
                </div>
                
                <div style="background-color: #E8F5E9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                    <p style="margin: 0;"><strong>💡 Next Steps:</strong></p>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>Review the orders scheduled for delivery on {formatted_date}</li>
                        <li>Ensure adequate stock for all items</li>
                        <li>Coordinate with the preparation team</li>
                        <li>Monitor payment collection for due amounts</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px; color: #666;">This report helps you plan and prepare for the next day's deliveries efficiently.</p>
            </div>
            
            <div style="background-color: #F5F5DC; padding: 15px; text-align: center; margin-top: 20px;">
                <p style="margin: 0; color: #666; font-size: 12px;">
                    This is an automated daily report from Mansoor Hotel & Sweets Management System<br/>
                    Generated on {datetime.now().strftime('%d-%m-%Y at %I:%M %p')}
                </p>
            </div>
        </body>
        </html>
        """
        
        # Save PDF temporarily
        import tempfile
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb')
        temp_pdf.write(pdf_bytes)
        temp_pdf.close()
        
        print(f"📧 Sending sales report email to managers: {MANAGER_EMAILS}")
        print(f"   Report Date: {formatted_date}")
        print(f"   Total Orders: {total_orders}")
        print(f"   Total Revenue: ₹{total_revenue}")
        
        # Send email with PDF attachment to all managers
        result = send_email_with_attachment(MANAGER_EMAILS, subject, body, temp_pdf.name)
        
        # Clean up temporary file
        try:
            os.unlink(temp_pdf.name)
        except:
            pass
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to send sales report email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
