#!/bin/bash

cd  ~
git clone https://github.com/pyinstaller/pyinstaller
cd pyinstaller/bootloader
python ./waf distclean all
cd ~
cd pyinstaller 
sudo python setup.py install
sudo pip install PyCrypto
cd  ~
mv helena/compiling . 
cd compiling
chmod +x pycompile.sh
sudo ./pycompile.sh ~/helena main.py
cd ~
cd helena/dist
cp main ../
cp key ../
cd ~

