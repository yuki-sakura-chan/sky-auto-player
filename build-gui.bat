@echo off
set FILENAME=Sap
set COMPANY_NAME=Yuki_Sakura
set PRODUCT_NAME=Sky-auto-player
set FILE_VERSION=1.0.0

nuitka ^
--standalone ^
--output-dir=dist ^
--output-filename=%FILENAME% ^
--company-name=%COMPANY_NAME% ^
--product-name=%PRODUCT_NAME% ^
--file-version=%FILE_VERSION% ^
--include-package=sakura ^
--assume-yes-for-downloads ^
--include-data-dir=resources=resources ^
--windows-icon-from-ico=resources/static/icon/logo-64x64.ico ^
--windows-console-mode=disable ^
--enable-plugin=pyside6 ^
--include-qt-plugins=sensible ^
--msvc=latest ^
.\gui.py