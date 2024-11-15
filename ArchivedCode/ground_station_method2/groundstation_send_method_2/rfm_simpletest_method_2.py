# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell


import board
import busio
import digitalio
import time
import struct
from adafruit_rfm import rfm9xfsk
from groundstation_send_method_2 import Data_To_AX25_method_2

def checkCorruptedPackets(packetList: list) -> list:
    """
    Takes a list storing packet data and returns a list of all the indices that
    do not have a proper packet stored, i.e. None is stored at the index.

    Args:
        packetList (list): The packet list to be checked for None values

    Returns:
        list: A list of integers that represent the indices that are missing
              packet values.
    """
    # Creates an empty list to append packet indices to
    corruptedPackets = []
    
    # Loops through each entry in the packetList and appends the index of
    # the entry if packetList[i] is None
    for i in range(len(packetList)):
        if packetList[i] is None:
            corruptedPackets.append(i)
            
    # If the length of the corruptedPackets is still empty even after the packetList
    # looped through, then there are no missing packets and None is returned
#     if len(corruptedPackets) == 0:
#         return None
    # Returns the list of corrupted packet indices
    return corruptedPackets

def continuousListening(packetList: list, packetNumber: int) -> list:
    """
    Takes a list to add packet data to. Then, it listens for send messages
    for certain amount of time. For each packet the ground station receives,
    the packet is decoded and the packet data is stored.

    Args:
        packetList (list): The packet list for packet data to be added to.

    Returns:
        list: The packet list with the updated packet data
    """
    # Creates a counter to keep count of the number of times the while loop below is run
    # Creates a boolean check to see if the last packet is received or not
    continueSending = True
    listeningCounter = 0

    while listeningCounter < (packetNumber) and continueSending:
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
    
# This is the callsign for our satellite and ground station
callsign = "K4KDJ"
    
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
# Creates an empty list of the expected size, filled with None values
# Packet data will be stored in this
packetList = []
for i in range(numberOfPackets):
    packetList.append(None)
    
# Tells satellite to send packets
rfm.send("Send packets")

# Wait to receive packets.
print("Waiting for packets...")
packetList = continuousListening(packetList, numberOfPackets)

corruptedPackets = checkCorruptedPackets(packetList)
while len(corruptedPackets) != 0:
    # Converts the list of corrupted/missing packets into a byte string, where each entry is 2 bytes long
    corruptedIndicesBytes = b''.join(struct.pack('h', num) for num in corruptedPackets)
    
    # Converts the corrupted indicies byte string into an AX25 frame to be sent
    corruptedIndicesFrame = Data_To_AX25_method_2.encode_ax25_frame(corruptedIndicesBytes, callsign, callsign, b'\x00', 1)
    
    # Sends AX25 frame of corrupted indicies
    rfm.send(corruptedIndicesFrame)
    
    # Listens for satellite response with new packets
    packetList = continuousListening(packetList, len(corruptedPackets))
    
    # Rechecks packetList to update the corruptedPacketList
    corruptedPackets = checkCorruptedPackets(packetList)
    print(corruptedPackets)

# Compiles the packet list into a byte array by appending each entry in packet list
# into a byte array
packetBytes = bytearray()

for i in range(len(packetList)):
    b = packetList[i]
    if b is not None:
        packetBytes += b
    # If an entry is None and previous code did not catch and fix it, that is reported here.
    # The index of the None entry is recorded and that particular byte is skipped
    else:
        print(f"There is a None packet present at packet index {i}.")
# Prints out the bytearray that stores the bytes of the image
print(packetBytes)
