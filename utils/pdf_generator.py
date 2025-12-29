from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os

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
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#FFD700'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#D2691E'),
            spaceAfter=12
        )
        
        # Title
        title = Paragraph("🍬 SWEET STORE", title_style)
        elements.append(title)
        
        subtitle = Paragraph("Order Invoice", styles['Heading2'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        # Order Information
        order_id = str(order_data.get('_id', 'N/A'))
        customer_name = order_data.get('customerName', 'N/A')
        mobile = order_data.get('mobile', 'N/A')
        address = order_data.get('address', 'N/A')
        order_date = order_data.get('orderDate', 'N/A')
        delivery_date = order_data.get('deliveryDate', 'N/A')
        
        # Order details table
        order_info = [
            ['Order ID:', order_id],
            ['Customer Name:', customer_name],
            ['Mobile:', mobile],
            ['Address:', address],
            ['Order Date:', order_date],
            ['Delivery Date:', delivery_date]
        ]
        
        order_table = Table(order_info, colWidths=[2*inch, 4*inch])
        order_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (-1, -1), 'Helvetica'),
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
        
        # Items table
        items = order_data.get('items', [])
        items_data = [['#', 'Item Name', 'Quantity', 'Unit', 'Price', 'Total']]
        
        for idx, item in enumerate(items, 1):
            sweet_name = item.get('sweetName', 'N/A')
            quantity = item.get('quantity', 0)
            unit = item.get('unit', 'kg')
            price = item.get('price', 0)
            total = price * quantity
            
            items_data.append([
                str(idx),
                sweet_name,
                f"{quantity}",
                unit,
                f"₹{price}",
                f"₹{total:.2f}"
            ])
        
        # Add total row
        total_amount = order_data.get('total', 0)
        items_data.append(['', '', '', '', 'Grand Total:', f"₹{total_amount}"])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 2*inch, 1*inch, 0.8*inch, 1*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFD700')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONT', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            
            # Total row
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
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
        
        # Build PDF
        doc.build(elements)
        print(f"✅ PDF generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Failed to generate PDF: {str(e)}")
        return None
