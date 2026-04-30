import ida_name
import ida_segment
import ida_bytes

def create_segment(name, start_ea, size, sclass="DATA"):
    end_ea = start_ea + size
    if not ida_segment.getseg(start_ea):
        ida_segment.add_segm(0, start_ea, end_ea, name, sclass)
        print(f"Created segment {name} at 0x{start_ea:X}")
    else:
        print(f"Segment already exists at 0x{start_ea:X}")

def define_registers():
    custom_base = 0xDFF000
    ciaa_base = 0xBFE000
    ciab_base = 0xBFD000

    create_segment("HW_CUSTOM", 0xDFF000, 0x200, "HW")
    create_segment("HW_CIAA", 0xBFE000, 0x1000, "HW")
    create_segment("HW_CIAB", 0xBFD000, 0x1000, "HW")

    # Original Chip Set (OCS) Register Map
    custom_registers = {
        0x000: "BLTDDAT",   0x002: "DMACONR",   0x004: "VPOSR",     0x006: "VHPOSR",
        0x008: "DSKDATR",   0x00A: "JOY0DAT",   0x00C: "JOY1DAT",   0x00E: "CLXDAT",
        0x010: "ADKCONR",   0x012: "POT0DAT",   0x014: "POT1DAT",   0x016: "POTGOR",
        0x018: "SERDATR",   0x01A: "DSKBYTR",   0x01C: "INTENAR",   0x01E: "INTREQR",
        0x020: "DSKPTH",    0x022: "DSKPTL",    0x024: "DSKLEN",    0x026: "DSKDAT",
        0x028: "REFPTR",    0x02A: "VPOSW",     0x02C: "VHPOSW",    0x02E: "COPCON",
        0x030: "SERDAT",    0x032: "SERPER",    0x034: "POTGO",     0x036: "JOYTEST",
        0x040: "BLTCON0",   0x042: "BLTCON1",   0x044: "BLTAFWM",   0x046: "BLTALWM",
        0x048: "BLTCPTH",   0x04A: "BLTCPTL",   0x04C: "BLTBPTH",   0x04E: "BLTBPTL",
        0x050: "BLTAPTH",   0x052: "BLTAPTL",   0x054: "BLTDPTH",   0x056: "BLTDPTL",
        0x058: "BLTSIZE",
        0x060: "BLTCMOD",   0x062: "BLTBMOD",   0x064: "BLTAMOD",   0x066: "BLTDMOD",
        0x070: "BLTCDAT",   0x072: "BLTBDAT",   0x074: "BLTADAT",
        0x07E: "DSKSYNC",   
        0x080: "COP1LCH",   0x082: "COP1LCL",   0x084: "COP2LCH",   0x086: "COP2LCL",
        0x088: "COPJMP1",   0x08A: "COPJMP2",   0x08C: "COPINS",    
        0x08E: "DIWSTRT",   0x090: "DIWSTOP",   0x092: "DDFSTRT",   0x094: "DDFSTOP",
        0x096: "DMACON",    0x098: "CLXCON",    0x09A: "INTENA",    0x09C: "INTREQ",
        0x09E: "ADKCON",
        # AUDIO
        0x0A0: "AUD0LTH", 0x0A2: "AUD0LTL", 0x0A4: "AUD0LEN", 0x0A6: "AUD0PER", 0x0A8: "AUD0VOL", 0x0AA: "AUD0DAT",
        0x0B0: "AUD1LTH", 0x0B2: "AUD1LTL", 0x0B4: "AUD1LEN", 0x0B6: "AUD1PER", 0x0B8: "AUD1VOL", 0x0BA: "AUD1DAT",
        0x0C0: "AUD2LTH", 0x0C2: "AUD2LTL", 0x0C4: "AUD2LEN", 0x0C6: "AUD2PER", 0x0C8: "AUD2VOL", 0x0CA: "AUD2DAT",
        0x0D0: "AUD3LTH", 0x0D2: "AUD3LTL", 0x0D4: "AUD3LEN", 0x0D6: "AUD3PER", 0x0D8: "AUD3VOL", 0x0DA: "AUD3DAT",
        # BITPLANES
        0x0E0: "BPL1PTH", 0x0E2: "BPL1PTL", 0x0E4: "BPL2PTH", 0x0E6: "BPL2PTL",
        0x0E8: "BPL3PTH", 0x0EA: "BPL3PTL", 0x0EC: "BPL4PTH", 0x0EE: "BPL4PTL",
        0x0F0: "BPL5PTH", 0x0F2: "BPL5PTL", 0x0F4: "BPL6PTH", 0x0F6: "BPL6PTL",
        0x0F8: "BPL7PTH", 0x0FA: "BPL7PTL", 0x0FC: "BPL8PTH", 0x0FE: "BPL8PTL",
        0x100: "BPLCON0", 0x102: "BPLCON1", 0x104: "BPLCON2",
        0x108: "BPL1MOD", 0x10A: "BPL2MOD",
        0x110: "BPL1DAT", 0x112: "BPL2DAT", 0x114: "BPL3DAT", 0x116: "BPL4DAT",
        0x118: "BPL5DAT", 0x11A: "BPL6DAT", 0x11C: "BPL7DAT", 0x11E: "BPL8DAT",
        # SPRITES
        0x120: "SPR0PTH", 0x122: "SPR0PTL", 0x124: "SPR1PTH", 0x126: "SPR1PTL",
        0x128: "SPR2PTH", 0x12A: "SPR2PTL", 0x12C: "SPR3PTH", 0x12E: "SPR3PTL",
        0x130: "SPR4PTH", 0x132: "SPR4PTL", 0x134: "SPR5PTH", 0x136: "SPR5PTL",
        0x138: "SPR6PTH", 0x13A: "SPR6PTL", 0x13C: "SPR7PTH", 0x13E: "SPR7PTL",
        # SPRITE DATA
        0x140: "SPR0POS", 0x142: "SPR0CTL", 0x144: "SPR0DATA", 0x146: "SPR0DATB",
        0x148: "SPR1POS", 0x14A: "SPR1CTL", 0x14C: "SPR1DATA", 0x14E: "SPR1DATB",
        0x150: "SPR2POS", 0x152: "SPR2CTL", 0x154: "SPR2DATA", 0x156: "SPR2DATB",
        0x158: "SPR3POS", 0x15A: "SPR3CTL", 0x15C: "SPR3DATA", 0x15E: "SPR3DATB",
        0x160: "SPR4POS", 0x162: "SPR4CTL", 0x164: "SPR4DATA", 0x166: "SPR4DATB",
        0x168: "SPR5POS", 0x16A: "SPR5CTL", 0x16C: "SPR5DATA", 0x16E: "SPR5DATB",
        0x170: "SPR6POS", 0x172: "SPR6CTL", 0x174: "SPR6DATA", 0x176: "SPR6DATB",
        0x178: "SPR7POS", 0x17A: "SPR7CTL", 0x17C: "SPR7DATA", 0x17E: "SPR7DATB",
        # COLOR PALETTE
        0x180: "COLOR00", 0x182: "COLOR01", 0x184: "COLOR02", 0x186: "COLOR03",
        0x188: "COLOR04", 0x18A: "COLOR05", 0x18C: "COLOR06", 0x18E: "COLOR07",
        0x190: "COLOR08", 0x192: "COLOR09", 0x194: "COLOR10", 0x196: "COLOR11",
        0x198: "COLOR12", 0x19A: "COLOR13", 0x19C: "COLOR14", 0x19E: "COLOR15",
        0x1A0: "COLOR16", 0x1A2: "COLOR17", 0x1A4: "COLOR18", 0x1A6: "COLOR19",
        0x1A8: "COLOR20", 0x1AA: "COLOR21", 0x1AC: "COLOR22", 0x1AE: "COLOR23",
        0x1B0: "COLOR24", 0x1B2: "COLOR25", 0x1B4: "COLOR26", 0x1B6: "COLOR27",
        0x1B8: "COLOR28", 0x1BA: "COLOR29", 0x1BC: "COLOR30", 0x1BE: "COLOR31"
    }
    
    ciaa_registers = {
        0x001: "CIAA_PRA",  0x101: "CIAA_PRB",  0x201: "CIAA_DDRA", 0x301: "CIAA_DDRB",
        0x401: "CIAA_TALO", 0x501: "CIAA_TAHI", 0x601: "CIAA_TBLO", 0x701: "CIAA_TBHI",
        0x801: "CIAA_TODLO",0x901: "CIAA_TODMID",0xA01: "CIAA_TODHI",0xB01: "CIAA_SDR",
        0xC01: "CIAA_ICR",  0xD01: "CIAA_CRA",  0xE01: "CIAA_CRB"
    }

    ciab_registers = {
        0x000: "CIAB_PRA",  0x100: "CIAB_PRB",  0x200: "CIAB_DDRA", 0x300: "CIAB_DDRB",
        0x400: "CIAB_TALO", 0x500: "CIAB_TAHI", 0x600: "CIAB_TBLO", 0x700: "CIAB_TBHI",
        0x800: "CIAB_TODLO",0x900: "CIAB_TODMID",0xA00: "CIAB_TODHI",0xB00: "CIAB_SDR",
        0xC00: "CIAB_ICR",  0xD00: "CIAB_CRA",  0xE00: "CIAB_CRB"
    }

    count = 0
    
    # Custom Chips are 16-bit words mapped at DFFxxx
    for offset, name in custom_registers.items():
        addr = custom_base + offset
        ida_bytes.create_word(addr, 2)
        if ida_name.set_name(addr, name, ida_name.SN_CHECK):
            count += 1

    # CIAA registers are mapped to odd bytes
    for offset, name in ciaa_registers.items():
        addr = ciaa_base + offset
        ida_bytes.create_byte(addr, 1)
        if ida_name.set_name(addr, name, ida_name.SN_CHECK):
            count += 1
            
    # CIAB registers are mapped to even bytes
    for offset, name in ciab_registers.items():
        addr = ciab_base + offset
        ida_bytes.create_byte(addr, 1)
        if ida_name.set_name(addr, name, ida_name.SN_CHECK):
            count += 1

    print(f"Amiga OCS Script: Successfully mapped {count} hardware registers.")

if __name__ == "__main__":
    define_registers()
