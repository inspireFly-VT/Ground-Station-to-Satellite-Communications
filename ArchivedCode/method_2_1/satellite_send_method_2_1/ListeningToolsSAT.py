import math
import time
from adafruit_rfm import rfm9xfsk
from satellite_send_method_2_1 import DataToAX25_method_2_1

# This is the callsign that is used as packet source and destination bytes
callsign = "K4KDJ"

def get_packet_number(size: int, step: int) -> (bytes, int):
    """
    Takes an integer that represents the total number of bytes had.
    Then calculates how many packets will need to be sent and encodes it
    into an AX25 frame, which is then returned.
    
    Args:
        size (int): The number of bytes had
        step (int): The number of bytes encoded into each packet
    Returns:
        bytes: An AX25 frame that holds the number of packets that will be sent
        int: An integer representing the number of packets that will be sent
    """
    # Calculates the number of packets that will be sent and then
    # converts it into bytes
    numberOfPackets = math.ceil(size / step)
    numberOfPacketsBytes = numberOfPackets.to_bytes(2, "big")

    # Encodes the numberOfPacketsBytes into an AX25 frame
    numberOfPacketsFrame = DataToAX25_method_2_1.encode_ax25_frame(numberOfPacketsBytes, callsign, callsign, b'\x01', 0)

    # Returns the encoded frame
    return numberOfPacketsFrame, numberOfPackets

def send_pic_data(data: bytes, rfm: RFM9xFSK, step: int, indexList: list) -> None:
    """
    Takes a byte array, rfm machine, and step counter. Then it encodes the
    byte array into AX25 packet frames of the given step size. Then sends
    the frame using the given rfm machine.
    
    Args:
        data (bytes): A byte array of the data needing to be encoded and sent
        rfm (RFM9xFSK): The rfm machine sending the bytes
        step (int): The number of bytes encoded into each packet
        indexList: A list that holds packet indices that need to be sent
    """
    # Initializes variables to track sending progress
    sentPackets = 0
    totalPackets = len(indexList)
    # This loops through every [step] bytes in jpg_bytes, encodes it into an
    # AX25 frame, and then sends it.
    for index in indexList:
        # Calculates the index of the bytes being packeted and grabs the bytes to send
        counter = index * step
        packetBytes = data[counter : counter + step]
        
        # Encodes the bytes being sent into an AX25 packet frame
        packetFrame = DataToAX25_method_2_1.encode_ax25_frame(packetBytes, callsign, callsign, b'\x02', index)
        
        # Sends the packeted data and prints out the status of the overal sending to the terminal
        rfm.send(packetFrame)
        print(f"Packet {index} sent: ", packetFrame)
        print(f"{sentPackets} packets sent, {totalPackets - sentPackets} packets left.")
        sentPackets += 1
        
        # Sleep timer to allow the groundstation to catch packets
        time.sleep(0.33)
        
    # Indiciates all packets have been sent.
    print("All packets sent")

def read_corrupt_indices(data: bytes) -> list:
    """
    Takes in a list of bytes where every two bytes represents an integer.
    Loops through the list and grabs all the integers and adds them to
    a list which is then returned
    
    Args:
        data (bytes): A byte array of the data needing to be converted to ints
    Returns:
        list: A list containing the converted integers
    """
    # Creates an empty list for corrupt indices to be added to
    corruptIndices = []
    
    # Initializes variables that represent our start and increment values
    start = 0
    inc = 2
    
    # Loops through the data and converts bytes into int
    while (start < len(data)):
        # Grabs the data two bytes at a time ad converts it to an int
        indexBytes = data[start : start + inc]
        index = int.from_bytes(indexBytes, "big")
        
        # Increments start counter
        start += inc
        
        # Appnds the new index to the list of corrupt indices
        corruptIndices.append(index)
        
    return corruptIndices
        
        
