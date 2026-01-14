from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

test_text = 'Test Hindi: जलेबी गुलाब जामुन'
print('Testing Nirmala TTC subfonts for Hindi support...\n')

for idx in range(8):
    try:
        font_name = f'NirmalaTest{idx}'
        pdfmetrics.registerFont(TTFont(font_name, 'C:\\Windows\\Fonts\\Nirmala.ttc', subfontIndex=idx))
        
        # Try to create a simple PDF with this font
        doc = SimpleDocTemplate(f'test_subfont_{idx}.pdf', pagesize=letter)
        elements = []
        
        # Create table with Hindi text
        data = [['Subfont', 'Text'], [str(idx), test_text]]
        table = Table(data)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        
        doc.build(elements)
        print(f'✅ Subfont {idx}: PDF created successfully - check test_subfont_{idx}.pdf')
        
    except Exception as e:
        print(f'❌ Subfont {idx}: ERROR - {str(e)[:80]}')

print('\n✅ Test complete! Check the generated PDFs to see which one displays Hindi correctly.')
