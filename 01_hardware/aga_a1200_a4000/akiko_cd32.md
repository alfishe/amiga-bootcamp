[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# Akiko — CD32 Custom Chip

## Overview

The **Akiko** chip is a custom ASIC unique to the Amiga CD32 game console (1993). It sits alongside the standard AGA chipset (Alice + Lisa + Paula) and provides three subsystems that exist in no other Amiga model:

1. **Chunky-to-Planar (C2P) conversion** — hardware-accelerated pixel format conversion
2. **CD-ROM controller** — drives the internal double-speed CD-ROM
3. **NVRAM interface** — I²C controller for the onboard serial EEPROM

Akiko is mapped at base address **`$B80000`** and occupies a 32 KB window (`$B80000`–`$B87FFE`).

## Chip Identification

Reading a longword from `$B80000` returns the Akiko ID:

```asm
    move.l  $B80000, d0     ; d0 = $C0CACAFE if Akiko present
    cmp.l   #$C0CACAFE, d0
    beq     .has_akiko
```

> [!NOTE]
> On non-CD32 machines, reading `$B80000` will return bus noise or trigger a bus error. Always wrap Akiko detection in an exception handler or use `graphics.library` v40+ `WriteChunkyPixels()` which auto-detects Akiko internally.

## Register Map

| Offset | Name | R/W | Description |
|---|---|---|---|
| `$B80000` | `AKIKO_ID` | R | Chip ID — returns `$C0CACAFE` |
| `$B80002` | `AKIKO_REV` | R | Silicon revision |
| `$B80004` | `AKIKO_INTREQ` | R | Interrupt request (CD subcode, C2P done) |
| `$B80008` | `AKIKO_INTENA` | RW | Interrupt enable mask |
| `$B80010` | `CDROM_PBXSTAT` | RW | CD-ROM PIO buffer/status |
| `$B80014` | `CDROM_FLAGS` | RW | CD-ROM control flags |
| `$B80018` | `CDROM_TXDATA` | W | CD-ROM command transmit |
| `$B8001C` | `CDROM_RXDATA` | R | CD-ROM response receive |
| `$B80020` | `CDROM_SUBCDATA` | R | CD subcode (Q-channel) data |
| `$B80024` | `NVRAM_CTRL` | RW | NVRAM I²C control (SCL/SDA direction) |
| `$B80028` | `NVRAM_DATA` | RW | NVRAM I²C data (SCL/SDA bit-bang) |
| `$B80030` | `C2P_INPUT` | W | Chunky-to-Planar input register (longword) |
| `$B80030` | `C2P_OUTPUT` | R | Chunky-to-Planar output register (longword) |

> [!IMPORTANT]
> The register map above is reverse-engineered from WinUAE (`akiko.cpp`) and community hardware testing. Commodore never published an official Akiko datasheet.

---

## Chunky-to-Planar (C2P) Conversion

### The Problem

The AGA chipset uses **planar** graphics — each bitplane is a separate contiguous block of memory. But most game engines (especially PC ports) render in **chunky** format — one byte per pixel in a linear framebuffer. Converting between these formats is computationally expensive on the 68020.

### How Akiko C2P Works

Akiko converts **32 chunky pixels** (8-bit each) into **8 bitplane longwords** in hardware. The CPU must feed data in and read results out — Akiko has **no DMA**; it is a register-based pipeline.

#### Conversion Protocol

```
Input:  8 longwords of chunky data  (4 pixels × 8 = 32 pixels)
Output: 8 longwords of planar data  (1 longword per bitplane × 8 planes)
```

**Step 1 — Write 8 longwords of chunky pixels:**

```asm
; a0 = source chunky buffer (32 pixels = 32 bytes, read as 8 longwords)
; Each longword contains 4 consecutive 8-bit pixels: [P0|P1|P2|P3]

    lea     $B80030, a1         ; C2P input register
    move.l  (a0)+, (a1)         ; pixels 0–3
    move.l  (a0)+, (a1)         ; pixels 4–7
    move.l  (a0)+, (a1)         ; pixels 8–11
    move.l  (a0)+, (a1)         ; pixels 12–15
    move.l  (a0)+, (a1)         ; pixels 16–19
    move.l  (a0)+, (a1)         ; pixels 20–23
    move.l  (a0)+, (a1)         ; pixels 24–27
    move.l  (a0)+, (a1)         ; pixels 28–31
```

**Step 2 — Read 8 longwords of planar output:**

```asm
; a2 = destination planar buffer (8 bitplanes × 4 bytes = 32 bytes)

    lea     $B80030, a1         ; C2P output register (same address, read mode)
    move.l  (a1), (a2)+         ; bitplane 0 (32 pixels, 1 bit each)
    move.l  (a1), (a2)+         ; bitplane 1
    move.l  (a1), (a2)+         ; bitplane 2
    move.l  (a1), (a2)+         ; bitplane 3
    move.l  (a1), (a2)+         ; bitplane 4
    move.l  (a1), (a2)+         ; bitplane 5
    move.l  (a1), (a2)+         ; bitplane 6
    move.l  (a1), (a2)+         ; bitplane 7
```

#### Optimised Loop (MOVEM)

In practice, the entire 32-pixel conversion is done with two MOVEM instructions:

```asm
; Convert 32 chunky pixels → 8 planar longwords
; a0 = chunky source, a2 = planar dest
; a1 = $B80030 (Akiko C2P register)

    movem.l (a0)+, d0-d7        ; load 32 chunky pixels (8 longwords)
    movem.l d0-d7, (a1)         ; write to Akiko C2P input
    movem.l (a1), d0-d7         ; read 8 planar longwords from Akiko
    movem.l d0-d7, (a2)         ; store to bitplane memory
    lea     32(a2), a2          ; advance planar pointer
```

> [!WARNING]
> MOVEM to a fixed address writes all registers to the **same** address (FIFO-style), which is exactly what Akiko expects. This only works because `$B80030` is a hardware register, not normal RAM.

#### Full-Screen Conversion Example

For a 320×256 screen at 8 bitplanes (256 colours):

```asm
; Total pixels = 320 × 256 = 81,920
; Each pass converts 32 pixels → 81,920 / 32 = 2,560 passes

    lea     chunky_buffer, a0
    lea     planar_buffer, a2
    lea     $B80030, a1
    move.l  #2560-1, d7         ; loop counter

.c2p_loop:
    movem.l (a0)+, d0-d6/a3     ; 8 longwords (use a3 for 8th reg)
    movem.l d0-d6/a3, (a1)      ; write to Akiko
    movem.l (a1), d0-d6/a3      ; read planar output
    movem.l d0-d6/a3, (a2)
    lea     32(a2), a2
    dbf     d7, .c2p_loop
```

### Performance Characteristics

| Metric | Value |
|---|---|
| Pixels per pass | 32 |
| CPU cycles per pass | ~80–100 (68020 @ 14 MHz) |
| Throughput | ~1.5 MB/s (register I/O bound) |
| 320×256×8bpp full screen | ~54 ms (~18 fps standalone) |

#### When to Use Akiko C2P

| Scenario | Recommendation |
|---|---|
| Stock CD32 (68020, Chip RAM only) | **Use Akiko** — significantly faster than CPU-only C2P |
| CD32 + SX-32 with 68030 + Fast RAM | Benchmark both — software C2P may match Akiko |
| CD32 + 68040/060 accelerator | **Use software C2P** — CPU is 5–10× faster than Akiko's throughput |

### AmigaOS Interface

OS-compliant applications use `WriteChunkyPixels()` from `graphics.library` v40+:

```c
#include <graphics/gfx.h>

/* graphics.library auto-detects Akiko and uses it if present */
WriteChunkyPixels(
    rp,             /* RastPort */
    xstart, ystart, /* top-left corner */
    xstop, ystop,   /* bottom-right corner */
    chunky_array,   /* source chunky pixel data */
    bytes_per_row   /* chunky buffer pitch */
);
```

---

## CD-ROM Controller

### Hardware

The CD32 contains a **Philips/Sony double-speed (2×) CD-ROM** drive. Unlike the CDTV (which uses a SCSI-based controller via DMAC/WD33C93), the CD32's CD-ROM is controlled **directly by Akiko** through a proprietary PIO interface.

### Drive Capabilities

| Feature | Specification |
|---|---|
| Speed | 2× (300 KB/s data, 150 KB/s audio) |
| Media | CD-ROM (Mode 1/2), CD-DA, Mixed Mode |
| Seek | ~400 ms average |
| Interface | Akiko PIO (no SCSI, no IDE) |

### CD-ROM Register Protocol

Communication with the drive is command/response based through the Akiko registers:

1. **Write command bytes** to `CDROM_TXDATA` (`$B80018`)
2. **Poll status** via `CDROM_PBXSTAT` (`$B80010`) for response availability
3. **Read response bytes** from `CDROM_RXDATA` (`$B8001C`)
4. **Read subcode** from `CDROM_SUBCDATA` (`$B80020`) for TOC/position data

### Boot from CD

The CD32 boots exclusively from CD-ROM (no floppy drive). The boot sequence:

1. Kickstart 3.1 initialises from ROM (`$F80000`)
2. Extended ROM at `$E00000` provides `cd.device` and the CD filesystem
3. Akiko initialises the CD-ROM drive
4. The system reads the TOC and looks for a boot block (Amiga executable format)
5. If found, the boot executable is loaded and run — this is the game/application entry point

> [!NOTE]
> CD32 game discs use standard ISO 9660 with Amiga-specific boot blocks. Many titles also include CD-DA audio tracks for music, played via Akiko's CDDA passthrough.

---

## NVRAM (Non-Volatile Storage)

### Hardware

The CD32 includes a **1 Kbit (128 bytes) serial EEPROM** (typically a 93C46 or compatible) accessed via I²C bit-banging through Akiko registers.

| Parameter | Value |
|---|---|
| Type | Serial EEPROM (I²C / Microwire) |
| Capacity | 1 Kbit (128 bytes usable) |
| Interface | Akiko bit-bang (SCL/SDA via `$B80024`/`$B80028`) |
| Persistence | Battery-backed (CR2032) |
| Typical use | Game saves, system preferences, high scores |

### Access Protocol

NVRAM access requires bit-banging the I²C clock (SCL) and data (SDA) lines through Akiko registers:

```asm
; Simplified NVRAM byte read
; d0 = address (0–127)

    ; Set SDA as output, clock high
    move.l  #$01, $B80024       ; NVRAM_CTRL: configure direction
    
    ; Send device address + read command via bit-bang
    ; (full protocol requires start condition, address bits, ack)
    
    ; Clock in 8 data bits
    moveq   #7, d1
.read_bit:
    bset    #0, $B80028         ; SCL high
    move.l  $B80028, d2         ; read SDA
    bclr    #0, $B80028         ; SCL low
    roxl.b  #1, d0              ; shift bit into result
    dbf     d1, .read_bit
```

### AmigaOS NVRAM Access

The OS provides `nonvolatile.library` for structured NVRAM access:

```c
#include <libraries/nonvolatile.h>

/* Store data */
StoreNV("MyGame", "SaveSlot1", save_data, data_length, TRUE);

/* Retrieve data */
APTR data = GetNV("MyGame", "SaveSlot1", TRUE);
```

---

## CD32 Expansion Options

The CD32 has **no standard expansion slots** (no Zorro, no CPU slot, no trapdoor, no PCMCIA). Third-party units connect via the rear expansion port:

### SX-1 (Paravision)

| Feature | Specification |
|---|---|
| Memory | 1× 72-pin SIMM (1–8 MB Fast RAM) |
| Storage | Internal 44-pin IDE (2.5" HDD) + external DB37 IDE |
| I/O | Parallel (DB25), Serial (9-pin RS232), RGB video (DB23) |
| Keyboard | AT-101 connector |
| Floppy | External DB23 floppy connector |
| Other | RTC (CR2032), FMV pass-through, disable switch |

### SX-32 / SX-32 Pro (DCE)

| Feature | Specification |
|---|---|
| Memory | 1× 72-pin SIMM (up to 8 MB) |
| Storage | Internal 44-pin IDE |
| I/O | Parallel (DB25), Serial (DB25), RGB (DB23), VGA (HD15) |
| CPU upgrade | SX-32 Pro includes 68030 socket |
| Other | RTC, external floppy |

### FMV Module (Commodore)

| Feature | Specification |
|---|---|
| Function | MPEG-1 video + audio decoder (Video CD playback) |
| Video chip | C-Cube CL450 MPEG decoder |
| Audio chip | LSI Logic audio decoder |
| Limitation | Caps system Fast RAM at 4 MB |
| Compatibility | Works with SX-1 (pass-through); **incompatible** with SX-32 |

> [!WARNING]
> The FMV module had four hardware revisions. Early revisions (rev 1–2) are prone to overheating. If sourcing one today, look for rev 3 or later.

---

## CD32 vs A1200 — Hardware Comparison

The CD32 is often described as "an A1200 in a console shell." The chipset is identical, but the system-level hardware differs significantly:

| Feature | A1200 | CD32 |
|---|---|---|
| CPU | 68EC020 @ 14 MHz | 68EC020 @ 14 MHz |
| Custom chips | Alice + Lisa + Paula | Alice + Lisa + Paula + **Akiko** |
| Chip RAM | 2 MB | 2 MB |
| Chipset | AGA | AGA |
| Storage | IDE (Gayle), Floppy | **CD-ROM (Akiko)**, no floppy |
| Expansion | Trapdoor (150-pin), PCMCIA | Rear port only (SX-1/SX-32) |
| Keyboard | Built-in | None (requires SX-1/SX-32) |
| Controller | Atari-style DB9 joystick | **CD32 gamepad** (7-button protocol) |
| NVRAM | None | **128 bytes EEPROM** (Akiko) |
| Gayle | Yes (IDE, PCMCIA) | **No** — Akiko replaces storage functions |
| C2P hardware | No | **Yes** (Akiko) |
| Boot media | Floppy / HDD | CD-ROM only |

### CD32 Gamepad Protocol

The CD32 gamepad uses a serial shift-register protocol through the standard DB9 controller port, providing 7 buttons:

| Button | Bit | Accent |
|---|---|---|
| Blue (Play) | 0 | Fire 1 / primary action |
| Red (Rewind) | 1 | Fire 2 / secondary |
| Yellow (FF) | 2 | Fire 3 |
| Green (Stop) | 3 | Fire 4 |
| Right shoulder | 4 | Shoulder R |
| Left shoulder | 5 | Shoulder L |
| Pause | 6 | Start/Pause |

Detection: the CD32 pad responds to a clock signal on pin 5 of the joystick port. Standard Atari-style joysticks ignore this signal and remain compatible.

---

## Detecting CD32 at Runtime

```c
#include <exec/execbase.h>

/* Method 1: Check Akiko ID register (hardware-level) */
BOOL has_akiko(void)
{
    volatile ULONG *akiko_id = (ULONG *)0xB80000;
    /* Wrap in exception handler — bus error on non-CD32 */
    return (*akiko_id == 0xC0CACAFE);
}

/* Method 2: Check for CD32 via expansion.library (safer) */
#include <libraries/configvars.h>
#include <clib/expansion_protos.h>

BOOL is_cd32(void)
{
    /* Akiko autoconfig: manufacturer 0x0202, product 0x3E */
    struct ConfigDev *cd = FindConfigDev(NULL, 0x0202, 0x3E);
    return (cd != NULL);
}
```

## References

- WinUAE source: `akiko.cpp` — reverse-engineered register definitions (Toni Wilen)
- Commodore CD32 Technical Reference (internal, partial — never publicly released)
- NDK39: `graphics/gfx.h` — `WriteChunkyPixels()` prototype
- NDK39: `libraries/nonvolatile.h` — NVRAM access API
- [Big Book of Amiga Hardware — CD32](https://bigbookofamigahardware.com/)
- English Amiga Board (EAB) — CD32 hardware discussions

## See Also

- [AGA Chipset Internals](chipset_aga.md) — Alice and Lisa (shared with CD32)
- [Memory Types](../common/memory_types.md) — CD32 memory configuration
- [Address Space](../common/address_space.md) — CD32 address map with Akiko region
