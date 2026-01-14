from fontTools.ttLib import TTCollection
import os

ttc_path = 'C:\\Windows\\Fonts\\Nirmala.ttc'
rupee_unicode = 0x20B9  # ₹ symbol

print('Checking which Nirmala subfont contains Rupee symbol (₹)...\n')

ttc = TTCollection(ttc_path)

for idx, font in enumerate(ttc.fonts):
    try:
        font_name = font['name'].getBestFamilyName()
        
        # Check if font has a cmap table
        if 'cmap' in font:
            # Get all Unicode characters supported by this font
            cmap = font.getBestCmap()
            if cmap:
                has_rupee = rupee_unicode in cmap
                has_hindi = 0x091C in cmap  # ज (Devanagari letter ja)
                
                print(f'Subfont {idx}: {font_name}')
                print(f'  Rupee symbol (₹): {"✅ YES" if has_rupee else "❌ NO"}')
                print(f'  Hindi support:     {"✅ YES" if has_hindi else "❌ NO"}')
                
                if has_rupee and has_hindi:
                    print(f'  🎯 THIS IS THE CORRECT SUBFONT! Use index {idx}')
                print()
                
    except Exception as e:
        print(f'Subfont {idx}: Error - {e}\n')

print('='*60)
print('Recommendation: Use the subfont that has BOTH ✅ symbols')
