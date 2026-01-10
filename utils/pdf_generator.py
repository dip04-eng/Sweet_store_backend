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
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#9333EA'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#9333EA'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Title
        title = Paragraph("🍬 SWEET STORE - Sales Statement", title_style)
        elements.append(title)
        
        # Filter info subtitle
        filter_parts = []
        if filters.get('statusFilter'):
            filter_parts.append(f"Status: {filters['statusFilter']}")
        if filters.get('dateFilter'):
            filter_parts.append(f"Order Date: {filters['dateFilter']}")
        if filters.get('pendingPayment'):
            filter_parts.append("Delivered + Pending Payment")
        
        filter_text = " | ".join(filter_parts) if filter_parts else "All Orders"
        subtitle = Paragraph(f"Filters: {filter_text}", subtitle_style)
        elements.append(subtitle)
        
        generated_time = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style)
        elements.append(generated_time)
        elements.append(Spacer(1, 0.2*inch))
        
        # ===== SUMMARY SECTION =====
        total_orders = len(orders)
        total_amount = sum(order.get('total', 0) for order in orders)
        total_advance = sum(order.get('advancePaid', 0) for order in orders)
        total_due = total_amount - total_advance
        
        summary_data = [
            ['Total Orders', 'Total Amount', 'Advance Paid', 'Amount Due'],
            [str(total_orders), f"₹{total_amount:,.2f}", f"₹{total_advance:,.2f}", f"₹{total_due:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333EA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F3E8FF')),
            ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#DC2626')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9333EA')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(summary_table)
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
                unit = item.get('unit', 'kg')
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
        
        # Create sweets table
        sweets_data = [['#', 'Sweet Name', 'Quantity', 'Unit', 'Total Amount']]
        for idx, (key, sweet) in enumerate(sorted(sweets_sold.items(), key=lambda x: x[1]['total'], reverse=True), 1):
            sweets_data.append([
                str(idx),
                sweet['name'],
                f"{sweet['quantity']:.2f}",
                sweet['unit'],
                f"₹{sweet['total']:,.2f}"
            ])
        
        # Add grand total row
        grand_total_qty = sum(s['quantity'] for s in sweets_sold.values())
        sweets_data.append(['', 'GRAND TOTAL', f"{grand_total_qty:.2f}", '', f"₹{total_amount:,.2f}"])
        
        sweets_table = Table(sweets_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 0.8*inch, 1.5*inch])
        sweets_table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EC4899')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            # Grand total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FDF2F8')),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
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
        
        # Customer orders table
        customer_data = [['#', 'Customer Name', 'Mobile', 'Order Date', 'Items', 'Total', 'Paid', 'Due']]
        
        for idx, order in enumerate(orders, 1):
            customer = order.get('customerName', 'N/A')
            mobile = order.get('mobile', 'N/A')
            order_date = order.get('orderDate', 'N/A')
            if order_date and 'T' in str(order_date):
                order_date = order_date.split('T')[0]
            
            # Get items summary
            items = order.get('items', [])
            items_summary = ', '.join([f"{item.get('sweetName', '')}({item.get('quantity', 0)})" for item in items[:2]])
            if len(items) > 2:
                items_summary += f" +{len(items)-2} more"
            
            total = order.get('total', 0)
            advance = order.get('advancePaid', 0)
            due = total - advance
            
            customer_data.append([
                str(idx),
                customer[:20],
                mobile,
                order_date,
                items_summary[:30],
                f"₹{total:,.0f}",
                f"₹{advance:,.0f}",
                f"₹{due:,.0f}"
            ])
        
        customer_table = Table(customer_data, colWidths=[0.35*inch, 1.2*inch, 0.9*inch, 0.75*inch, 1.5*inch, 0.65*inch, 0.55*inch, 0.55*inch])
        
        customer_table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333EA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (5, 1), (7, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9333EA')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Alternating row colors and highlight due amounts
        for i in range(1, len(customer_data)):
            if i % 2 == 0:
                customer_table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9FAFB')))
            # Highlight due > 0 in red
            order = orders[i-1]
            due = order.get('total', 0) - order.get('advancePaid', 0)
            if due > 0:
                customer_table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.HexColor('#DC2626')))
                customer_table_style.append(('FONT', (7, i), (7, i), 'Helvetica-Bold'))
        
        customer_table.setStyle(TableStyle(customer_table_style))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = f"""
        <para align=center>
        <font size=9 color="#666666">
        Sweet Store Sales Statement<br/>
        Total Orders: {total_orders} | Total Sweets: {len(sweets_sold)} types | Amount Due: ₹{total_due:,.2f}
        </font>
        </para>
        """
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
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
