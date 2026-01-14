import urllib.request

# Noto Sans supports Hindi and Rupee symbol
url = 'https://noto-website-2.storage.googleapis.com/pkgs/NotoSans-unhinted.zip'

print('Downloading Noto Sans font...')
urllib.request.urlretrieve(url, 'NotoSans.zip')
print('✅ Downloaded! Extracting...')

import zipfile
with zipfile.ZipFile('NotoSans.zip', 'r') as zip_ref:
    # Extract only the Regular TTF
    for file in zip_ref.namelist():
        if 'Regular.ttf' in file and 'Noto' in file:
            zip_ref.extract(file)
            print(f'✅ Extracted: {file}')
            
            # Rename to simple name
            import os
            import shutil
            if os.path.exists(file):
                shutil.move(file, 'NotoSans.ttf')
                print('✅ Font ready: NotoSans.ttf')
                break

print('✅ Complete!')
