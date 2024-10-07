@echo off
set FILENAME=Sap
set COMPANY_NAME=Yuki_Sakura
set PRODUCT_NAME=Sky-auto-player
set FILE_VERSION=1.0.0

nuitka --standalone --output-filename=%FILENAME% --output-dir=dist --company-name=%COMPANY_NAME% --product-name=%PRODUCT_NAME% --file-version=%FILE_VERSION% --assume-yes-for-downloads --follow-imports --include-package=sakura --include-data-dir=resources=resources --include-data-file=config.yaml=config.yaml --windows-icon-from-ico=resources/static/icon/logo-64x64.ico --windows-console-mode=disable --enable-plugin=pyside6 --mingw64 .\gui.py