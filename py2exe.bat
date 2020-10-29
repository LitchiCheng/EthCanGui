pyinstaller -D -w --hidden-import=PyQt5.sip EthCanGui.py
xcopy .\qss dist\EthCanGui\qss\ /E /Y
pause 