import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=DataWatch',
    '--distpath=dist',
    '--workpath=tmp',
])