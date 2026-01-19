from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import sys
import urllib.request
import re

# Font names for English and Hindi
ENGLISH_FONT = 'Helvetica'
HINDI_FONT = 'Helvetica'
UNICODE_FONT = 'Helvetica'
UNICODE_FONT_BOLD = 'Helvetica-Bold'

def download_font(url, font_path, name):
    """Download a font from URL"""
    try:
        print(f"📥 Downloading {name}...")
        urllib.request.urlretrieve(url, font_path)
        print(f"✅ {name} downloaded: {os.path.getsize(font_path)} bytes")
        return True
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")
        return False

def has_devanagari(text):
    """Check if text contains Devanagari (Hindi) characters"""
    if not text:
        return False
    # Devanagari Unicode range: U+0900 to U+097F
    return bool(re.search(r'[\u0900-\u097F]', str(text)))

def format_mixed_text(text, english_font, hindi_font):
    """Format text with appropriate fonts for English and Hindi parts"""
    if not text:
        return str(text)
    
    text = str(text)
    result = []
    current_text = ""
    current_is_hindi = None
    
    for char in text:
        is_hindi = bool(re.match(r'[\u0900-\u097F]', char))
        
        if current_is_hindi is None:
            current_is_hindi = is_hindi
            current_text = char
        elif is_hindi == current_is_hindi:
            current_text += char
        else:
            # Switch font
            if current_is_hindi:
                result.append(f'<font name="{hindi_font}">{current_text}</font>')
            else:
                result.append(f'<font name="{english_font}">{current_text}</font>')
            current_text = char
            current_is_hindi = is_hindi
    
    # Add remaining text
    if current_text:
        if current_is_hindi:
            result.append(f'<font name="{hindi_font}">{current_text}</font>')
        else:
            result.append(f'<font name="{english_font}">{current_text}</font>')
    
    return ''.join(result)

try:
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    
    # Font file paths
    noto_sans_path = os.path.join(backend_dir, 'NotoSans-Regular.ttf')
    noto_devanagari_path = os.path.join(backend_dir, 'NotoSansDevanagari.ttf')
    
    english_registered = False
    hindi_registered = False
    
    # Register NotoSans for English/Latin text
    if os.path.exists(noto_sans_path):
        try:
            pdfmetrics.registerFont(TTFont('NotoSans', noto_sans_path))
            ENGLISH_FONT = 'NotoSans'
            UNICODE_FONT = 'NotoSans'
            UNICODE_FONT_BOLD = 'NotoSans'
            english_registered = True
            print(f"✅ NotoSans (English) font registered")
        except Exception as e:
            print(f"⚠️ Failed to register NotoSans: {e}")
    
    # Download NotoSans if not exists
    if not english_registered:
        noto_sans_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
        if download_font(noto_sans_url, noto_sans_path, "NotoSans"):
            try:
                pdfmetrics.registerFont(TTFont('NotoSans', noto_sans_path))
                ENGLISH_FONT = 'NotoSans'
                UNICODE_FONT = 'NotoSans'
                UNICODE_FONT_BOLD = 'NotoSans'
                english_registered = True
                print(f"✅ NotoSans (English) downloaded and registered")
            except Exception as e:
                print(f"⚠️ Failed to register downloaded NotoSans: {e}")
    
    # Register NotoSansDevanagari for Hindi text
    if os.path.exists(noto_devanagari_path):
        try:
            pdfmetrics.registerFont(TTFont('NotoDevanagari', noto_devanagari_path))
            HINDI_FONT = 'NotoDevanagari'
            hindi_registered = True
            print(f"✅ NotoSansDevanagari (Hindi) font registered")
        except Exception as e:
            print(f"⚠️ Failed to register NotoSansDevanagari: {e}")
    
    # Download NotoSansDevanagari if not exists
    if not hindi_registered:
        noto_deva_url = "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        if download_font(noto_deva_url, noto_devanagari_path, "NotoSansDevanagari"):
            try:
                pdfmetrics.registerFont(TTFont('NotoDevanagari', noto_devanagari_path))
                HINDI_FONT = 'NotoDevanagari'
                hindi_registered = True
                print(f"✅ NotoSansDevanagari (Hindi) downloaded and registered")
            except Exception as e:
                print(f"⚠️ Failed to register downloaded NotoSansDevanagari: {e}")
    
    # Fallback to Windows fonts if needed
    if not english_registered or not hindi_registered:
        nirmala_ttf = 'C:\\Windows\\Fonts\\Nirmala.ttf'
        if os.path.exists(nirmala_ttf):
            try:
                pdfmetrics.registerFont(TTFont('Nirmala', nirmala_ttf))
                if not english_registered:
                    ENGLISH_FONT = 'Nirmala'
                    UNICODE_FONT = 'Nirmala'
                    UNICODE_FONT_BOLD = 'Nirmala'
                if not hindi_registered:
                    HINDI_FONT = 'Nirmala'
                print("⚠️ Using Windows Nirmala font as fallback")
            except Exception as e:
                print(f"⚠️ Failed to register Nirmala: {e}")
    
    print(f"📝 Font setup complete:")
    print(f"   English font: {ENGLISH_FONT}")
    print(f"   Hindi font: {HINDI_FONT}")

except Exception as e:
    print(f"❌ Error during font registration: {e}")
    print("⚠️ Hindi text and rupee symbol may show as blocks")


def generate_order_pdf(order_data, filename="invoice.pdf"):
    """
    Generate a PDF invoice for an order.
    
    Args:
        order_data: Dictionary containing order information
        filename: Output PDF filename
    
    Returns:
        str: Path to generated PDF file
    """
    print(f"📄 generate_order_pdf called")
    print(f"   Filename: {filename}")
    print(f"   Order Data Type: {type(order_data)}")
    print(f"   Order Data Keys: {order_data.keys() if hasattr(order_data, 'keys') else 'Not a dict'}")
    
    try:
        # Define custom page template with header
        def add_page_header(canvas, doc):
            """Add header with logo to every page"""
            print(f"🎨 Order PDF: add_page_header called for page {doc.page}")
            canvas.saveState()
            
            # Logo paths
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(script_dir)
                project_dir = os.path.dirname(backend_dir)
                hotel_logo_path = os.path.join(project_dir, 'Sweet_store_frontend', 'public', 'hotel_logo2-removebg-preview.png')
                name_logo_path = os.path.join(project_dir, 'Sweet_store_frontend', 'public', 'Name.png')
                
                # Center position for logos
                page_width = letter[0]
                center_x = page_width / 2
                
                # Calculate total width of both logos to center them as a group
                total_logo_width = 3.5 * inch
                start_x = center_x - (total_logo_width / 2)
                
                # Draw hotel logo (left side)
                if os.path.exists(hotel_logo_path):
                    canvas.drawImage(
                        hotel_logo_path, 
                        start_x, 
                        letter[1] - 120, 
                        width=1.5*inch, 
                        height=1.5*inch, 
                        preserveAspectRatio=True, 
                        mask='auto'
                    )
                
                # Draw name logo (right side, immediately after hotel logo)
                if os.path.exists(name_logo_path):
                    canvas.drawImage(
                        name_logo_path, 
                        start_x + 1.5*inch, 
                        letter[1] - 100, 
                        width=2*inch, 
                        height=1*inch, 
                        preserveAspectRatio=True, 
                        mask='auto'
                    )
                
            except Exception as e:
                print(f"⚠️ Could not load logos in header: {e}")
                # Fallback to text header
                canvas.setFont('Helvetica-Bold', 16)
                canvas.setFillColor(colors.HexColor('#FFD700'))
                canvas.drawCentredString(page_width / 2, letter[1] - 70, "MANSOOR HOTEL N SWEETS")
            
            canvas.restoreState()
        
        # Create PDF document with custom page template
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter,
            leftMargin=50,
            rightMargin=50,
            topMargin=130,  # Increased to accommodate logo header
            bottomMargin=50
        )
        
        # Set up page template with header
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='header_template', frames=frame, onPage=add_page_header)
        doc.addPageTemplates([template])
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles with Unicode font support
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=ENGLISH_FONT,
            fontSize=24,
            textColor=colors.HexColor('#FFD700'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=ENGLISH_FONT,
            fontSize=14,
            textColor=colors.HexColor('#D2691E'),
            spaceAfter=12
        )
        
        # Cell style for mixed fonts
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName=ENGLISH_FONT,
            fontSize=10,
            leading=12
        )
        
        # Logos now in page header - will appear on every page
        # Subtitle (removed title)
        subtitle = Paragraph("Order Invoice", styles['Heading2'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        # Order Information
        # Get sequential order number from orderNumber field (set when order is created)
        order_number = order_data.get('orderNumber', None)
        if order_number:
            order_id = f"{order_number:04d}"  # Format as 0001, 0002, etc.
        else:
            # Fallback: use MongoDB ObjectId
            order_id = str(order_data.get('_id', 'N/A'))
        customer_name = order_data.get('customerName', 'N/A')
        mobile = order_data.get('mobile', 'N/A')
        address = order_data.get('address', 'N/A')
        
        # Format dates as dd-mm-yyyy
        order_date = order_data.get('orderDate', 'N/A')
        if order_date != 'N/A':
            try:
                from datetime import datetime
                date_obj = datetime.strptime(str(order_date).split('T')[0], '%Y-%m-%d')
                order_date = date_obj.strftime('%d-%m-%Y')
            except:
                pass
        
        delivery_date = order_data.get('deliveryDate', 'N/A')
        if delivery_date != 'N/A':
            try:
                from datetime import datetime
                date_obj = datetime.strptime(str(delivery_date).split('T')[0], '%Y-%m-%d')
                delivery_date = date_obj.strftime('%d-%m-%Y')
            except:
                pass
        
        # Order details table with Paragraphs for mixed font support
        order_info = [
            [Paragraph('Order ID:', cell_style), Paragraph(order_id, cell_style)],
            [Paragraph('Customer Name:', cell_style), Paragraph(format_mixed_text(customer_name, ENGLISH_FONT, HINDI_FONT), cell_style)],
            [Paragraph('Mobile:', cell_style), Paragraph(mobile, cell_style)],
            [Paragraph('Address:', cell_style), Paragraph(format_mixed_text(address, ENGLISH_FONT, HINDI_FONT), cell_style)],
            [Paragraph('Order Date:', cell_style), Paragraph(order_date, cell_style)],
            [Paragraph('Delivery Date:', cell_style), Paragraph(delivery_date, cell_style)]
        ]
        
        order_table = Table(order_info, colWidths=[2*inch, 4*inch])
        order_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#D2691E')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(order_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Items heading
        items_heading = Paragraph("Order Items", heading_style)
        elements.append(items_heading)
        elements.append(Spacer(1, 0.1*inch))
        
        # Items table with Paragraphs for mixed font support
        items = order_data.get('items', [])
        items_data = [[
            Paragraph('#', cell_style),
            Paragraph('Item Name', cell_style),
            Paragraph('Quantity', cell_style),
            Paragraph('Price', cell_style),
            Paragraph('Total', cell_style)
        ]]
        
        for idx, item in enumerate(items, 1):
            sweet_name = item.get('sweetName', 'N/A')
            quantity = item.get('quantity', 0)
            unit = item.get('unit', 'Kg')
            price = item.get('price', 0)
            total = price * quantity
            
            # Combine quantity and unit
            quantity_with_unit = f"{quantity} {unit}"
            
            items_data.append([
                Paragraph(str(idx), cell_style),
                Paragraph(format_mixed_text(sweet_name, ENGLISH_FONT, HINDI_FONT), cell_style),
                Paragraph(quantity_with_unit, cell_style),
                Paragraph(f"₹{price}", cell_style),
                Paragraph(f"₹{total:.2f}", cell_style)
            ])
        
        # Add total row
        total_amount = order_data.get('total', 0)
        items_data.append([
            Paragraph('', cell_style),
            Paragraph('', cell_style),
            Paragraph('', cell_style),
            Paragraph('Grand Total:', cell_style),
            Paragraph(f"₹{total_amount}", cell_style)
        ])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 1*inch, 1.3*inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFD700')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            
            # Total row
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFF8DC')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#D2691E')),
            
            # Grid
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = f"""
        <para align=center>
        <font size=10 color="#666666">
        Thank you for your order!<br/>
        We'll prepare your sweets with love ❤️<br/><br/>
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </font>
        </para>
        """
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF with logo on every page
        doc.build(elements, onFirstPage=add_page_header, onLaterPages=add_page_header)
        print(f"✅ PDF generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Failed to generate PDF: {str(e)}")
        return None


def generate_orders_statement_pdf(orders, filters, filename="statement.pdf"):
    """
    Generate a PDF statement for filtered orders with customer details and sweet sales summary.
    
    Args:
        orders: List of order dictionaries
        filters: Dictionary with filter information for the header
        filename: Output PDF filename
    
    Returns:
        bytes: PDF file bytes
    """
    print(f"📄 generate_orders_statement_pdf called")
    print(f"   Filename: {filename}")
    print(f"   Total Orders: {len(orders)}")
    
    try:
        from io import BytesIO
        
        # Create PDF document
        buffer = BytesIO()
        
        # Define custom page template with header
        def add_page_header(canvas, doc):
            """Add header with logo to every page"""
            print(f"🎨 Statement PDF: add_page_header called for page {doc.page}")
            canvas.saveState()
            
            # Logo paths
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(script_dir)
                project_dir = os.path.dirname(backend_dir)
                hotel_logo_path = os.path.join(project_dir, 'Sweet_store_frontend', 'public', 'hotel_logo2-removebg-preview.png')
                name_logo_path = os.path.join(project_dir, 'Sweet_store_frontend', 'public', 'Name.png')
                
                # Center position for logos
                page_width = A4[0]
                center_x = page_width / 2
                
                # Calculate total width of both logos to center them as a group
                total_logo_width = 3.5 * inch
                start_x = center_x - (total_logo_width / 2)
                
                # Draw hotel logo (left side)
                if os.path.exists(hotel_logo_path):
                    canvas.drawImage(
                        hotel_logo_path, 
                        start_x, 
                        A4[1] - 120, 
                        width=1.5*inch, 
                        height=1.5*inch, 
                        preserveAspectRatio=True, 
                        mask='auto'
                    )
                
                # Draw name logo (right side, immediately after hotel logo)
                if os.path.exists(name_logo_path):
                    canvas.drawImage(
                        name_logo_path, 
                        start_x + 1.5*inch, 
                        A4[1] - 100, 
                        width=2*inch, 
                        height=1*inch, 
                        preserveAspectRatio=True, 
                        mask='auto'
                    )
                
            except Exception as e:
                print(f"⚠️ Could not load logos in header: {e}")
                # Fallback to text header
                canvas.setFont('Helvetica-Bold', 16)
                canvas.setFillColor(colors.HexColor('#9333EA'))
                canvas.drawCentredString(page_width / 2, A4[1] - 70, "MANSOOR HOTEL N SWEETS")
            
            canvas.restoreState()
        
        # Create document with custom page template
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            leftMargin=50,
            rightMargin=50,
            topMargin=130,  # Increased to accommodate logo header
            bottomMargin=50
        )
        
        # Set up page template with header
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='header_template', frames=frame, onPage=add_page_header)
        doc.addPageTemplates([template])
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles with Unicode font support
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=ENGLISH_FONT,
            fontSize=22,
            textColor=colors.HexColor('#9333EA'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName=ENGLISH_FONT,
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName=ENGLISH_FONT,
            fontSize=14,
            textColor=colors.HexColor('#9333EA'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Sales Statement subtitle (logos now in page header)
        sales_statement = Paragraph("Sales Statement", subtitle_style)
        elements.append(sales_statement)
        
        # # Filter info subtitle
        # filter_parts = []
        # if filters.get('statusFilter'):
        #     filter_parts.append(f"Status: {filters['statusFilter']}")
        # if filters.get('dateFilter'):
        #     filter_parts.append(f"Order Date: {filters['dateFilter']}")
        # if filters.get('pendingPayment'):
        #     filter_parts.append("Delivered + Pending Payment")
        
        # filter_text = " | ".join(filter_parts) if filter_parts else "All Orders"
        # subtitle = Paragraph(f"Filters: {filter_text}", subtitle_style)
        # elements.append(subtitle)
        
        # Get date range from orders
        date_range_text = "All Orders"
        if orders:
            order_dates = []
            for order in orders:
                order_date = order.get('orderDate', '')
                if order_date:
                    try:
                        if 'T' in str(order_date):
                            order_date = order_date.split('T')[0]
                        date_obj = datetime.strptime(order_date, '%Y-%m-%d')
                        order_dates.append(date_obj)
                    except:
                        pass
            
            if order_dates:
                min_date = min(order_dates)
                max_date = max(order_dates)
                date_range_text = f"Date Range: {min_date.strftime('%d-%m-%Y')} to {max_date.strftime('%d-%m-%Y')}"
        
        date_range = Paragraph(date_range_text, subtitle_style)
        elements.append(date_range)
        elements.append(Spacer(1, 0.2*inch))
        
        # ===== SUMMARY SECTION =====
        total_orders = len(orders)
        total_amount = sum(order.get('total', 0) for order in orders)
        total_advance = sum(order.get('advancePaid', 0) for order in orders)
        total_due = total_amount - total_advance
        
        # Create paragraph style for table cells
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName=ENGLISH_FONT,
            fontSize=10,
            leading=12
        )
        
        cell_style_bold = ParagraphStyle(
            'CellStyleBold',
            parent=styles['Normal'],
            fontName=ENGLISH_FONT,
            fontSize=12,
            leading=14
        )
        
        # Wrap summary data in Paragraphs to ensure proper font usage
        summary_data = [
            [
                Paragraph('Total Orders', cell_style),
                Paragraph('Total Amount', cell_style),
                Paragraph('Advance Paid', cell_style),
                Paragraph('Amount Due', cell_style)
            ],
            [
                Paragraph(str(total_orders), cell_style_bold),
                Paragraph(f"₹{total_amount:,.2f}", cell_style_bold),
                Paragraph(f"₹{total_advance:,.2f}", cell_style_bold),
                Paragraph(f"₹{total_due:,.2f}", cell_style_bold)
            ]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch], repeatRows=1)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333EA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), ENGLISH_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 1), (-1, 1), ENGLISH_FONT),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F3E8FF')),
            ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#DC2626')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9333EA')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        # Keep summary table together on same page
        elements.append(KeepTogether([summary_table]))
        elements.append(Spacer(1, 0.3*inch))
        
        # ===== TOTAL SWEETS SOLD SECTION =====
        elements.append(Paragraph("📦 Total Sweets Sold", section_header_style))
        
        # Aggregate all sweets sold
        sweets_sold = {}
        for order in orders:
            items = order.get('items', [])
            for item in items:
                sweet_name = item.get('sweetName', 'Unknown')
                quantity = float(item.get('quantity', 0))
                unit = item.get('unit', 'Kg')
                price = float(item.get('price', 0))
                item_total = quantity * price
                
                key = f"{sweet_name}|{unit}"
                if key not in sweets_sold:
                    sweets_sold[key] = {
                        'name': sweet_name,
                        'quantity': 0,
                        'unit': unit,
                        'total': 0
                    }
                sweets_sold[key]['quantity'] += quantity
                sweets_sold[key]['total'] += item_total
        
        # Create sweets table with Paragraphs for mixed font support
        header_row = [
            Paragraph('#', cell_style),
            Paragraph('Sweet Name', cell_style),
            Paragraph('Quantity', cell_style),
            Paragraph('Total Amount', cell_style)
        ]
        sweets_data = [header_row]
        
        for idx, (key, sweet) in enumerate(sorted(sweets_sold.items(), key=lambda x: x[1]['total'], reverse=True), 1):
            sweet_name = sweet['name']
            print(f"   Sweet #{idx}: {sweet_name} (type: {type(sweet_name)}, repr: {repr(sweet_name)})")
            
            # Use mixed font formatting for sweet names (English + Hindi)
            mixed_name = format_mixed_text(sweet_name, ENGLISH_FONT, HINDI_FONT)
            
            # Combine quantity and unit in single column
            quantity_with_unit = f"{sweet['quantity']:.2f} {sweet['unit']}"
            
            sweets_data.append([
                Paragraph(str(idx), cell_style),
                Paragraph(mixed_name, cell_style),
                Paragraph(quantity_with_unit, cell_style),
                Paragraph(f"₹{sweet['total']:,.2f}", cell_style)
            ])
        
        # Add grand total row
        grand_total_qty = sum(s['quantity'] for s in sweets_sold.values())
        sweets_data.append([
            Paragraph('', cell_style_bold),
            Paragraph('GRAND TOTAL', cell_style_bold),
            Paragraph(f"{grand_total_qty:.2f}", cell_style_bold),
            Paragraph(f"₹{total_amount:,.2f}", cell_style_bold)
        ])
        
        # Sweets table with repeatRows to ensure header repeats on each page
        sweets_table = Table(sweets_data, repeatRows=1)
        sweets_table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EC4899')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            # Grand total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FDF2F8')),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#9333EA')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#EC4899')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # Alternating row colors
        for i in range(1, len(sweets_data) - 1):
            if i % 2 == 0:
                sweets_table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FDF2F8')))
        
        sweets_table.setStyle(TableStyle(sweets_table_style))
        elements.append(sweets_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ===== CUSTOMER DETAILS SECTION =====
        elements.append(Paragraph("👥 Customer Order Details", section_header_style))
        
        # Sort orders by orderDate in ascending order
        sorted_orders = sorted(orders, key=lambda x: x.get('orderDate', ''))
        
        # Customer orders table with Paragraph headers
        customer_data = [[
            Paragraph('#', cell_style),
            Paragraph('Customer Name', cell_style),
            Paragraph('Mobile', cell_style),
            Paragraph('Order Date', cell_style),
            Paragraph('Items', cell_style),
            Paragraph('Total', cell_style),
            Paragraph('Paid', cell_style),
            Paragraph('Due', cell_style)
        ]]
        
        for idx, order in enumerate(sorted_orders, 1):
            customer = order.get('customerName', 'N/A')
            mobile = order.get('mobile', 'N/A')
            order_date = order.get('orderDate', 'N/A')
            if order_date and 'T' in str(order_date):
                order_date = order_date.split('T')[0]
            # Convert date format from yyyy-mm-dd to dd-mm-yyyy
            if order_date != 'N/A':
                try:
                    date_obj = datetime.strptime(order_date, '%Y-%m-%d')
                    order_date = date_obj.strftime('%d-%m-%Y')
                except:
                    pass  # Keep original if conversion fails
            
            # Get items summary - format each item on a new line (show all items)
            items = order.get('items', [])
            items_list = []
            for item in items:  # Show all items
                sweet_name = item.get('sweetName', '')
                quantity = item.get('quantity', 0)
                unit = item.get('unit', 'Kg')
                # Apply mixed font to sweet name with quantity and unit
                mixed_name = format_mixed_text(f"{sweet_name} - {quantity} {unit}", ENGLISH_FONT, HINDI_FONT)
                items_list.append(mixed_name)
            
            items_summary = '<br/>'.join(items_list)
            
            total = order.get('total', 0)
            advance = order.get('advancePaid', 0)
            due = total - advance
            
            items_style = ParagraphStyle('ItemsList', fontName=ENGLISH_FONT, fontSize=7, leading=10)
            
            customer_data.append([
                Paragraph(str(idx), cell_style),
                Paragraph(format_mixed_text(customer[:20], ENGLISH_FONT, HINDI_FONT), cell_style),
                Paragraph(mobile, cell_style),
                Paragraph(order_date, cell_style),
                Paragraph(items_summary, items_style),
                Paragraph(f"₹{total:,.0f}", cell_style),
                Paragraph(f"₹{advance:,.0f}", cell_style),
                Paragraph(f"₹{due:,.0f}", cell_style)
            ])
        
        customer_table = Table(customer_data, colWidths=[0.35*inch, 1.0*inch, 1.1*inch, 0.9*inch, 2*inch, 0.8*inch, 0.8*inch, 0.8*inch], repeatRows=1)
        
        customer_table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333EA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (5, 1), (7, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9333EA')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (2, 1), (3, -1), 'OFF'),  # Prevent wrapping for mobile and order date
        ]
        
        # Alternating row colors and highlight due amounts
        for i in range(1, len(customer_data)):
            if i % 2 == 0:
                customer_table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9FAFB')))
            # Highlight due > 0 in red
            order = sorted_orders[i-1]
            due = order.get('total', 0) - order.get('advancePaid', 0)
            if due > 0:
                customer_table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.HexColor('#DC2626')))
        
        customer_table.setStyle(TableStyle(customer_table_style))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer with proper font for rupee symbol
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=ENGLISH_FONT,
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        footer_text = f"""
        Mansoor Hotel and Sweets - Sales Statement<br/>
        Total Orders: {total_orders} | Total Sweets: {len(sweets_sold)} types | Amount Due: ₹{total_due:,.2f}
        """
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
        
        # Build PDF with logo on every page
        doc.build(elements, onFirstPage=add_page_header, onLaterPages=add_page_header)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        print(f"✅ Statement PDF generated: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ Failed to generate statement PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_sales_report_pdf(date, sales_data, orders, filename="sales_report.pdf"):
    """
    Generate a PDF sales report matching the exact website display format with logo header on every page.
    """
    print(f"📊 generate_sales_report_pdf called")
    print(f"   Date: {date}")
    print(f"   Sales Data: {sales_data}")
    
    try:
        from io import BytesIO
        from reportlab.platypus import PageTemplate, Frame
        from reportlab.lib.utils import ImageReader
        import base64
        
        # Create PDF document with custom page template
        buffer = BytesIO()
        
        # Define custom page template with header
        def add_page_header(canvas, doc):
            """Add header with logo to every page - matching order PDF style"""
            canvas.saveState()
            
            # Logo paths - same as order PDF
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(script_dir)
                project_dir = os.path.dirname(backend_dir)
                hotel_logo_path = os.path.join(project_dir, 'Sweet_store_frontend', 'public', 'hotel_logo2-removebg-preview.png')
                name_logo_path = os.path.join(project_dir, 'Sweet_store_frontend', 'public', 'Name.png')
                
                # Center position for logos (like order PDF)
                page_width = A4[0]
                center_x = page_width / 2
                
                # Calculate total width of both logos to center them as a group
                # Hotel logo: 1.5 inches, Name logo: 2.0 inches, Total: 3.5 inches
                total_logo_width = 3.5 * inch
                start_x = center_x - (total_logo_width / 2)
                
                # Draw hotel logo (left side) - shifted down
                if os.path.exists(hotel_logo_path):
                    canvas.drawImage(
                        hotel_logo_path, 
                        start_x, 
                        A4[1] - 120, 
                        width=1.5*inch, 
                        height=1.5*inch, 
                        preserveAspectRatio=True, 
                        mask='auto'
                    )
                
                # Draw name logo (right side, immediately after hotel logo) - shifted down
                if os.path.exists(name_logo_path):
                    canvas.drawImage(
                        name_logo_path, 
                        start_x + 1.5*inch, 
                        A4[1] - 100, 
                        width=2*inch, 
                        height=1*inch, 
                        preserveAspectRatio=True, 
                        mask='auto'
                    )
                
            except Exception as e:
                print(f"⚠️ Could not load logos in header: {e}")
                # Fallback to text header
                canvas.setFont('Helvetica-Bold', 16)
                canvas.setFillColor(colors.HexColor('#8B5CF6'))
                canvas.drawCentredString(page_width / 2, A4[1] - 70, "MANSOOR HOTEL N SWEETS")
            
            canvas.restoreState()
        
        # Create document with custom page template
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            leftMargin=50, 
            rightMargin=50, 
            topMargin=120,  # Increased to accommodate logo header (1.5 inch logo height + spacing)
            bottomMargin=50
        )
        
        # Set up page template with header
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='header_template', frames=frame, onPage=add_page_header)
        doc.addPageTemplates([template])
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Use best available Unicode fonts
        try:
            # Try to use registered Unicode fonts first
            unicode_font = UNICODE_FONT if 'UNICODE_FONT' in globals() else 'DejaVu Sans'
            unicode_font_bold = UNICODE_FONT_BOLD if 'UNICODE_FONT_BOLD' in globals() else 'DejaVu Sans Bold'
        except:
            # Fallback to system fonts
            unicode_font = 'Helvetica'
            unicode_font_bold = 'Helvetica-Bold'
        
        # Custom styles for exact website matching
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=unicode_font_bold,
            fontSize=18,
            textColor=colors.HexColor('#8B5CF6'),  # Purple color
            spaceAfter=5,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName=unicode_font,
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontName=unicode_font_bold,
            fontSize=14,
            textColor=colors.HexColor('#8B5CF6'),
            spaceAfter=15,
            spaceBefore=20
        )
        
        # Title and Date (Company name now in header)
        title_style_report = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName=unicode_font_bold,
            fontSize=16,
            textColor=colors.HexColor('#8B5CF6'),
            spaceAfter=5,
            alignment=TA_CENTER,
            spaceBefore=0
        )
        
        elements.append(Paragraph("Daily Sales Report", title_style_report))
        elements.append(Paragraph(f"{date}", subtitle_style))
        
        # Handle empty or None sales_data
        if not sales_data:
            sales_data = {
                'total_amount': 0,
                'total_orders': 0,
                'total_sweets_sold': 0,
                'avg_order_value': 0,
                'sweets_breakdown': []
            }
        
        # Sales Summary Section - 4 Cards Layout
        elements.append(Paragraph("📊 Sales Summary", header_style))
        
        # Create 2x2 grid for summary cards (exactly like website)
        total_revenue = sales_data.get('total_amount', 0) or 0
        total_orders = sales_data.get('total_orders', 0) or 0
        items_sold = sales_data.get('total_sweets_sold', 0) or 0
        avg_order_value = sales_data.get('avg_order_value', 0) or 0
        
        summary_data = [
            [
                f"Total Amount\n₹{total_revenue:.2f}",
                f"Number of People\n{total_orders}"
            ],
            [
                f"Items Sold\n{items_sold}",
                f"Avg. Order Value\n₹{avg_order_value:.2f}"
            ]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.8*inch, 2.8*inch])
        summary_table.setStyle(TableStyle([
            # Card styling to match website
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#A855F7')),  # Purple card
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#3B82F6')),  # Blue card  
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#10B981')),  # Green card
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#F97316')),  # Orange card
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), unicode_font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Sweets Sold Breakdown Section (exactly like website)
        sweets_breakdown = sales_data.get('sweets_breakdown', [])
        if sweets_breakdown:
            elements.append(Paragraph("🍬 Sweets Sold Breakdown", header_style))
            
            # Create table with exact website columns
            breakdown_data = [['Sweet Name', 'Quantity', 'Rate', 'Total Amount']]
            
            for sweet in sweets_breakdown:
                sweet_name = sweet.get('name', 'Unknown')
                quantity = sweet.get('quantity', 0)
                rate = sweet.get('rate', 0)
                total = sweet.get('total', 0)
                unit = sweet.get('unit', 'Kg')
                
                breakdown_data.append([
                    sweet_name,  # Keep original name with Unicode characters
                    f"{quantity} {unit}",
                    f"₹{rate:.2f} / {unit}",
                    f"₹{total:.2f}"
                ])
            
            # Add Grand Total row (exactly like website)
            breakdown_data.append(['', '', 'Grand Total:', f"₹{total_revenue:.2f}"])
            
            # Create table with exact website styling
            breakdown_table = Table(breakdown_data, colWidths=[2.2*inch, 1.2*inch, 1.3*inch, 1.3*inch])
            breakdown_table.setStyle(TableStyle([
                # Header styling (gray BACKGROUND like website)
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D1D5DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Sweet Name left
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Quantity center
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),  # Rate center  
                ('ALIGN', (3, 0), (3, 0), 'RIGHT'),   # Total Amount right
                ('FONTNAME', (0, 0), (-1, 0), unicode_font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('ALIGN', (0, 1), (0, -2), 'LEFT'),    # Sweet names left
                ('ALIGN', (1, 1), (1, -2), 'CENTER'),  # Quantity center
                ('ALIGN', (2, 1), (2, -2), 'CENTER'),  # Rate center
                ('ALIGN', (3, 1), (3, -2), 'RIGHT'),   # Amount right
                ('FONTNAME', (0, 1), (-1, -2), unicode_font),
                ('FONTSIZE', (0, 1), (-1, -2), 10),
                
                # Alternating row colors like website
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9FAFB')]),
                
                # Grand Total row styling (gray BACKGROUND like website)
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F3F4F6')),
                ('FONTNAME', (0, -1), (-1, -1), unicode_font_bold),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('ALIGN', (2, -1), (2, -1), 'RIGHT'),  # "Grand Total:" right-aligned
                ('ALIGN', (3, -1), (3, -1), 'RIGHT'),  # Amount right-aligned
                ('TEXTCOLOR', (3, -1), (3, -1), colors.HexColor('#8B5CF6')),  # Purple color like website
                
                # Table borders
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#D1D5DB')),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(breakdown_table)
            elements.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%d/%m/%Y at %H:%M:%S')}"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=unicode_font,
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(elements)
        
        print(f"✅ Sales report PDF generated successfully")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"❌ Sales report PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
