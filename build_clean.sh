#!/bin/bash
source /home/shiro/esp-idf-v5.5.2/export.sh
rm -rf sdkconfig sdkconfig.old dependencies.lock build build_esp32s3 managed_components
export IDF_TARGET=esp32s3
idf.py set-target esp32s3
echo 'Target set. Deleting lock file to force regeneration for esp32s3'
rm -f dependencies.lock
idf.py build
