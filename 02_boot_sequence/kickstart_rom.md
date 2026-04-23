[← Home](../README.md) · [Boot Sequence](README.md)

# Kickstart ROM — Internal Structure, Module Layout, Custom ROMs

## Overview

The Kickstart ROM is a single binary image containing the entire AmigaOS kernel — exec.library, graphics.library, dos.library, device drivers, system resources, and boot code. Understanding its internal structure is essential for ROM modding, FPGA core development, and reverse engineering. This document covers the binary layout, how modules are organized, how to extract and rebuild ROMs, and how to create custom Kickstart images.

---

## ROM Types

| Kickstart | Size | Base Address | Models | ROM Chips |
|---|---|---|---|---|
| 1.0–1.1 | 256 KB | `$FC0000` | A1000 (WCS) | 2× 128 KB |
| 1.2 | 256 KB | `$FC0000` | A500 (early), A2000 | 2× 128 KB |
| 1.3 | 256 KB | `$FC0000` | A500, A2000 | 2× 128 KB (27C010) |
| 2.04 | 512 KB | `$F80000` | A500+ | 2× 256 KB (27C020) |
| 2.05 | 512 KB | `$F80000` | A600 | 1× 512 KB (27C040) |
| 3.0 | 512 KB | `$F80000` | A1200, A4000 | 1× 512 KB (27C040) |
| 3.1 | 512 KB | `$F80000` | All models | 1× 512 KB or 2× 256 KB |
| 3.1.4 | 512 KB | `$F80000` | All models | 1× 512 KB |
| 3.2 | 512 KB | `$F80000` | All models | 1× 512 KB |
| CD32 ext | 512 KB | `$E00000` | CD32 | Extension ROM bank |

---

## Binary Structure

### Memory Layout (512 KB Kickstart)

```
$F80000 ┌──────────────────────────────────┐
        │ Reset Vectors (8 bytes)          │
        │   $F80000: Initial SSP ($000400) │
        │   $F80004: Initial PC            │
$F80008 ├──────────────────────────────────┤
        │ ROM Header (16 bytes)            │
        │   Magic word ($1114 or $1111)    │
        │   ROM size in KB (512)           │
        │   Flags / version info           │
$F80018 ├──────────────────────────────────┤
        │ Boot Code                        │
        │   Hardware init                  │
        │   ROM checksum                   │
        │   Memory detection               │
        │   OVL clear                      │
        ├──────────────────────────────────┤
        │ Resident Module Area             │
        │ ┌────────────────────────────┐   │
        │ │ exec.library               │   │
        │ │   RomTag ($4AFC)           │   │
        │ │   Code + data              │   │
        │ ├────────────────────────────┤   │
        │ │ expansion.library          │   │
        │ ├────────────────────────────┤   │
        │ │ graphics.library           │   │
        │ ├────────────────────────────┤   │
        │ │ layers.library             │   │
        │ ├────────────────────────────┤   │
        │ │ intuition.library          │   │
        │ ├────────────────────────────┤   │
        │ │ dos.library                │   │
        │ ├────────────────────────────┤   │
        │ │ ... more modules ...       │   │
        │ └────────────────────────────┘   │
        ├──────────────────────────────────┤
        │ System Fonts                     │
        │   Topaz 8, Topaz 9               │
        ├──────────────────────────────────┤
        │ Resident Module Pointer Table    │
        │   (Array of pointers to RomTags) │
        ├──────────────────────────────────┤
        │ Exec ROM Entry (boot entry point)│
        ├──────────────────────────────────┤
$FFFFF8 │ Checksum Complement (4 bytes)    │
$FFFFFC │ ROM End Marker (4 bytes)         │
$FFFFFF └──────────────────────────────────┘
```

### ROM Header

```c
/* At ROM_BASE + 8 */
struct KickstartHeader {
    UWORD kh_Magic;         /* $1114 (512KB) or $1111 (256KB) */
    UWORD kh_SizeKB;        /* ROM size / 1024 */
    ULONG kh_Flags;         /* ROM type flags */
    UWORD kh_Version;       /* Major.Minor */
    UWORD kh_Revision;      /* Revision number */
};
```

| Magic | Meaning |
|---|---|
| `$1111` | 256 KB ROM (Kickstart 1.x) |
| `$1114` | 512 KB ROM (Kickstart 2.0+) |

### Checksum Complement

The checksum complement is located at a fixed offset near the end of the ROM:

| ROM Size | Complement Offset | Absolute Address |
|---|---|---|
| 256 KB | `$3FFE8` | `$FFFFE8` |
| 512 KB | `$7FFE8` | `$FFFFE8` |

---

## Resident Module Layout

Modules are packed sequentially in the ROM. Each module starts with a RomTag (`$4AFC`):

```
Module N:
    ┌─────────────────────────┐
    │ RomTag ($4AFC)          │  26 bytes
    │   rt_MatchWord = $4AFC  │
    │   rt_MatchTag → self    │
    │   rt_EndSkip → past end │
    │   rt_Flags, rt_Version  │
    │   rt_Type, rt_Pri       │
    │   rt_Name → name string │
    │   rt_IdString → ID      │
    │   rt_Init → init func   │
    ├─────────────────────────┤
    │ Function Code           │  Variable size
    │   Library functions     │
    │   Internal routines     │
    ├─────────────────────────┤
    │ Data / Constants        │
    │   String tables         │
    │   Default values        │
    ├─────────────────────────┤
    │ Name String             │  "exec.library\0"
    │ ID String               │  "exec 40.70 (16.7.93)\r\n\0"
    └─────────────────────────┘
    ← rt_EndSkip points here
```

### Kickstart 3.1 (40.068) Module Inventory

| Module | Type | Size (approx) | Init Priority |
|---|---|---|---|
| exec.library | `NT_LIBRARY` | ~48 KB | 126 |
| expansion.library | `NT_LIBRARY` | ~8 KB | 120 |
| 68040.library | `NT_LIBRARY` | ~12 KB | 105 |
| utility.library | `NT_LIBRARY` | ~6 KB | 100 |
| mathieeesingbas.library | `NT_LIBRARY` | ~2 KB | 96 |
| alib (private) | `NT_LIBRARY` | ~1 KB | 80 |
| graphics.library | `NT_LIBRARY` | ~80 KB | 70 |
| layers.library | `NT_LIBRARY` | ~14 KB | 60 |
| cia.resource | `NT_RESOURCE` | ~3 KB | 55 |
| potgo.resource | `NT_RESOURCE` | ~1 KB | 52 |
| misc.resource | `NT_RESOURCE` | ~1 KB | 50 |
| intuition.library | `NT_LIBRARY` | ~70 KB | 50 |
| timer.device | `NT_DEVICE` | ~4 KB | 40 |
| keyboard.device | `NT_DEVICE` | ~4 KB | 35 |
| gameport.device | `NT_DEVICE` | ~3 KB | 30 |
| input.device | `NT_DEVICE` | ~6 KB | 20 |
| trackdisk.device | `NT_DEVICE` | ~14 KB | 10 |
| carddisk.device | `NT_DEVICE` | ~4 KB | 5 |
| audio.device | `NT_DEVICE` | ~6 KB | 5 |
| console.device | `NT_DEVICE` | ~22 KB | 0 |
| dos.library | `NT_LIBRARY` | ~50 KB | −50 |
| filesystem (FFS) | handler | ~18 KB | −50 |
| ramlib | module | ~4 KB | −120 |
| strap (bootstrap) | module | ~4 KB | −120 |
| **Total** | | **~400 KB** | |

The remaining ~112 KB contains fonts, boot code, ROM entry, padding, and the checksum.

---

## Extracting Modules from a ROM

### Using Python (romtool from amitools)

```bash
# Install amitools
pip install amitools

# List all modules in a ROM:
romtool list kick31.rom
# Output:
#   0: exec.library      V40.70  pri=126  flags=COLDSTART
#   1: expansion.library  V40.2   pri=120  flags=COLDSTART
#   ...

# Extract (split) all modules:
romtool split kick31.rom output_dir/
# Creates individual module files + index.txt

# Show ROM info:
romtool info kick31.rom
# Output:
#   Size: 524288 (512 KB)
#   Header: $1114
#   Checksum: OK ($FFFFFFFF)
#   Version: 40.068
```

### Using Manual Scanning

```python
#!/usr/bin/env python3
"""Scan a Kickstart ROM for resident modules"""
import struct

def scan_rom(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    rom_base = 0xF80000 if len(data) == 524288 else 0xFC0000

    offset = 0
    while offset < len(data) - 26:
        # Look for RomTag magic word $4AFC
        word = struct.unpack('>H', data[offset:offset+2])[0]
        if word == 0x4AFC:
            # Read rt_MatchTag (self-pointer)
            match_tag = struct.unpack('>I', data[offset+2:offset+6])[0]
            expected = rom_base + offset

            if match_tag == expected:
                # Valid RomTag — extract fields
                end_skip = struct.unpack('>I', data[offset+6:offset+10])[0]
                flags    = data[offset+10]
                version  = data[offset+11]
                rt_type  = data[offset+12]
                pri      = struct.unpack('>b', bytes([data[offset+13]]))[0]
                name_ptr = struct.unpack('>I', data[offset+14:offset+18])[0]
                id_ptr   = struct.unpack('>I', data[offset+18:offset+22])[0]

                # Read name string
                name_off = name_ptr - rom_base
                name = data[name_off:data.index(0, name_off)].decode('ascii')

                print(f"  ${rom_base+offset:08X}: {name:30s}  V{version}  pri={pri:4d}")

                # Skip to end of this module
                offset = end_skip - rom_base
                continue

        offset += 2  # Must be word-aligned

scan_rom('kick31.rom')
```

### Dumping from Real Hardware

```
; On a real Amiga — dump ROM to disk:
; Using transrom:
1> transrom >RAM:kick.rom

; Or via shell:
1> C:Copy ROM: RAM:kick.rom

; The ROM: device provides direct access to the Kickstart ROM image
```

---

## Building Custom Kickstart ROMs

### Using romtool (amitools)

```bash
# Start with extracted modules:
romtool split kick31.rom modules/

# Edit index.txt to add/remove/reorder modules
# Replace a module:
cp my_patched_dos.library modules/dos.library

# Rebuild:
romtool build modules/ custom_kick.rom
# romtool automatically:
#   1. Packs all modules sequentially
#   2. Builds the ResModules pointer table
#   3. Calculates and inserts checksum complement
#   4. Verifies the final image

# Verify:
romtool info custom_kick.rom
```

### Using Remus (Amiga-native)

Remus is a GUI-based Kickstart editor:

1. Load a base ROM image
2. Drag modules between ROM images
3. Replace individual modules with patched versions
4. Click "Build" — handles packing, alignment, checksum
5. Save the result and burn to EPROM

### Manual ROM Assembly

```python
#!/usr/bin/env python3
"""Minimal ROM builder — calculates checksum"""
import struct

def build_rom(modules, rom_size=524288):
    rom = bytearray(rom_size)
    rom_base = 0xF80000 if rom_size == 524288 else 0xFC0000

    # 1. Write reset vectors
    struct.pack_into('>I', rom, 0, 0x00000400)  # Initial SSP
    struct.pack_into('>I', rom, 4, rom_base + 0x0008)  # Initial PC

    # 2. Write ROM header
    struct.pack_into('>H', rom, 8, 0x1114)  # Magic (512KB)
    struct.pack_into('>H', rom, 10, rom_size // 1024)

    # 3. Pack modules starting at offset $20
    offset = 0x20
    for mod_data in modules:
        rom[offset:offset+len(mod_data)] = mod_data
        offset += len(mod_data)
        # Align to word boundary
        if offset & 1:
            offset += 1

    # 4. Calculate checksum complement
    checksum = 0
    # Clear complement location first
    ck_offset = rom_size - 24
    struct.pack_into('>I', rom, ck_offset, 0)

    for i in range(0, rom_size, 4):
        val = struct.unpack('>I', rom[i:i+4])[0]
        checksum = (checksum + val) & 0xFFFFFFFF
        if checksum < val:  # Carry
            checksum = (checksum + 1) & 0xFFFFFFFF

    complement = (0xFFFFFFFF - checksum) & 0xFFFFFFFF
    struct.pack_into('>I', rom, ck_offset, complement)

    return bytes(rom)
```

---

## ROM Variants and Extensions

### Extended ROMs (CD32, A4000T)

Some systems have a secondary ROM mapped at `$E00000`:

| System | Main ROM | Extension ROM |
|---|---|---|
| CD32 | `$F80000` (512 KB) | `$E00000` (512 KB) — CD filesystem, NVRAM |
| A4000T | `$F80000` (512 KB) | (None — all in main ROM) |
| A1000 | WCS (256 KB) | Loaded from floppy into WCS RAM |

### MapROM / Soft-Kickstart

Many accelerator boards support **MapROM** — loading a Kickstart image into Fast RAM and remapping the ROM address range:

```
1> LoadModule ROM:68040.library     ; Load replacement module
1> MapROM kick32.rom                ; Copy to Fast RAM, remap $F80000
1> Reset                            ; Warm reset — boots from RAM copy
```

This allows running newer Kickstart versions without burning EPROMs.

### 1 MB ROM Images

Some setups combine a 512 KB Kickstart with a 512 KB extension ROM:

```
$E00000–$E7FFFF: Extension ROM (512 KB)
$F80000–$FFFFFF: Main Kickstart (512 KB)
```

Tools like Remus and Capitoline can build combined 1 MB images.

---

## Burning Physical ROMs

| ROM Size | EPROM Type | Pin Count | Notes |
|---|---|---|---|
| 256 KB | 27C020 | 32-pin | Used in pairs (Hi/Lo byte) |
| 512 KB | 27C040 / 27C400 | 32/40-pin | Single chip (A600/A1200) |
| 512 KB | 29F040 (Flash) | 32-pin | Reflashable — recommended for development |

### Programming Steps

1. Build or verify your ROM image with correct checksum
2. Program the EPROM/Flash using a TL866-II+ or similar programmer
3. For 256 KB pairs: split the image into even/odd bytes
4. Insert into the correct socket(s) — verify orientation
5. Power on — should boot cleanly if image is valid

```bash
# Split 512 KB image into Hi/Lo bytes for dual-chip setups:
romtool split-bytes custom_kick.rom kick_hi.bin kick_lo.bin
# Or manually:
python3 -c "
d = open('kick.rom','rb').read()
open('kick_hi.bin','wb').write(d[1::2])  # Odd bytes
open('kick_lo.bin','wb').write(d[0::2])  # Even bytes
"
```

---

## Verifying a ROM Image

```bash
# Verify checksum:
romtool info kick.rom | grep Checksum
# Expected: "Checksum: OK ($FFFFFFFF)"

# Verify size:
ls -la kick.rom
# Expected: 262144 (256 KB) or 524288 (512 KB)

# Quick checksum in Python:
python3 -c "
import struct
d = open('kick.rom','rb').read()
s = 0
for i in range(0, len(d), 4):
    v = struct.unpack('>I', d[i:i+4])[0]
    s += v
    if s >= 0x100000000:
        s = (s + 1) & 0xFFFFFFFF
print(f'Checksum: \${ s:08X}', '✓' if s == 0xFFFFFFFF else '✗ BAD')
"
```

---

## References

- NDK39: `exec/resident.h`, `exec/execbase.h`
- amitools: `romtool` — https://github.com/cnvogelg/amitools
- See also: [Cold Boot](cold_boot.md) — boot sequence using the ROM
- See also: [Kickstart Init](kickstart_init.md) — how residents are initialized
- See also: [Resident Modules](../06_exec_os/resident_modules.md) — RomTag structure
