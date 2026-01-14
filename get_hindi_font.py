import os
import requests

print('Downloading Noto Sans Devanagari from Google Fonts API...')

# Try to get the TTF directly from a working source
urls = [
    'https://fonts.gstatic.com/s/notosansdevanagari/v31/TuGoUUFzXI5FBtUq5a8bjKYTZjtRU6Sgv3NaV_SNmI0b8QQCQmHn6B2OHjbL_08AlXQky-AzoFoW4Ow.ttf',
    'https://raw.githubusercontent.com/rsms/inter/master/fonts/static/Inter-Regular.ttf',
]

for i, url in enumerate(urls):
    try:
        print(f'\nTrying source {i+1}...')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            filename = 'HindiFont.ttf'
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f'✅ Font downloaded successfully: {filename}')
            print(f'   Size: {len(response.content)} bytes')
            
            # Test if it's a valid TTF
            try:
                from fontTools.ttLib import TTFont
                font = TTFont(filename)
                print(f'   Font family: {font["name"].getBestFamilyName()}')
                print('✅ Font is valid!')
                break
            except Exception as e:
                print(f'⚠️  Font validation error: {e}')
                
        else:
            print(f'   Status: {response.status_code}')
            
    except Exception as e:
        print(f'   Error: {str(e)[:100]}')

print('\n' + ('='*50))

# If that didn't work, let's extract from Nirmala.ttc  
if not os.path.exists('HindiFont.ttf'):
    print('Trying to extract Regular font from Nirmala.ttc...')
    try:
        from fontTools.ttLib import TTCollection, TTFont
        
        ttc = TTCollection('C:\\Windows\\Fonts\\Nirmala.ttc')
        print(f'Found {len(ttc.fonts)} fonts in Nirmala.ttc')
        
        # Try each font
        for i, font in enumerate(ttc.fonts):
            name = font['name'].getBestFamilyName()
            print(f'  Font {i}: {name}')
            
            # Look for Nirmala UI (usually has better Unicode coverage)
            if 'Nirmala UI' in name:
                print(f'  ✅ Extracting {name}...')
                font.save('HindiFont.ttf')
                print(f'✅ Saved as HindiFont.ttf')
                break
                
    except Exception as e:
        print(f'❌ Error: {e}')

if os.path.exists('HindiFont.ttf'):
    print('\n✅ FINAL: HindiFont.ttf is ready!')
else:
    print('\n❌ FAILED: Could not get a Hindi font')
