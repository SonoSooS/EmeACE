import io
import struct

# Could be argv[0]
SAVEFILE_NAME = "pokecontest.sav"
# Couild be argv[1]
PAYLOAD_NAME = "payload.bin"
# Could be argv[2]
SAVEFILE_OUT_NAME = "pokeace.sav"

SAVE_SLOT = 0xC
SAVE_OFFS = 0


def bytes_replace(data, offset, replacing):
    return data[0 : offset] + replacing + data[(offset + len(replacing)) : ]
    

def section_calc_length(section_number):
    # https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III)#Section_ID
    
    section_length = 3968 # 0xF80
    
    if section_number == 0:
        section_length = 3884
    elif section_number == 4:
        section_length == 3848
    elif section_number == 13:
        section_length = 2000
    
    return section_length
    

def section_checksum(section, section_length):
    # Do the literal check-sum over each u32,
    #  like described in the file structure linked here:
    # https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III)#Checksum
    chksum = 0xFFFFFFFF & sum(d[0] for d in struct.iter_unpack("<I", section[0:section_length]))
    
    # Convert int to bytes for the lower and upper u16 adding
    realsum = struct.pack("<I", chksum)
    
    # Use struct hack to add the lower and upper u16 together
    realsum = 0xFFFF & sum(d[0] for d in struct.iter_unpack("<H", realsum))
    
    # Convert real checksum to bytes for writing to file
    realsum_data = struct.pack("<H", realsum)
    
    return realsum_data
    

def section_verify(section):
    section_number = struct.unpack("<H", section[0xFF4:0xFF6])[0]
    section_chksum = section[0xFF6:0xFF8]
    
    section_length = section_calc_length(section_number)
    
    chksum = section_checksum(section, section_length)
    
    return chksum == section_chksum
    

def section_fix(section):
    section_number = struct.unpack("<H", section[0xFF4:0xFF6])[0]
    section_length = section_calc_length(section_number)
    
    chksum = section_checksum(section, section_length)
    
    #section = bytes_replace(section, 0xFF6, chksum)
    section = section[0 : 0xFF6] + chksum + section[0xFF8 : ]
    
    return section
    

def section_split(save):
    saves = 14 * [None]
    
    for i in range(0, 14):
        splitted = save[0x1000 * i : 0x1000 * (i + 1)]
        
        section_number = struct.unpack("<H", splitted[0xFF4:0xFF6])[0]
        
        if section_number >= 14:
            raise Exception("Savefile corrupted: section number out of range")
        
        if saves[section_number] != None:
            raise Exception("Savefile corrupted: section number duplicate " + section_number)
        
        saves[section_number] = splitted
    
    return saves
    
def section_join(saves):
    invalid_count = sum((1 if len(section) != 0x1000 else 0) for section in saves)
    
    if invalid_count != 0:
        raise Exception("Programming error: section size barbarized")
    
    return b''.join(saves)
    

def exploit_do(saves):
    payload = None
    
    with io.open(PAYLOAD_NAME, "rb") as f:
        payload = f.read()
    
    saveslot = saves[SAVE_SLOT]
    
    slotlen = section_calc_length(SAVE_SLOT)
    payloadlen = len(payload)
    
    if((payloadlen + SAVE_OFFS) >= slotlen):
        raise Exception("Payload oversized!")
    
    #saveslot = bytes_replace(saveslot, SAVE_OFFS, payload)
    saveslot = saveslot[0 : SAVE_OFFS] + payload + saveslot[(SAVE_OFFS + payloadlen) : ]
    
    
    saveslot = section_fix(saveslot)
    
    saves[SAVE_SLOT] = saveslot
    
    pass
    

if __name__ == '__main__':
    # Two save buffers for wear leveling
    save1 = None
    save2 = None
    # Rest of the savedata
    save_rest = None
    
    # Selected save, other gets FF'd out
    save = None
    
    
    with io.open(SAVEFILE_NAME, "rb") as f:
        save1 = f.read(0xE000)
        save2 = f.read(0xE000)
        save_rest = f.read() # Read to end
    
    buf1 = save1[0x0FF8:0x1000]
    buf2 = save2[0x0FF8:0x1000]
    
    if buf2[0:4] != b'\x25\x20\x01\x08': # Uninitialized data
        save = save1
    elif buf1[0:4] != b'\x25\x20\x01\x08': # Uninitialized data (not possible, but just in case)
        save = save2
    else:
        id1 = struct.pack("<I", buf1[0xFFC:0x1000])
        id2 = struct.pack("<I", buf2[0xFFC:0x1000])
        
        save = save1 if id1 > id2 else save2
    
    if save[0x0FF8:0x0FFC] != b'\x25\x20\x01\x08':
        raise Exception("Save is uninitialized or corrupted!")
    
    
    save_ordered = section_split(save)
    
    num_correct = sum(section_verify(section) for section in save_ordered)
    
    if num_correct != len(save_ordered):
        raise Exception("Save corrupted: unverifiable sections: " + str(14 - num_correct))
    
    exploit_do(save_ordered)
    
    save = section_join(save_ordered)
    
    
    with io.open(SAVEFILE_OUT_NAME, "wb") as f:
        f.write(save)
        f.write(0xE000 * b'\xFF')
        f.write(save_rest)
    
