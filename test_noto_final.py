from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Test NotoSans-Regular
pdfmetrics.registerFont(TTFont('NotoSans', 'NotoSans-Regular.ttf'))

test_text = 'Amount Due: ₹150.00 | जलेबी गुलाब जामुन'

doc = SimpleDocTemplate('test_noto_final.pdf', pagesize=letter)
elements = []

data = [
    ['Font Test', 'Result'],
    ['Noto Sans', test_text]
]
table = Table(data, colWidths=[150, 400])
table.setStyle(TableStyle([
    ('FONT', (0, 0), (-1, -1), 'NotoSans'),
    ('FONTSIZE', (0, 0), (-1, -1), 16),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('PADDING', (0, 0), (-1, -1), 10),
]))
elements.append(table)

doc.build(elements)
print('✅ test_noto_final.pdf created!')
print('📝 Check if this PDF shows ₹ and Hindi correctly.')
