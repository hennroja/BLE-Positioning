import os
import sys
import struct
import bluetooth._bluetooth as bluez
from time import sleep
import json
import requests
import datetime

LE_META_EVENT = 0x3e
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C

EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04


devid = 0
url = 'http://192.168.178.52:8080/PositioningServer/test'
adress = "AA:AA:AA:BB:BB:BB"
headers = {'content-type': 'application/json'}



def listen_le_scan(socket):
    enable = 0x01
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(socket, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def gethostaddr(socket):
    try:
        try:
            addr = bluez.getsockname(socket)
            print addr
        except IOError, e:
            print "oh no ... :( ... error"
    finally:
        socket.close()
    return addr

def parse_le_events(socket):

    old_filter = socket.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    nfilter = bluez.hci_filter_new()
    bluez.hci_filter_all_events(nfilter)
                                            # HCI_EVENT_PKT = 0x04
    bluez.hci_filter_set_ptype(nfilter, bluez.HCI_EVENT_PKT)
    
    # socket.setsockopt(level, optname, value)
    socket.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, nfilter)

    bluez.hci_send_cmd(socket, bluez.OGF_HOST_CTL, 
            bluez.OCF_READ_INQUIRY_MODE )

    #while(true):
    for i in range(0, 5000):
        pkt = socket.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])

        # BLE EVENTS
        if event == LE_META_EVENT:

            subevent, = struct.unpack("B", pkt[3])
            pkt = pkt[4:]
            if subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = struct.unpack("B", pkt[0])[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    report_event_type = struct.unpack("B", pkt[report_pkt_offset + 1])[0]
                    bdaddr_type = struct.unpack("B", pkt[report_pkt_offset + 2])[0]
                    report_data_length, = struct.unpack("B", pkt[report_pkt_offset + 9])
                    payload = "{"
                    payload += "\"addr\": \"%s\"" % packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                    report_pkt_offset = report_pkt_offset +  10 + report_data_length + 1
                    rssi, = struct.unpack("b", pkt[report_pkt_offset -1])
                   
                    payload += ", \"rssi\": %s " % rssi
                    payload += ", \"source\": \"%s\" " % adress
                    payload += ", \"captured\": \"%s\"" % datetime.datetime.now().isoformat()
                    payload += "}"
                    print payload
                    requests.post(url, data=payload, headers=headers)

                    #requests.post(url, data=json.dumps(payload), headers=headers)

        
        sleep(1.00) 
    socket.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )

try:
    socket = bluez.hci_open_dev(devid)
except:
    print "failed open ble socket..."
    sys.exit(1)

listen_le_scan(socket)
parse_le_events(socket)

try:
    bluez.hci_close_dev(devid)
    print "close hci connection..."
except:
    print "failed close ble socket..."
    sys.exit(1)
