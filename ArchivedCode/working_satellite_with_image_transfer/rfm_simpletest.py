# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell

import board
import busio
import digitalio
import time
from adafruit_rfm import rfm9xfsk
import DataToAX25

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

# jpg_file = open(r"Camera Function Test.jpg",'rb')

# This opens the image file and reads it into a list of bytes
jpg_file = open(r"blue.jpg", 'rb')
jpg_bytes = jpg_file.read()
print(type(jpg_bytes))
print(len(jpg_bytes))

# Sets up a counter and step variable to control what bytes are sent and how many are sen't
# at a time
counter = 0
step = 32

# This is the callsign that is used as packet source and destination bytes
callsign = "K4KDJ"

# This loops through every [step] bytes in jpg_bytes and sends them to the ground station
while(counter < len(jpg_bytes)):
    # Encodes the bytes being send into AX25 packet form
    frame = DataToAX25.encode_ax25_frame(jpg_bytes[counter : counter + step], callsign, callsign, b'\x00')
    
    # Sends the packeted data and prints out the status of the overal sending to the terminal
    rfm.send(frame)
    print("sent: ",frame)
    print(counter, " bytes sent, ", len(jpg_bytes) - counter, " bytes left.")
    
    # Checks that the groundstation received the sent bytes. If the bytes were received the ground station
    # sends back a message to acknowledge that the bytes were received, then counter is increased to send
    # the next set of bytes
    packet = rfm.receive(timeout=0.5)
    if packet is not None:
        counter += step
    

# # Working image transfer commented out to test packet transfers
# while(counter < len(jpg_bytes)):
#     rfm.send(jpg_bytes[counter:counter+step])
#     print("sent: ",jpg_bytes[counter:counter+step])
#     print(counter, " bytes sent, ", len(jpg_bytes) - counter, " bytes left.")
#     packet = rfm.receive(timeout=0.5)
#     if packet is not None:
#         counter += step


# while(counter < len(jpg_bytes)):
#     rfm.send(counter.to_bytes(2,"big"))
#     print("sent",counter)
#     packet = rfm.receive(timeout=0.5)
#     if packet is not None:
#         counter += 1


# Original testing code commented out to test image byte sending     
# while(True):
#     rfm.send(bytes("Hello!\r\n", "utf-8"))
#     print("Sent Hello World message!")
#     time.sleep(1);

# Wait to receive packets.
# print("Waiting for packets...")

# while True:
#     # Optionally change the receive timeout from its default of 0.5 seconds:
#     # packet = rfm9x.receive(timeout=5.0)
#     packet = rfm.receive(timeout=5.0)
#     # If no packet was received during the timeout then None is returned.
#     if packet is None:
#         # Packet has not been received
#         rfm.send("not received")
#         print("Received nothing! Listening again...")
#     else:
#         # Received a packet!
#         # Print out the raw bytes of the packet:
#         rfm.send("received")
#         print(f"Received (raw bytes): {packet}")
#         # And decode to ASCII text and print it too.  Note that you always
#         # receive raw bytes and need to convert to a text format like ASCII
#         # if you intend to do string processing on your data.  Make sure the
#         # sending side is sending ASCII data before you try to decode!
#         try:
#             packet_text = str(packet, "ascii")
#             print(f"Received (ASCII): {packet_text}")
#         except UnicodeError:
#             print("Hex data: ", [hex(x) for x in packet])
#         # Also read the RSSI (signal strength) of the last received message and
#         # print it.
#         rssi = rfm.last_rssi
#         print(f"Received signal strength: {rssi} dB")
