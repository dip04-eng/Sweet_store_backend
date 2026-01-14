from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Test using TTC directly vs extracted TTF
test_text = 'Total Amount Due: ₹150.00'
hindi_text = 'जलेबी गुलाब जामुन'

print('Testing Nirmala TTC subfont 0 vs extracted HindiFont.ttf...\n')

# Test 1: Use TTC directly
try:
    pdfmetrics.registerFont(TTFont('NirmalaTTC', 'C:\\Windows\\Fonts\\Nirmala.ttc', subfontIndex=0))
    
    doc = SimpleDocTemplate('test_TTC_direct.pdf', pagesize=letter)
    elements = []
    
    data = [
        ['Test', 'Text'],
        ['English + Rupee', test_text],
        ['Hindi', hindi_text],
        ['Combined', f'{test_text} {hindi_text}']
    ]
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'NirmalaTTC'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    
    doc.build(elements)
    print('✅ test_TTC_direct.pdf created (using Nirmala.ttc subfont 0)')
except Exception as e:
    print(f'❌ TTC test failed: {e}')

# Test 2: Use extracted TTF
try:
    pdfmetrics.registerFont(TTFont('ExtractedTTF', 'HindiFont.ttf'))
    
    doc = SimpleDocTemplate('test_extracted_TTF.pdf', pagesize=letter)
    elements = []
    
    data = [
        ['Test', 'Text'],
        ['English + Rupee', test_text],
        ['Hindi', hindi_text],
        ['Combined', f'{test_text} {hindi_text}']
    ]
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'ExtractedTTF'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    
    doc.build(elements)
    print('✅ test_extracted_TTF.pdf created (using HindiFont.ttf)')
except Exception as e:
    print(f'❌ Extracted TTF test failed: {e}')

print('\n📝 Compare both PDFs:')
print('   - test_TTC_direct.pdf (should show ₹ and Hindi)')
print('   - test_extracted_TTF.pdf (might have missing glyphs)')
