modprobe -v btusb
echo "0b05 17cb" >> /sys/bus/usb/drivers/btusb/new_id

