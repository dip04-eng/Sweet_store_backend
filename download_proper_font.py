import urllib.request
import zipfile
import os
import shutil

print('Downloading Noto Sans font (includes Hindi + Rupee symbol)...\n')

# Download from a reliable mirror
url = 'https://fonts.google.com/download?family=Noto%20Sans'

try:
    # Try direct download
    print('Step 1: Downloading font package...')
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=30) as response:
        with open('NotoSans.zip', 'wb') as f:
            f.write(response.read())
    
    print('✅ Downloaded!\n')
    
    print('Step 2: Extracting Regular font...')
    with zipfile.ZipFile('NotoSans.zip', 'r') as zip_ref:
        # List all files
        files = zip_ref.namelist()
        print(f'Found {len(files)} files in archive')
        
        # Find and extract Regular font
        for file in files:
            if 'Regular' in file and file.endswith('.ttf'):
                zip_ref.extract(file)
                print(f'✅ Extracted: {file}')
                
                # Move to root with simple name
                if os.path.exists(file):
                    shutil.move(file, 'NotoSans-Regular.ttf')
                    print('✅ Renamed to: NotoSans-Regular.ttf')
                    break
    
    # Cleanup
    os.remove('NotoSans.zip')
    print('\n✅ SUCCESS! Font ready: NotoSans-Regular.ttf')
    
except Exception as e:
    print(f'\n❌ Download failed: {e}')
    print('\nTrying alternative method...')
    
    # Alternative: Use requests to download from CDN
    try:
        import requests
        
        # Try Google Fonts API to get font files
        api_url = 'https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400'
        response = requests.get(api_url)
        
        # Parse CSS to find TTF URL
        import re
        ttf_urls = re.findall(r'url\((https://[^)]+\.(?:ttf|woff2))\)', response.text)
        
        if ttf_urls:
            print(f'Found font URL: {ttf_urls[0]}')
            font_response = requests.get(ttf_urls[0])
            
            with open('NotoSans-Regular.ttf', 'wb') as f:
                f.write(font_response.content)
            
            print('✅ SUCCESS! Font downloaded: NotoSans-Regular.ttf')
        else:
            print('❌ Could not find font URL')
            
    except Exception as e2:
        print(f'❌ Alternative also failed: {e2}')
        print('\n⚠️  MANUAL ACTION REQUIRED:')
        print('   Please download Noto Sans manually from:')
        print('   https://fonts.google.com/noto/specimen/Noto+Sans')
        print('   Save NotoSans-Regular.ttf to this directory')
