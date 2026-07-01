[← Home](../README.md) · [Boot Sequence](README.md)

# Kickstart ROM — Internal Structure, Module Layout, Custom ROMs

## Overview

The Kickstart ROM is a single binary image containing the entire AmigaOS kernel — exec.library, graphics.library, dos.library, device drivers, system resources, and boot code. Understanding its internal structure is essential for ROM modding, FPGA core development, and reverse engineering. This document covers the binary layout, how modules are organized, how to extract and rebuild ROMs, and how to create custom Kickstart images.

---

## ROM Types

The Amiga's Kickstart ROM underwent significant evolution throughout the machine's lifespan, growing from a lean 256 KB firmware in the early days to a packed 512 KB kernel in the later 32-bit era. Understanding the physical constraints and memory mapping of these different versions is critical when modifying or swapping ROMs across different Amiga models. 

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

The Kickstart binary is not a filesystem; it is a meticulously structured, flat memory image. Because the 68000 CPU must boot directly from this address space, the ROM begins with hardcoded architectural vectors. Following this boot stub, the ROM is simply a sequential concatenation of resident modules (libraries and device drivers), bounded by a final checksum. 

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

Immediately following the CPU reset vectors sits the ROM Header. This 16-byte structure is the first piece of metadata that system diagnostics and expansion tools inspect to verify the integrity, size, and version of the OS payload.

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

### Physical ROM Interleaving (32-bit Architectures)

While a Kickstart ROM image (e.g., `kick31.rom`) is distributed as a single, contiguous 512 KB file, the physical reality on 32-bit Amigas (A1200, A3000, A4000) is different. 

The 68020/030/040 CPUs fetch instructions over a **32-bit data bus**. Because standard EPROMs of the era (like the 27C400 or 27C800) only have a **16-bit data bus**, the Amiga motherboard achieves 32-bit throughput by pairing two 16-bit ROM chips side-by-side and reading them simultaneously:
- **ROM 0 (U314 on A1200)**: Connected to data lines **D31–D16** (the upper 16 bits).
- **ROM 1 (U315 on A1200)**: Connected to data lines **D15–D0** (the lower 16 bits).

To make this work, the logical 512 KB Kickstart file must be **word-interleaved** (sometimes confusingly called "byteswapped") when burned to physical EPROMs. 
Since the image is just a linear sequence of 16-bit words, the split works like this:
- **Word 0** (offset `$0000`) goes to **ROM 0**
- **Word 1** (offset `$0002`) goes to **ROM 1**
- **Word 2** (offset `$0004`) goes to **ROM 0**
- **Word 3** (offset `$0006`) goes to **ROM 1**

When the CPU reads a 32-bit longword from `$F80000`, the hardware selects both chips. ROM 0 outputs Word 0 onto the high half of the bus, and ROM 1 outputs Word 1 onto the low half. The CPU sees the perfectly reassembled 32-bit longword.

When burning custom ROMs, modern EPROM programmers usually have an "Interleave" or "Word Split" function to handle this automatically. Alternatively, command-line tools like `srec_cat` can pre-split the single `.rom` file into `.hi` and `.lo` binary halves before burning.

### Checksum Complement

To ensure the ROM image is uncorrupted, the entire memory block is checksummed by the early boot code. However, instead of storing the final calculated sum, the ROM stores a **complement** value near its physical end. This clever design ensures that if you sum every 32-bit longword in the entire ROM (including the complement itself), the final mathematical result is always `0xFFFFFFFF`.

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

### How Exec Discovers and Initializes Modules

During the system cold start, `exec.library` (which is always the first module executed) scans the ROM address space looking for the `$4AFC` magic word that signifies a `RomTag`. To make this scan nearly instantaneous, `exec` uses the `rt_EndSkip` pointer: when it finds a valid `RomTag`, it reads the module's metadata, and then jumps its scanning pointer directly to the address contained in `rt_EndSkip`, skipping the entire body of the module.

As `exec` discovers valid modules, it sorts them into an array called `ResModules` based on their `rt_Pri` (Priority) and `rt_Version`. Higher priority modules will be initialized first. 

Once the ROM scan is complete, `exec` calls its internal `InitCode` function. This function iterates through the `ResModules` array and initializes each module by inspecting its `rt_Flags`.

#### The AUTOINIT Flag

If a module's `RomTag` does **not** have the `AUTOINIT` flag set, `exec` simply performs a `JMP` to the address specified in `rt_Init`, leaving the module to initialize itself entirely from scratch.

However, if the `AUTOINIT` flag **is** set (which is true for almost all standard libraries and devices), `exec` performs an elegant automated initialization:
1. It treats the `rt_Init` pointer not as code, but as a pointer to a structured initialization table (containing the library's size, its function vectors, and its data structure initializers).
2. `exec` automatically calls `MakeLibrary` on this table, dynamically allocating and populating the module's Base Structure in RAM.
3. `exec` then examines the module's `rt_Type` (e.g., `NT_LIBRARY` or `NT_DEVICE`) and automatically calls `AddLibrary`, `AddDevice`, or `AddResource` to permanently register the module in the system's public lists.

This means a developer can write a complete device driver or library in C or Assembly, set the `AUTOINIT` flag, and let the OS handle the memory allocation and list registration automatically.

### Kickstart 3.1 (40.068) Module Inventory

To illustrate the sheer density of the Kickstart ROM, below is the standard module inventory for AmigaOS 3.1. Notice how the core `exec.library` commands the highest priority to ensure it initializes the system lists before any other device attempts to register itself. Conversely, the `strap` module (the bootstrap that displays the insert disk screen) runs at a negative priority, guaranteeing it only executes after all hardware and filesystems have fully initialized.

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

For cross-platform development (macOS, Linux, Windows), the open-source `amitools` suite is the gold standard. Its `romtool` utility provides an elegant, non-destructive way to parse, split, and rebuild Kickstart ROMs directly from the command line.

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
# Rebuild:
romtool build modules/ custom_kick.rom
# romtool automatically:
#   1. Packs all modules sequentially (concatenating their binaries)
#   2. Ensures the $4AFC RomTag magic words remain word-aligned
#   3. Re-calculates and updates all rt_EndSkip pointers to span the concatenated binaries
#   4. Calculates and inserts the global checksum complement at the end of the ROM
#   5. Verifies the final image

# Verify:
romtool info custom_kick.rom
```

### Adding Custom Auto-Initializing Modules

If you write a custom module (e.g., a modern IDE driver or a new filesystem) and want it to be automatically loaded and initialized when the Amiga boots, you simply need to build it as a standard AmigaOS Resident Module.

1. **Structure your code:** Ensure your compiled binary begins with a valid `RomTag` structure (magic word `$4AFC`).
2. **Set the correct flags:** Set the `AUTOINIT` bit in `rt_Flags` and point `rt_Init` to your auto-init table so `exec` handles the `MakeLibrary`/`AddDevice` boilerplate.
3. **Choose a priority:** Set your `rt_Pri` carefully. If your module replaces a standard ROM module (like `scsi.device`), it must have a higher priority than the original so it initializes first and takes over the device name. If it's a completely new driver, standard priority (usually 0 to 50) is fine.
4. **Pack it into the ROM:** Add your compiled binary to the `romtool` build directory and list it in `index.txt`. When `romtool` builds the ROM, your module is physically appended. On the next boot, `exec`'s cold start scan will discover your `$4AFC` tag, add it to `ResModules`, and auto-initialize it.

#### Wrapping Disk-Based Devices (e.g., ehide.device)

Often, you will want to add a third-party driver to your ROM that was distributed as a standard AmigaDOS disk executable (Hunk format), such as the TerribleFire `ehide.device`. These files **do not have a RomTag** and contain relocations that must be resolved in RAM; they will crash if executed directly from the ROM address space.

To pack them into a Kickstart ROM, you must wrap them using a **ROM Wrapper** (often called a *RomHeader* or *RomModule* loader).

**How a ROM Wrapper works:**
1. The wrapper is a tiny snippet of assembly containing a valid `$4AFC` `RomTag`.
2. The original `ehide.device` file is embedded as a binary payload immediately following the wrapper.
3. During cold boot, `exec` finds the wrapper's `RomTag` and jumps to its `rt_Init` routine.
4. The wrapper's init routine allocates RAM (using `AllocMem`), unpacks the embedded Hunk payload into that RAM, applies all memory relocations (acting like a miniature `LoadSeg`), and finally jumps to the device's true initialization vector in RAM.

**Tools & Projects:**
* **Remus:** The Amiga-native GUI tool Remus has a built-in feature to wrap standard AmigaDOS executables. If you drag `ehide.device` into the build list, Remus automatically prepends a wrapper and pre-calculates relocations.
* **DoRom / RomModule:** Classic command-line utilities found on Aminet that take a disk-based `.device` and output a `.rom` module ready to be packed by `romtool`.
* **BlizKick / rommodule:** Toni Wilen and other developers have written standard open-source wrappers (often referred to as `rommodule`) originally designed for BlizKick and WinUAE, which are perfectly suited for building custom physical ROMs.

**Illustrative Wrapper Snippet:**
```m68k
RomTag:
        ; 1. Standard RomTag points to the loader
        DC.W    $4AFC           ; rt_MatchWord
        DC.L    RomTag          ; rt_MatchTag
        DC.L    EndSkip         ; rt_EndSkip
        DC.B    $81             ; rt_Flags (RTF_AUTOINIT | RTF_COLDSTART)
        DC.B    $25             ; rt_Version
        DC.B    $03             ; rt_Type (NT_DEVICE)
        DC.B    $40             ; rt_Pri (High priority to replace standard IDE)
        DC.L    NameString      ; "ehide.device"
        DC.L    IdString
        DC.L    InitRoutine     ; Jumps here on boot

InitRoutine:
        ; 2. Allocate RAM for the payload
        move.l  #PayloadSize, d0
        move.l  #MEMF_PUBLIC, d1
        jsr     _LVOAllocMem(a6)
        
        ; 3. Copy and relocate the embedded Hunk payload into RAM
        ; ... (Mini-LoadSeg logic goes here) ...

        ; 4. Jump to the uncompressed/relocated device init in RAM
        jmp     (a0)            

        ; 5. The actual ehide.device hunk executable payload is appended here
PayloadStart:
        INCBIN  "ehide.device"
EndSkip:
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

As the Amiga architecture evolved, the 512 KB `$F80000` space became too small to house all the necessary drivers—especially for specialized hardware like the CD32 console or the A4000T's SCSI controllers. Commodore solved this by mapping a secondary "Extension ROM" into the `$E00000` address space.

Some systems have a secondary ROM mapped at `$E00000`:

| System | Main ROM | Extension ROM |
|---|---|---|
| CD32 | `$F80000` (512 KB) | `$E00000` (512 KB) — CD filesystem, NVRAM |
| A4000T | `$F80000` (512 KB) | (None — all in main ROM) |
| A1000 | WCS (256 KB) | Loaded from floppy into WCS RAM |

## MapROM, WCS, and Shadow RAM Architectures

While modern Amiga users associate "MapROM" with accelerator cards speeding up ROM access or soft-loading custom Kickstart images, the concept of mapping a disk-loaded OS into RAM was actually invented by Commodore out of sheer necessity. 

### Historical Origins: A1000 and A3000

Commodore utilized RAM-mapped ROMs twice in the Amiga's history when hardware launch dates preceded the completion of the operating system:

1. **The Amiga 1000 WCS (1985):** The original Amiga 1000 shipped without a Kickstart ROM chip. Instead, it contained a tiny 8KB boot ROM and 256KB of dedicated RAM called the **Writable Control Store (WCS)**. When powered on, the boot ROM prompted the user for a Kickstart floppy disk. It loaded the 256KB OS into the WCS RAM, triggered a hardware register to write-protect that RAM, and mapped it to the ROM address space (`$FC0000`). This allowed Commodore to ship the A1000 while Kickstart 1.0/1.1 was still heavily in beta.
2. **The Amiga 3000 "SuperKickstart" (1990):** When the Amiga 3000 was ready to launch, AmigaOS 2.0 was not finished. Commodore shipped early A3000s with physical **Kickstart 1.4** ROMs. These were not a complete OS; they were essentially a bootloader. Kickstart 1.4 read a file named `DEVS:kickstart` (containing OS 1.3 or a 2.0 beta) from the hard drive into Fast RAM. It then used the 68030 processor's internal **MMU (Memory Management Unit)** to transparently map that Fast RAM to the `$F80000` ROM address space. 

It was only later that third-party accelerator manufacturers (like Phase5 and Apollo) co-opted and branded this concept as **"MapROM"**, realizing it was the perfect solution for both overcoming the 16-bit physical ROM speed bottleneck and allowing users to upgrade to Kickstart 3.1 without buying physical chips.

### Why Accelerators Use MapROM

Because the physical Kickstart ROMs on the Amiga motherboard reside on a relatively slow 16-bit data bus (even on 32-bit machines, ROM access is significantly slower than Fast RAM), executing OS routines directly from ROM creates a bottleneck. MapROM solves this by copying the Kickstart image into fast 32-bit RAM, and redirecting all CPU reads for the ROM address space (`$F80000`) to that RAM.

### How the Remap Physically Happens

The Amiga must always begin its initial power-on sequence using the physical ROM chips, because the MapROM redirect is not yet active. The remap happens in a multi-stage process:

1. **Cold Boot:** The Amiga powers on. The CPU fetches its initial PC from the physical ROM chips at `$F80000` and boots normally.
2. **Image Loading:** During `S:Startup-Sequence` (or manually in a shell), a MapROM tool (e.g., `BlizKick`, `MuMapROM`, or `CPU FASTROM`) is executed. The tool allocates 512KB of Fast RAM and copies either the physical ROM (for a speed boost) or a `.rom` file from disk into this RAM buffer.
3. **The Redirect:** The tool activates the redirection using one of two methods:
   - **Hardware MapROM:** Accelerators with a dedicated memory controller (like Phase5 Blizzards) have a specific hardware register. When toggled, the accelerator's logic physically intercepts any CPU bus accesses to `$F80000` and routes them directly to a dedicated 512KB slice of Fast RAM on the card.
   - **MMU MapROM:** Tools like `MuMapROM` configure the 68030/040/060 Memory Management Unit (MMU). The MMU translation table is updated so that logical accesses to `$F80000` are translated in silicon to the physical address of the allocated Fast RAM. The MMU page is marked as Cacheable and Read-Only.
4. **The Reset:** Once the redirect is configured, the tool triggers a system reset (often a "warm" soft-reset via CPU instruction, or triggering the chipset reset line). 
5. **Execution:** The CPU resets and fetches the initial PC from `$F80000`. Because the Hardware MapROM latch or the specific MMU configuration is designed to *survive* a soft reset, the CPU is now reading from the Fast RAM copy. `exec.library` boots identically to a cold start, but executes entirely from the mapped image.

### Reset Survival and Limitations

* **Soft Resets (Ctrl-A-A):** Hardware MapROM implementations usually survive a keyboard reset because the accelerator's CPLD retains the register state. MMU implementations often drop the MMU tables on a keyboard reset unless a resident program traps the reset vector to restore the MMU state immediately.
* **Cold Resets (Power Cycle):** No MapROM implementation survives a power cycle. The machine will always fall back to the physical ROMs on a cold boot.
* **Auto-Mapping:** Some accelerators have their own small boot ROM on the card (acting as an expansion device) that can automatically intercept the boot sequence, copy the physical ROM to RAM, and engage Hardware MapROM before DOS even loads.

### 1 MB Custom ROM Images

Modern Amiga enthusiasts often exhaust the standard 512 KB limit when trying to pack third-party filesystems (like PFS3), updated SCSI/IDE drivers (like `ehide.device`), and patched `icon.library` files into a custom Kickstart. 

To bypass this limit, modders can construct massive 1 MB custom ROM images. This is achieved by combining the primary 512 KB Kickstart with a custom 512 KB Extension ROM. When burned to a 1 MB EPROM (like the 27C800) or a modern Flash adapter, the Amiga effortlessly boots the main kernel from `$F80000` and then auto-discovers the extra drivers housed in the `$E00000` space.

```
$E00000–$E7FFFF: Extension ROM (512 KB)
$F80000–$FFFFFF: Main Kickstart (512 KB)
```

Tools like Remus and Capitoline can effortlessly build these combined 1 MB images.

---

## Burning Physical ROMs

Once you have meticulously crafted and verified a custom Kickstart image using tools like `romtool`, the final frontier is migrating that binary out of the digital realm and into physical silicon. Burning Amiga ROMs requires selecting the correct EPROM type that matches your motherboard's socket specifications, and—crucially—interleaving the data correctly if you are targeting a 32-bit machine.

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

- AmigaOS NDK 3.1 / 3.2: `exec/resident.h`, `exec/execbase.h`
- amitools: `romtool` — https://github.com/cnvogelg/amitools
- See also: [Cold Boot](cold_boot.md) — boot sequence using the ROM
- See also: [Kickstart Boot Diagnostics](kickstart-boot-diagnostics.md) — ROM checksum algorithm, CC_BADROMSUM red screen
- See also: [Kickstart Init](kickstart_init.md) — how residents are initialized
- See also: [Resident Modules](../06_exec_os/resident_modules.md) — RomTag structure
omTag structure
