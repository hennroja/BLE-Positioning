#!/bin/bash

if [ "$(id -u)" != "0" ]; then
        echo "Sorry, but you have to be root."
        exit 1
fi
apt-get update
apt-get upgrade
apt-get install libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libread$
echo "Creating bluez_temp folder"
cd ~/
mkdir bluez_temp
cd bluez_temp
echo "Download: bluez-5.17"
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.17.tar.xz
echo "Download: dbus-1.8.0"
wget http://dbus.freedesktop.org/releases/dbus/dbus-1.8.0.tar.gz
echo "uncompressing"
tar --xz -xvf bluez-5.17.tar.xz 
tar xzf dbus-1.8.0.tar.gz
cd dbus-1.8.0
echo "install dbus-1.8.0"
./configure
make
make install
cd ../bluez-5.17
echo "install dbus-1.8.0"
./configure --disable-systemd --enable-library --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental
make
make install
cd ..
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py
pip install pybluez
