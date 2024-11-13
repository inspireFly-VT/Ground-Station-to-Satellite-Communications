import Data_To_AX25 as AX25

message = b'InspireFly'

print(message)

AX25_message = AX25.encode_ax25_frame(message, "K4KDJ", "K4KDJ", b'\xFF')

print(AX25_message)

AX25.decode_ax25_frame(AX25_message)