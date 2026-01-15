from fontTools.ttLib import TTFont

# Check what's in NotoSans-Regular.ttf
try:
    font = TTFont('NotoSans-Regular.ttf')
    cmap = font.getBestCmap()
    
    rupee_unicode = 0x20B9  # ₹
    hindi_ja = 0x091C  # ज
    
    print('Checking NotoSans-Regular.ttf:')
    print(f'  Rupee symbol (₹): {"✅ YES" if rupee_unicode in cmap else "❌ NO"}')
    print(f'  Hindi (ज):        {"✅ YES" if hindi_ja in cmap else "❌ NO"}')
    
    if rupee_unicode not in cmap:
        print('\n⚠️  NotoSans-Regular does NOT have rupee symbol!')
        print('   Need to download Noto Sans Devanagari instead')
    
except Exception as e:
    print(f'Error: {e}')
