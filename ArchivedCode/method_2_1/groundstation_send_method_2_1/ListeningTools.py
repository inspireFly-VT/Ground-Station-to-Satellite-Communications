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
    print(corruptedList)
            
    # This is the callsign for our satellite and ground station
    callsign = "K4KDJ"

    # Converts the list of corrupted/missing packets into a byte string, where each entry is 2 bytes long
    corruptedListBytes = b''
    
    for index in corruptedList:
        indexBytes = index.to_bytes(2, "big")
        corruptedListBytes += indexBytes
    
    # Converts the list of corrupted indicies byte string into an AX25 frame to be sent
    corruptedListFrame = DataToAX25_2_1.encode_ax25_frame(corruptedListBytes, callsign, callsign, b'\x00', 1)
    
    # Returns AX25 frame of corrupted indicies
    # Sleep for a second to give the satellite time to start receiving
    time.sleep(1.0)
    return corruptedListFrame
