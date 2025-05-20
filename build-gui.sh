export FILENAME=Sap
export COMPANY_NAME=Yuki_Sakura
export PRODUCT_NAME=Sky-auto-player
export FILE_VERSION=1.0.0

nuitka --standalone \
--output-filename="$FILENAME" \
--output-dir=dist \
--company-name="$COMPANY_NAME" \
--product-name="$PRODUCT_NAME" \
--file-version="$FILE_VERSION" \
--assume-yes-for-downloads \
--follow-imports \
--include-package=sakura \
--include-data-dir=resources=resources \
--include-data-file=config.yaml=config.yaml \
--enable-plugin=pyside6 \
./gui.py
