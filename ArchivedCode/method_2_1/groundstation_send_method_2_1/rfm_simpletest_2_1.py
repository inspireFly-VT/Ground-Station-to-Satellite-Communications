# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell


import board
import busio
import digitalio
from adafruit_rfm import rfm9xfsk
from groundstation_send_method_2_1 import ListeningTools
from groundstation_send_method_2_1 import DataToAX25_2_1


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
# rfm.modulation_type = 1
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
# and 252 bytes forn  an RFM9x.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.

#message = "Hello world!\r\n"

# while (True):
    # rfm.send(bytes("Hello world\r\n", "utf-8"))
    # print("Sent: Hello World message!") 
    # time.sleep(1)
    
    
# Creates a default, empty list 500 entries long that picture data will be stored in
# packetList should be updated later to match the expected number of picture data packets
packetList = []
for i in range(500):
    packetList.append(None)
    
# Creates a boolean value to check if the terminating command has been sent
# Also a counter for checking the number of times no packet is received
continueListening = True
check = 0
    
# Prints out that listening for packets is starting
print("Listening for packets...")

# Loops to listen for packets. If the terminating command is sent, continueListening becomes false
# and looping ends
# If check is over 5, meaning no packets were received five times in a row, then looping ends
while continueListening and check < 5:
    # Constant listening for a packet being sent from the satellite
    # Changed the receive timeout from its default of 0.5 seconds to 5.0 seconds
    packet = rfm.receive(timeout=5.0)
    
    # If no packet is received, then the loop is started over after incrementing check
    if packet is None:
        print("No packet received. Listening again...")
        check += 1
        continue
    
    # Resets check if a package is received
    check = 0
    
    # Prints out the raw bytes of the packet
    print(f"Received (Raw Bytes): {packet}")
    
    # Decodes the packet to get the operating mode, fcs value, data, and data index.
    # These will be passed to functions later to record the data in the packet list
    operatingMode, fcsCorrect, data, indexBytes = DataToAX25_2_1.decode_ax25_frame(packet)
    
    # Checks the fcsCorrect value
    # If false, something was corrupted during sending and the bytes were incorrect
    # The loop is started over to listen again
    if fcsCorrect is True:
        # Attempts to convert the packet data into ASCII and print it out
        try:
            packet_text = str(packet, "ascii")
            print(f"Received (ASCII) at index {dataIndex}: {packet_text}")
        # If there is an error with printing the packet data in ASCII, the
        # hex data for the packet is printed out.
        except UnicodeError:
            print("Hex data: ", [hex(x) for x in packet])

        # Reads in the RSSI (signal strength) of the last received message and
        # prints it.
        rssi = rfm.last_rssi
        print(f"Received signal strength: {rssi} dB")
        
        # Decides what function to call depending on the value of operatingMode
        # Note, there could be potential errors if there is a stop in listening
        # or 0x01 isn't sent first. 
        #
        # 0x01 indicates the number of packets for the picture was sent
        # 0x02 indicates picture packet data was sent
        # 0x03 indicates corrupted byte list was requested
        # 0x04 indicates all packages were sent properly and to terminate listening
        if operatingMode == b'\x01':
            packetList = ListeningTools.get_packet_number(data)
        elif operatingMode == b'\x02':
            dataIndex = int.from_bytes(indexBytes, 'big')
            packetList[dataIndex] = data
        elif operatingMode == b'\x03':
            rfm.send(ListeningTools.send_corrupted_packets(packetList))
            corruptedPacketsSent = True
        elif operatingMode == b'\x04':
            continueListening = False
        else:
            print("Unrecognizable command received.")
        
# Initializes an empty byte array for packet data to be added to
packetBytes = bytearray()

# Loops through each entry in packetList and adds them to packetBytes
for i in range(len(packetList)):
    b = packetList[i]
    if b is not None:
        packetBytes += b
    # If an entry is None and previous code did not catch and fix it, that is reported here.
    # The index of the None entry is recorded and that particular byte is skipped in the
    # adding process
    else:
        print(f"There is a None packet present at packet index {i}.")
# Prints out the bytearray that stores the bytes of the image
print(packetBytes)