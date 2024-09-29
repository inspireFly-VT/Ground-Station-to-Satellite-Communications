# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the rfm9x FSK radio.
# Author: Jerry Needell
import board
import busio
import digitalio
import rfm9xfsk
from DataToAX25 import decode_ax25_frame
from DataToAX25 import encode_ax25_frame

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.GP8)
RESET = digitalio.DigitalInOut(board.GP9)

# Initialize SPI bus.
spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)

# Initialze RFM radio
rfm9xfsk = rfm9xfsk.RFM9xFSK(spi, CS, RESET, RADIO_FREQ_MHZ)

# Print out some chip state:
print("Temperature: {0}C".format(rfm9xfsk.temperature))
print("Frequency: {0}mhz".format(rfm9xfsk.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm9xfsk.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm9xfsk.frequency_deviation))

# Send a packet.  Note you can only send a packet up to 60 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
rfm9xfsk.send(bytes("Hello world!\r\n", "utf-8"))
print("Sent hello world message!")

# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 60 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for packets...")
count = 0
while True:
    packet = rfm9xfsk.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9xfsk.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        x=2
#         print("Received nothing! Listening again...")
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
#         print("Received (raw bytes): {0}".format(packet))
        count = count + 1
        print(count)
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        
        recievedOperation, fcsCorrect = decode_ax25_frame(packet)
        GS_operation = 0
        if(recievedOperation == 20):
            print("Satellite in Joke Mode")
            GS_operation = 16
        elif recievedOperation == 21:
            print("Beacon No Picture")
            GS_operation = 16
        elif recievedOperation == 22:
            print("Beacon with picture")
            GS_operation = 16
        elif recievedOperation == 23:
            print("Face")
            GS_operation = -1
        elif recievedOperation == 25:
            print("State of health with picture")
            GS_operation = 32
        elif recievedOperation == 26:
            print("State of health without picture")
            GS_operation = 31
        elif recievedOperation == 28:
            print("Selfie")
            GS_operation = 99
        else:
            print("Unknown")
            
        if(fcsCorrect):
            print("Recieved FCS is Equal")
        else:
            print("Recieved FCS is Not Equal")
        
        message = b'\ Sent Operation 16'
        ax25_message = encode_ax25_frame(message, 'K4KDJ', 'K4KDJ', GS_operation)
        rfm9xfsk.send(ax25_message)
        print(ax25_message)
#         try:
#             worked = decode_ax25_frame(packet)
#             if(worked == False):
#                 message = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
#                 ax25_message = encode_ax25_frame(message, 'K4KDJ', 'K4KDJ')
#                 rfm9xfsk.send(ax25_message)
#                 print(ax25_message)
#             else:
#                 message = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
#                 ax25_message = encode_ax25_frame(message, 'K4KDJ', 'K4KDJ')
#                 rfm9xfsk.send(ax25_message)
#                 print(ax25_message)
#             
#         except:
#             print("error")
        
        #try:
        #    packet_text = str(packet, "ascii")
        #    print("Received (ASCII): {0}".format(packet_text))
        #except:
        #    print("Hex data: ", [hex(x) for x in packet])
        #    x = 5
        rssi = rfm9xfsk.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
