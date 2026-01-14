from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import os

test_text = 'Amount: ₹150 जलेबी'
fonts_to_test = [
    ('Mangal', 'C:\\Windows\\Fonts\\Mangal.ttf'),
    ('Kokila', 'C:\\Windows\\Fonts\\Kokila.ttf'),
    ('Utsaah', 'C:\\Windows\\Fonts\\Utsaah.ttf'),
    ('Aparajita', 'C:\\Windows\\Fonts\\Aparajita.ttf'),
    ('Sanskrit Text', 'C:\\Windows\\Fonts\\Sanskrit.ttf'),
]

print('Testing Windows Hindi fonts...\n')

for font_name, font_path in fonts_to_test:
    if not os.path.exists(font_path):
        print(f'⏭️  {font_name}: File not found - {font_path}')
        continue
        
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        
        # Try to create a PDF
        doc = SimpleDocTemplate(f'test_{font_name.replace(" ", "_")}.pdf', pagesize=letter)
        elements = []
        
        data = [['Font', 'Text'], [font_name, test_text]]
        table = Table(data)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        
        doc.build(elements)
        print(f'✅ {font_name}: PDF created - check test_{font_name.replace(" ", "_")}.pdf')
        
    except Exception as e:
        print(f'❌ {font_name}: ERROR - {str(e)[:100]}')

print('\n✅ Test complete! Check the generated PDFs.')
