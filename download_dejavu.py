import requests

print('Downloading DejaVu Sans (known to work with reportlab)...\n')

url = 'https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip'

try:
    response = requests.get(url, timeout=60)
    
    if response.status_code == 200:
        with open('dejavu.zip', 'wb') as f:
            f.write(response.content)
        print('✅ Downloaded!')
        
        import zipfile
        with zipfile.ZipFile('dejavu.zip', 'r') as zip_ref:
            # Extract DejaVuSans.ttf
            for file in zip_ref.namelist():
                if file.endswith('DejaVuSans.ttf'):
                    zip_ref.extract(file)
                    print(f'✅ Extracted: {file}')
                    
                    # Move to root
                    import os, shutil
                    if '/' in file:
                        shutil.move(file, 'DejaVuSans.ttf')
                        # Cleanup extracted folder
                        folder = file.split('/')[0]
                        if os.path.exists(folder):
                            shutil.rmtree(folder)
                    print('✅ Ready: DejaVuSans.ttf')
                    break
        
        os.remove('dejavu.zip')
        print('✅ Complete!')
        
    else:
        print(f'❌ Download failed: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')
