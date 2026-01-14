from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

test_text = 'Amount: ₹150.00 जलेबी'
print('Testing Nirmala TTC subfonts for Rupee symbol (₹) and Hindi...\n')

for idx in range(6):
    try:
        font_name = f'NirmalaTest{idx}'
        pdfmetrics.registerFont(TTFont(font_name, 'C:\\Windows\\Fonts\\Nirmala.ttc', subfontIndex=idx))
        
        doc = SimpleDocTemplate(f'test_rupee_{idx}.pdf', pagesize=letter)
        elements = []
        
        data = [
            ['Subfont', 'Text'],
            [str(idx), test_text]
        ]
        table = Table(data, colWidths=[80, 300])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        
        doc.build(elements)
        print(f'✅ Subfont {idx}: test_rupee_{idx}.pdf created')
        
    except Exception as e:
        print(f'❌ Subfont {idx}: {str(e)[:80]}')

print('\n✅ Check the PDFs to see which subfont shows ₹ correctly!')
