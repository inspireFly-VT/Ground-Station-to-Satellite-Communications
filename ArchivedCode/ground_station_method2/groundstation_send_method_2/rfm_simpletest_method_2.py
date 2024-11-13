# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell


import board
import busio
import digitalio
import time
from adafruit_rfm import rfm9xfsk
from groundstation_send_method_2 import Data_To_AX25_method_2

def checkCorruptedPackets(packetList: list) -> list:
    corruptedPackets = []
    for i in range(len(packetList)):
        if i is None:
            corruptedPackets.append(i)
    if len(corruptedPackets) == 0:
        return None
    return corruptedPackets

def continuousListening(packetList: list) -> list:
    # Creates a counter to keep count of the number of times the while loop below is run
    # Creates a boolean check to see if the last packet is received or not
    continueSending = True
    listeningCounter = 0

    while listeningCounter < (numberOfPackets) and continueSending:
        # Increments listening counter
        listeningCounter += 1
        # Optionally change the receive timeout from its default of 0.5 seconds:
        packet = rfm.receive(timeout=1.0)
        # If no packet was received during the timeout then None is returned.
        if packet is None:
            # Packet has not been received
            print("Received nothing! Listening again...")
        else:
            # Received a packet!
            # Print out the raw bytes of the packet:        
            print(f"Received (raw bytes): {packet}")
            # And decode to ASCII text and print it too.  Note that you always
            # receive raw bytes and need to convert to a text format like ASCII
            # if you intend to do string processing on your data.  Make sure the
            # sending side is sending ASCII data before you try to decode!

            
            # Decodes packet
            operatingMode, fcsCorrect, data, packetIndex = Data_To_AX25_method_2.decode_ax25_frame(packet)
            packetIndex = int.from_bytes(packetIndex, "big")
            
            # Asks for packet again if fcsCorrect is false
            # If fcsCorrect is false, no confirmation message is sent to the satellite
            # Then satellite should send it again
            if not fcsCorrect:
                print("fcs not correct")
    #             rfm.send(None)
                continue
            
            packetList[packetIndex] = data
            try:
                packet_text = str(packet, "ascii")
                print(f"Received (ASCII) at index {packetIndex}: {packet_text}")
            except UnicodeError:
                print("Hex data: ", [hex(x) for x in packet])

            # Also read the RSSI (signal strength) of the last received message and
            # print it.
            rssi = rfm.last_rssi
            print(f"Received signal strength: {rssi} dB")
            
            if packetIndex == numberOfPackets - 1:
                continueSending = False
    return packetList

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
    
# Declares a variable to store the number of packets being sent
numberOfPackets = -1
    
# Tells the satellite to send the number of packets
rfm.send("Send number of packets")

while True:
    # Optionally change the receive timeout from its default of 0.5 seconds:
    packet = rfm.receive(timeout=5.0)
    
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
        
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:        
        print(f"Received (raw bytes): {packet}")
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        
        # Decodes the packet, the data field should hold a byte representation of the number
        # of packets that will be sent
        operatingMode, fcsCorrect, size, dataIndex = Data_To_AX25_method_2.decode_ax25_frame(packet)
        
        # Checks fcsCorrect value to check for corruption. If fcsCorrect is false,
        # no confirmation message is sent so the satellite resends info.
        if not fcsCorrect:
            print("fcs not correct")
            continue
        
        # Converts 
        numberOfPackets = int.from_bytes(size, 'big')
        break;
        
# Prints out the number of expected packets
print(f"Expected number of packets is {numberOfPackets}.")
# Creates an empty list of the expected size
packetList = []
for i in range(numberOfPackets):
    packetList.append(None)
    
# Tells satellite to send packets
rfm.send("Send packets")

# Wait to receive packets.
print("Waiting for packets...")
packetList = continuousListening(packetList)

corruptedPackets = checkCorruptedPackets(packetList)
while corruptedPackets is not None:
    # Converts the list of corrupted/missing packets into a byte string, where each entry is 2 bytes long
    corruptedIndicesBytes = b''.join(struct.pack('h', num) for num in corruptedPackets)
    
    # Converts the corrupted indicies byte string into an AX25 frame to be sent
    corruptedIndiciesFrame = Data_To_AX25_method_2.encode_ax25_frame(corruptedIndicesBytes)
    
    # Sends AX25 frame of corrupted indicies
    rfm.send(corruptedIndiciesFrame)
    
    # Listens for satellite response with new packets
    packetList = continuousListening(packetList)
    
    # Rechecks packetList to update the corruptedPacketList
    corruptedPackets = checkCorruptedPackets(packetList)
       
packetBytes = bytearray()
for b in packetList:
    if b is not None:
        packetBytes += b
    else:
        print("There is a None packet present.")
print(packetBytes)
        
#receivedPacket = bytearray()