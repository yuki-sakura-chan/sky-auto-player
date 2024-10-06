nuitka --standalone ^
--follow-imports ^
--include-package=sakura ^
--include-data-dir=resources=resources ^
--include-data-file=config.yaml=config.yaml ^
--windows-icon-from-ico=resources/static/icon/logo-64x64.ico ^
--windows-console-mode=disable ^
--enable-plugin=pyside6 ^
--mingw64 .\gui.py