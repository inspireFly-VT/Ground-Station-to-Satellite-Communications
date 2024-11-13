with open(r"C:\Users\davee\OneDrive\Pictures\20240408_151131.jpg",'rb') as jpg_file:
    # Read the bytes of the file
    jpg_bytes = jpg_file.read()

# jpg_bytes now contains the raw byte data of the image
print(jpg_bytes)