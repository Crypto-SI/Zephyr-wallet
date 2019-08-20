# -*- mode: python -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules


for i, x in enumerate(sys.argv):
    if x == '--name':
        cmdline_name = sys.argv[i+1]
        break
else:
    raise Exception('no name')

hiddenimports = collect_submodules('trezorlib')
hiddenimports += collect_submodules('safetlib')
hiddenimports += collect_submodules('btchip')
hiddenimports += collect_submodules('keepkeylib')
hiddenimports += collect_submodules('websocket')

# safetlib imports PyQt5.Qt.  We use a local updated copy of pinmatrix.py until they
# release a new version that includes https://github.com/archos-safe-t/python-safet/commit/b1eab3dba4c04fdfc1fcf17b66662c28c5f2380e
hiddenimports.remove('safetlib.qt.pinmatrix')

hiddenimports += [
    'zephyr',
    'zephyr_code.base_crash_reporter',
    'zephyr_code.base_wizard',
    'zephyr_code.plot',
    'zephyr_code.qrscanner',
    'zephyr_code.websockets',
    'zephyr_code.gui.qt',
    'PyQt5.sip',
    'PyQt5.QtPrintSupport',  # needed by Revealer

    'zephyr_code.plugins',

    'zephyr_code.plugins.hw_wallet.qt',

    'zephyr_code.plugins.audio_modem.qt',
    'zephyr_code.plugins.cosigner_pool.qt',
    'zephyr_code.plugins.digitalbitbox.qt',
    'zephyr_code.plugins.email_requests.qt',
    'zephyr_code.plugins.keepkey.qt',
    'zephyr_code.plugins.revealer.qt',
    'zephyr_code.plugins.labels.qt',
    'zephyr_code.plugins.trezor.qt',
    'zephyr_code.plugins.hideez.client',
    'zephyr_code.plugins.hideez.qt',
    'zephyr_code.plugins.safe_t.client',
    'zephyr_code.plugins.safe_t.qt',
    'zephyr_code.plugins.ledger.qt',
    'zephyr_code.plugins.virtualkeyboard.qt',

    'quark_hash'
]

datas = [
    ('zephyr_code/*.json', 'zephyr_code/'),
    ('zephyr_code/wordlist', 'zephyr_code/wordlist'),
    ('zephyr_code/gui/icons', 'zephyr_code/gui/icons'),
    ('C:\\zbarw', '.'),
]

datas += collect_data_files('trezorlib')
datas += collect_data_files('hideezlib')
datas += collect_data_files('safetlib')
datas += collect_data_files('btchip')
datas += collect_data_files('keepkeylib')

# Add libusb so Trezor and Safe-T mini will work
binaries = [('C:/Python36/libusb-1.0.dll', '.')]

# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-remove-tkinter-tcl
sys.modules['FixTk'] = None
excludes = ['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter']
excludes += [
    'PyQt5.QtBluetooth',
    'PyQt5.QtCLucene',
    'PyQt5.QtDBus',
    'PyQt5.Qt5CLucene',
    'PyQt5.QtDesigner',
    'PyQt5.QtDesignerComponents',
    'PyQt5.QtHelp',
    'PyQt5.QtLocation',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaQuick_p',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtNetworkAuth',
    'PyQt5.QtNfc',
    'PyQt5.QtOpenGL',
    'PyQt5.QtPositioning',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickParticles',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtSql',
    'PyQt5.Qt5Sql',
    'PyQt5.Qt5Svg',
    'PyQt5.QtTest',
    'PyQt5.QtWebChannel',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebKit',
    'PyQt5.QtWebKitWidgets',
    'PyQt5.QtWebSockets',
    'PyQt5.QtXml',
    'PyQt5.QtXmlPatterns',
    'PyQt5.QtWebProcess',
    'PyQt5.QtWinExtras',
]

a = Analysis(['zephyr'],
             hiddenimports=hiddenimports,
             datas=datas,
             binaries=binaries,
             excludes=excludes,
             runtime_hooks=['pyi_runtimehook.py'])

# http://stackoverflow.com/questions/19055089/
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='zephyr_code/gui/icons/zephyr.ico',
          name=os.path.join('build\\pyi.win32\\electrum', cmdline_name))

# exe with console output
conexe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          debug=False,
          strip=False,
          upx=False,
          console=True,
          icon='zephyr_code/gui/icons/zephyr.ico',
          name=os.path.join('build\\pyi.win32\\electrum',
                            'console-%s' % cmdline_name))

# trezorctl separate executable
tctl_a = Analysis(['C:/Python36/Scripts/trezorctl'],
                  hiddenimports=[
                    'pkgutil',
                    'win32api',
                  ],
                  excludes=excludes,
                  runtime_hooks=['pyi_tctl_runtimehook.py'])

tctl_pyz = PYZ(tctl_a.pure)

tctl_exe = EXE(tctl_pyz,
           tctl_a.scripts,
           exclude_binaries=True,
           debug=False,
           strip=False,
           upx=False,
           console=True,
           name=os.path.join('build\\pyi.win32\\electrum', 'trezorctl.exe'))

coll = COLLECT(exe, conexe, #tctl_exe,
               a.binaries,
               a.datas,
               strip=False,
               upx=False,
               name=os.path.join('dist', 'zephyr'))
