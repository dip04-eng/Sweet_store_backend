import requests

# Use a reliable CDN
url = 'https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-devanagari@5.0.17/files/noto-sans-devanagari-devanagari-400-normal.woff2'
response = requests.get(url, timeout=30)

if response.status_code == 200:
    with open('HindiFont.woff2', 'wb') as f:
        f.write(response.content)
    print('✅ Font downloaded successfully!')
    print('Note: This is a WOFF2 file. Converting to TTF...')
    
    # Try fonttools if available
    try:
        from fontTools.ttLib import TTFont as FTTTFont
        font = FTTTFont('HindiFont.woff2')
        font.save('HindiFont.ttf')
        print('✅ Converted to TTF!')
    except ImportError:
        print('⚠️  fonttools not installed. Install with: pip install fonttools brotli')
else:
    print(f'❌ Download failed: {response.status_code}')
