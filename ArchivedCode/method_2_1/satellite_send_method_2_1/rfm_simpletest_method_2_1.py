# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell

import board
import busio
import digitalio
import time
import struct
import math
from adafruit_rfm import rfm9xfsk
from satellite_send_method_2_1 import DataToAX25_method_2_1
from satellite_send_method_2_1 import ListeningToolsSAT

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.GP8)
RESET = digitalio.DigitalInOut(board.GP9)

# Initialize SPI bus.
spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)

# Initialze RFM radio
# uncommnet the desired import and rfm initialization depending on the radio boards being used

# Use rfm9x for two RFM9x radios using LoRa

# from adafruit_rfm import rfm9x

# rfm = rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Use rfm9xfsk for two RFM9x radios or RFM9x to RFM69 using FSK



rfm = rfm9xfsk.RFM9xFSK(spi, CS, RESET, RADIO_FREQ_MHZ)

# Use rfm69 for two RFM69 radios using FSK

# from adafruit_rfm import rfm69

# rfm = rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)

# For RFM69 only: Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
# rfm.encryption_key = None
# rfm.encryption_key = (
#    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
# )

# for OOK on RFM69 or RFM9xFSK
# rfm.modulation_type = 1

# Send a packet.  Note you can only send a packet containing up to 60 bytes for an RFM69
# and 252 bytes for an RFM9x.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.

# This opens the image file and reads it into a list of bytes
jpg_file = open(r"blue.jpg", 'rb')
jpg_bytes = jpg_file.read()

# This is the callsign that is used as packet source and destination bytes
callsign = "K4KDJ"

# Sets up a counter and step variable to control what bytes are sent and how many are sent
# at a time
counter = 0
step = 32

# Calls a method to calculate the number of packets that will be sent & sends it
size = len(jpg_bytes)
numberOfPacketsFrame, numberOfPackets = ListeningToolsSAT.get_packet_number(size, step)
rfm.send(numberOfPacketsFrame)

# Creates a list containing every index and then
# calls a method to encode jpg_bytes into AX25 packets and send it
totalList = range(numberOfPackets)
ListeningToolsSAT.send_pic_data(jpg_bytes, rfm, step, totalList)

# This tells the ground station to send a list of corrupted/missing packets to be resent
while True:
    # Initializes a packet variable to store corrupted packet data
    # Initializes a counter variable to check infinite looping
    packet = None
    check = 0
    
    # Creates and encodes the send message into an AX25 frame and sends it
    sendMessage = bytes("Send the corrupted bytes.", "utf-8")
    initSendFrame = DataToAX25_method_2_1.encode_ax25_frame(sendMessage, callsign, callsign, b'\x03', 1)
    
    # Loop until the list of corrupted packet indices is received.
    while packet is None and check <= 5:
        rfm.send(initSendFrame)
        packet = rfm.receive(timeout=5.0)
        print("No corrupted packet list received. Listening again...")
        
        # Increments check
        check += 1
    
    # If check is over 5, meaning no packet has been received 5 times in a row,
    # loops are broken
    if check > 5:
        break
    
    # Decodes the received AX25 frame that contains the list of corrupted
    # packet indices
    operatingMode, fcsCorrect, data, packetIndex = DataToAX25_method_2_1.decode_ax25_frame(packet)
    
    # Checks the FCS value of the decoded packet. If False, something went wrong and the loop
    # is restarted
    if fcsCorrect is False:
        continue
    
    # If the number of corrupted packets is 0, meaning the groundstation
    # has all working packets, then the loop is terminated. 
    if len(data) == 0:
        break
    
    # Calls a method to get the list of corrupt packet indices
    corruptIndexList = ListeningToolsSAT.read_corrupt_indices(data)
    # Calls a function of the jpg_bytes with the list of corrupt indices
    ListeningToolsSAT.send_pic_data(jpg_bytes, rfm, step, corruptIndexList)
    
        
# Converts a message signifying that all bytes have been sent and encodes it into
# an AX25 frame
endMessage = bytes("All bytes sent.", "utf-8")
endFrame = DataToAX25_method_2_1.encode_ax25_frame(endMessage, callsign, callsign, b'\x04', 1)

# Sends the endFrame 4 times to ensure it is received
for i in range(4):
    rfm.send(endFrame)
    time.sleep(1.0)
    
print("End frame sent. Terminating messages.")
