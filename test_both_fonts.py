from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Test both fonts
fonts_to_test = [
    ('DejaVuSans.ttf', 'DejaVu'),
    ('NotoSans-Regular.ttf', 'Noto'),
]

test_data = [
    'Amount Due: ₹150.00',
    'जलेबी (Jalebi)',
    'गुलाब जामुन',
    'Total: ₹250.00'
]

for font_file, font_name in fonts_to_test:
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_file))
        
        doc = SimpleDocTemplate(f'test_{font_name}_final.pdf', pagesize=letter)
        elements = []
        
        data = [[f'{font_name} Font Test', 'Result']]
        for text in test_data:
            data.append([font_name, text])
        
        table = Table(data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ]))
        elements.append(table)
        
        doc.build(elements)
        print(f'✅ test_{font_name}_final.pdf created')
        
    except Exception as e:
        print(f'❌ {font_name}: {e}')

print('\n📝 Check both PDFs to see which one renders ₹ correctly!')
