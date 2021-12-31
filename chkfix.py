import io
import struct

# Could be argv[0]
SAVEFILE_NAME = "pokecontest.sav"

# Box buffer
boxbytes = None

with io.open(SAVEFILE_NAME, "rb") as f:
    # Relevant box data starts at 0xD000
    # According to the ID at 0xDFF4 in pokecontest.sav being 0x000B,
    #  we must use a size of 3968 for checksum according to the file structure here:
    # https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III)#Section_ID
    
    f.seek(0xD000, io.SEEK_SET)
    boxbytes = f.read(3968)     

# Do the literal check-sum over each u32,
#  like described in the file structure linked here:
# https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III)#Checksum
chksum = 0xFFFFFFFF & sum(d[0] for d in struct.iter_unpack("<I", boxbytes))

# Convert int to bytes for the lower and upper u16 adding
realsum = struct.pack("<I", chksum)
# Use struct hack to add the lower and upper u16 together
realsum = 0xFFFF & sum(d[0] for d in struct.iter_unpack("<H", realsum))

# Convert real checksum to bytes for writing to file
realsum_data = struct.pack("<H", realsum)

# Open (existing) file in write overwrite mode
with io.open(SAVEFILE_NAME, "r+b") as f:
    # Checksum u16 is located at +0xFF6 according ot the file structure document:
    # https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III)#Section_format
    f.seek(0xDFF6, io.SEEK_SET)
    f.write(realsum_data) # Overwrites instead of inserts
