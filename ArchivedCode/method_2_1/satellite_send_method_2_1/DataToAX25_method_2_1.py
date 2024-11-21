import binascii

def encode_ax25_frame(data: bytes, dest_callsign: str, source_callsign: str, operation: bytes, data_index: int) -> bytes:
    """
    Encodes a data payload into an AX.25 frame.

    Args:
        data (bytes): The data payload to be transmitted.
        dest_callsign (str): Destination callsign (6 characters).
        source_callsign (str): Source callsign (6 characters).
        data_index (int): The index of the data payload

    Returns:
        bytes: The AX.25 frame.
    """
    # Start flag (0x7E)
    ax25_frame = b'\x7E'
    
    # Kiss 1
    ax25_frame += b'\xc0'

    # Destination address (7 bytes)
    dest_address = f"{dest_callsign}"
    dest_address_bytes = bytes(dest_address, 'ascii')
    shifted_dest_address = bytes([byte << 1 for byte in dest_address_bytes])
    ax25_frame += shifted_dest_address
    ax25_frame += b'\x40'
    ax25_frame += b'\x61'

    # Source address (7 bytes)
    source_address = f"{source_callsign}"
    source_address_bytes = bytes(source_address, 'ascii')
    shifted_source_address = bytes([byte << 1 for byte in source_address_bytes])
    ax25_frame += shifted_source_address
    ax25_frame += b'\x40'
    ax25_frame += b'\x62'

    # Control field (0x03 for UI frames)
    ax25_frame += b'\x03'

    # Protocol ID (0xF0 for no layer 3 protocol)
    ax25_frame += b'\xF0'
    
    # Operation
    ax25_frame += operation
    
    # Data index
    index_bytes = data_index.to_bytes(2, "big")
    ax25_frame += index_bytes

    # Data payload
    ax25_frame += data

    # Kiss 2
    ax25_frame += b'\xc0'

    # FCS (Frame Check Sequence) - Calculate CRC16 and append
    crc = calculate_crc16(ax25_frame)
    ax25_frame += crc.to_bytes(2, 'big')

    # End flag (0x7E)
    ax25_frame += b'\x7E'

    return ax25_frame

def calculate_crc16(data: bytes) -> int:
    crc = 0x1D0F #CCITT-False is 0xFFFF, 
    poly = 0x1021  # CRC-CCITT polynomial

    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF  # Limit to 16 bits

    return crc

def decode_ax25_frame(frame):
    if len(frame) < 14:
        print("Invalid AX.25 frame")
        operatingMode = b'\xFF'
        fcsCorrect = False
        return operatingMode, fcsCorrect

    # AX.25 frame structure:
    # Flag (1 byte) | Destination (7 bytes) | Source (7 bytes) | Control (1 byte) | Protocol ID (1 byte) | Data | FCS (2 bytes) | Flag (1 byte)

    flag1 = frame[:1]
    kiss1 = frame[1:2]
    destination = frame[2:9]
    source = frame[9:16]
    control = frame[16:17]
    protocol_id = frame[17:18]
    operatingMode = frame[18:19]
    dataIndex = frame[19:21] # Data index field
    data = frame[21:-4]  # Data field
    kiss2 = frame[-4:-3]
    fcs = frame[-3:-1]  # Frame Check Sequence
    flag2 = frame[-1:]
    
    # Convert bytes to ASCII for destination and source addresses
    destination_address = ''.join(chr(byte >> 1) for byte in destination)
    source_address = ''.join(chr(byte >> 1) for byte in source)

    # Print decoded information
#     print("Flag1:", flag1)
#     print("Destination Address:", destination_address)
#     print("Source Address:", source_address)
#     print("Control:", control)
#     print("Protocol ID:", protocol_id)
    print("Operation: ", operatingMode)
    print("Data:", data)
    print("FCS:", fcs)
#     print("Flag2:", flag2)
    
    test = b''
    test = test + flag1
    test = test + kiss1
    test = test + destination
    test = test + source
    test = test + control
    test = test + protocol_id
    test = test + operatingMode
    test = test + dataIndex
    test = test + data
    test = test + kiss2
    newCrc = calculate_crc16(test).to_bytes(2, 'big')
    
    fcsCorrect = False
    if(newCrc == fcs):
        fcsCorrect = True

#     print("Calculated crc: ", newCrc)
#     print("Recieved crc: ", fcs)
        
    # Added data to the return items in order for the sake of testing
    # Added dataIndex to monitor the index of the packet being sent
    return operatingMode, fcsCorrect, data, dataIndex

# Example usage
# data_payload = b"Hello, world!"
# dest_callsign = "K4KDJ"
# source_callsign = "K4KDJ"
# ax25_frame = encode_ax25_frame(data_payload, dest_callsign, source_callsign)
# print("AX.25 Frame:", ax25_frame.hex())
# decode_ax25_frame(ax25_frame)

#test = b'\x7e\x96\x68\x97\xaa\x94\x42\x65\x96\x68\xb7\x88\x94\x54\x62\x03\xf0\x48\x75\x6c\x6c\x6f\x20\x77\xef\x72\x6d\x66\x21\x2a\x3a\x44\x34\x60\x7e'
#decode_ax25_frame(test)

