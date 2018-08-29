# -*- mode: python -*-

block_cipher = None


a = Analysis(['autoCalibration.py'],
             pathex=[r'C:\Mio\VolteraSW\camera'],
             binaries=[],
             datas=[('C:\\Mio\\VolteraSW\\camera\\favicon.ico', '.'),
                    ('C:\\Mio\\VolteraSW\\camera\\reference.png', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Camera Calibration',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon=r'C:\Mio\VolteraSW\camera\favicon.ico')
