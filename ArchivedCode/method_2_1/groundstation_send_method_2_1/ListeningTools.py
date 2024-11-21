import time
import struct
from adafruit_rfm import rfm9xfsk
from groundstation_send_method_2_1 import DataToAX25_2_1

def get_packet_number(size: bytes) -> list:
    """
    It takes a size (bytes) and returns an empty list of None objects of the given size.
    Args:
        size (bytes): The number of packets going to be sent in bytes.

    Returns:
        list: An empty list of None objects that is of the given size.
    """
    # Converts the size parameter from bytes to int
    numberOfPackets = int.from_bytes(size, 'big')
    
    # Prints out the expected number of packets
    print(f"The expected number of packets is {numberOfPackets}")
    
    # Creates an empty list and appends None objects corresponding to the
    # number of packets inputted (AKA size)
    packetList = []
    for i in range(numberOfPackets):
        packetList.append(None)
        
    # Returns the packetList
    return packetList

def send_corrupted_packets(packetList: list) -> bytes:
    """
    Takes a list storing packet data. It returns a list of all the indices that
    do not have a proper packet stored, i.e. None is stored at the specified index.
    Then the bytes of the AX25 framed list is returned

    Args:
        packetList (list): The packet list to be checked for None values
    Returns:
        bytes: The list of corrupted packet indices in bytes in an AX25 frame
    """
    # Creates an empty list to append packet indices to
    corruptedList = []
    
    # Loops through each entry in the packetList and appends the index of
    # the entry if packetList[i] is None
    for i in range(len(packetList)):
        if packetList[i] is None:
            corruptedList.append(i)
            
    # This is the callsign for our satellite and ground station
    callsign = "K4KDJ"

    # Converts the list of corrupted/missing packets into a byte string, where each entry is 2 bytes long
    corruptedListBytes = b''.join(struct.pack('h', num) for num in corruptedList)
    
    # Converts the list of corrupted indicies byte string into an AX25 frame to be sent
    corruptedListFrame = DataToAX25_2_1.encode_ax25_frame(corruptedListBytes, callsign, callsign, b'\x00', 1)
    
    # Returns AX25 frame of corrupted indicies
    # Sleep for a second to give the satellite time to start receiving
    time.sleep(1.0)
    return corruptedListFrame
    
    


# def continuousListening(packetList: list, packetNumber: int) -> list:
#     """
#     Takes a list to add packet data to. Then, it listens for send messages
#     for certain amount of time. For each packet the ground station receives,
#     the packet is decoded and the packet data is stored.
# 
#     Args:
#         packetList (list): The packet list for packet data to be added to.
# 
#     Returns:
#         list: The packet list with the updated packet data
#     """
#     # Creates a counter to keep count of the number of times the while loop below is run
#     # Creates a boolean check to see if the last packet is received or not
#     continueSending = True
#     listeningCounter = 0
# 
#     while listeningCounter < (packetNumber) and continueSending:
#         # Increments listening counter
#         listeningCounter += 1
#         # Optionally change the receive timeout from its default of 0.5 seconds:
#         packet = rfm.receive(timeout=1.0)
#         # If no packet was received during the timeout then None is returned.
#         if packet is None:
#             # Packet has not been received
#             print("Received nothing! Listening again...")
#         else:
#             # Received a packet!
#             # Print out the raw bytes of the packet:        
#             print(f"Received (raw bytes): {packet}")
#             # And decode to ASCII text and print it too.  Note that you always
#             # receive raw bytes and need to convert to a text format like ASCII
#             # if you intend to do string processing on your data.  Make sure the
#             # sending side is sending ASCII data before you try to decode!
# 
#             
#             # Decodes packet
#             operatingMode, fcsCorrect, data, packetIndex = DataToAX25_2_1.decode_ax25_frame(packet)
#             packetIndex = int.from_bytes(packetIndex, "big")
#             
#             # Asks for packet again if fcsCorrect is false
#             # If fcsCorrect is false, no confirmation message is sent to the satellite
#             # Then satellite should send it again
#             if not fcsCorrect:
#                 print("fcs not correct")
#     #             rfm.send(None)
#                 continue
#             
#             packetList[packetIndex] = data
#             try:
#                 packet_text = str(packet, "ascii")
#                 print(f"Received (ASCII) at index {packetIndex}: {packet_text}")
#             except UnicodeError:
#                 print("Hex data: ", [hex(x) for x in packet])
# 

#             
#             if packetIndex == numberOfPackets - 1:
#                 continueSending = False
#     return packetList
# 
# # This is the callsign for our satellite and ground station
# callsign = "K4KDJ"
#     
# # Declares a variable to store the number of packets being sent
# numberOfPackets = -1
#     
# # Tells the satellite to send the number of packets
# rfm.send("Send number of packets")
# 
# while True:
#     # Optionally change the receive timeout from its default of 0.5 seconds:
#     packet = rfm.receive(timeout=5.0)
#     
#     # If no packet was received during the timeout then None is returned.
#     if packet is None:
#         # Packet has not been received
#         print("Received nothing! Listening again...")
#         
#     else:
#         # Received a packet!
#         # Print out the raw bytes of the packet:        
#         print(f"Received (raw bytes): {packet}")
#         # And decode to ASCII text and print it too.  Note that you always
#         # receive raw bytes and need to convert to a text format like ASCII
#         # if you intend to do string processing on your data.  Make sure the
#         # sending side is sending ASCII data before you try to decode!
#         
#         # Decodes the packet, the data field should hold a byte representation of the number
#         # of packets that will be sent
#         operatingMode, fcsCorrect, size, dataIndex = DataToAX25_2_1.decode_ax25_frame(packet)
#         
#         # Checks fcsCorrect value to check for corruption. If fcsCorrect is false,
#         # no confirmation message is sent so the satellite resends info.
#         if not fcsCorrect:
#             print("fcs not correct")
#             continue
#         
#         # Converts 
#         numberOfPackets = int.from_bytes(size, 'big')
#         break;
#         
# # Prints out the number of expected packets
# print(f"Expected number of packets is {numberOfPackets}.")
# # Creates an empty list of the expected size, filled with None values
# # Packet data will be stored in this
# packetList = []
# for i in range(numberOfPackets):
#     packetList.append(None)
#     
# # Tells satellite to send packets
# rfm.send("Send packets")
# 
# # Wait to receive packets.
# print("Waiting for packets...")
# packetList = continuousListening(packetList, numberOfPackets)
# 
# corruptedPackets = checkCorruptedPackets(packetList)
# while len(corruptedPackets) != 0:
#     # Converts the list of corrupted/missing packets into a byte string, where each entry is 2 bytes long
#     corruptedIndicesBytes = b''.join(struct.pack('h', num) for num in corruptedPackets)
#     
#     # Converts the corrupted indicies byte string into an AX25 frame to be sent
#     corruptedIndicesFrame = DataToAX25_2_1.encode_ax25_frame(corruptedIndicesBytes, callsign, callsign, b'\x00', 1)
#     
#     # Sends AX25 frame of corrupted indicies
#     rfm.send(corruptedIndicesFrame)
#     
#     # Listens for satellite response with new packets
#     packetList = continuousListening(packetList, len(corruptedPackets))
#     
#     # Rechecks packetList to update the corruptedPacketList
#     corruptedPackets = checkCorruptedPackets(packetList)
#     print(corruptedPackets)