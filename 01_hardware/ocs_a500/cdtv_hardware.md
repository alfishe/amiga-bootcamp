[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# CDTV — Platform Hardware

## Overview

The **Commodore Dynamic Total Vision** (CDTV, 1991) is an A500-class OCS computer packaged as a consumer CD-ROM set-top box. Internally it uses the same Agnus/Denise/Paula chipset as the A500, but adds several unique subsystems:

1. **DMAC + WD33C93 SCSI controller** — drives the internal CD-ROM via DMA
2. **Extended ROM** — 512 KB of additional firmware for CD filesystem and player software
3. **NVRAM** — 64 KB battery-backed non-volatile storage
4. **IR remote receiver** — proprietary 40 kHz infrared protocol
5. **Real-Time Clock** — Oki MSM6242B at `$DC0000`

The CDTV has **no keyboard** (optional external), **no internal floppy** (optional external), and **no expansion slots** visible to the end user. It targets the living room, not the desktop.

## System Specifications

| Parameter | Value |
|---|---|
| CPU | 68000 @ 7.09 MHz (PAL) / 7.16 MHz (NTSC) |
| Chipset | OCS (Agnus 8361/8367, Denise 8362, Paula 8364) |
| Chip RAM | 1 MB (expandable to 2 MB with Super Agnus mod) |
| Fast RAM | None stock |
| ROM | 256 KB Kickstart 1.3 + 512 KB Extended ROM |
| CD-ROM | Single-speed (1×), SCSI-based via DMAC/WD33C93 |
| Audio | 4-channel Paula DMA + CD-DA passthrough |
| Video | Composite, S-Video, RF (no RGB without mod) |
| Controller | IR remote, optional external keyboard |
| Storage | CD-ROM, 64 KB NVRAM |

## Address Map — CDTV-Specific Regions

The standard OCS 24-bit address map applies. The CDTV adds these regions:

| Address Range | Size | Region |
|---|---|---|
| `$DC0000`–`$DC003F` | 64 B | Real-Time Clock (Oki MSM6242B) |
| `$E00000`–`$E3FFFF` | 256 KB | Extended ROM bank 1 (CD filesystem, player UI) |
| `$E40000`–`$E7FFFF` | 256 KB | Extended ROM bank 2 (DMAC driver, boot logic) |
| `$E90000`–`$E9FFFF` | 64 KB | DMAC registers (WD33C93 SCSI DMA controller) |
| `$F00000`–`$F3FFFF` | 256 KB | NVRAM (battery-backed, 64 KB actual usable) |

See also: [Address Space](../common/address_space.md) — full 24-bit map with CDTV-specific entries.

---

## DMAC and WD33C93 SCSI Controller

### Architecture

The CDTV's CD-ROM is connected via a **SCSI bus** — the same architecture used in the A2091 and A590 hard drive controllers. The system uses two chips:

| Chip | Role |
|---|---|
| **DMAC** (Commodore custom) | DMA controller — transfers data between the WD33C93 and Amiga memory |
| **WD33C93** (Western Digital) | SCSI Bus Interface Controller (SBIC) — handles SCSI protocol with the CD-ROM drive |

This is fundamentally different from the CD32, where Akiko handles CD-ROM control directly via PIO.

### DMAC Register Map

The DMAC is mapped at `$E90000`:

| Offset | Register | R/W | Description |
|---|---|---|---|
| `$E90000` | `DAWR` | W | DMAC address write (DMA destination) |
| `$E90002` | `WTCH` | W | Word Transfer Count High |
| `$E90004` | `CNTR` | RW | Control register (DMA direction, interrupt enable) |
| `$E90040` | `ACR_H` | W | Address Counter Register high word |
| `$E90042` | `ACR_L` | W | Address Counter Register low word |
| `$E90048` | `ST_DMA` | W | Start DMA transfer (write any value) |
| `$E9004A` | `FLUSH` | W | Flush DMA FIFO |
| `$E9004C` | `CINT` | W | Clear DMAC interrupt |
| `$E9004E` | `ISTR` | R | Interrupt Status Register |
| `$E90090` | `SASR` | W | WD33C93 Address/Select Register |
| `$E90091` | `SCMD` | RW | WD33C93 Data Register (read/write SBIC registers) |

### WD33C93 SBIC Registers

The WD33C93 is accessed indirectly through the DMAC. Write the target register number to `SASR` (`$E90090`), then read/write data via `SCMD` (`$E90091`):

| Register | Name | Description |
|---|---|---|
| `$00` | Own ID | SCSI initiator ID (typically 7) |
| `$01` | Control | DMA mode, interrupt enables |
| `$02` | Timeout | Selection timeout period |
| `$03`–`$0B` | CDB | Command Descriptor Block (SCSI command bytes) |
| `$0F` | Command | SCSI command register (initiate bus phases) |
| `$10` | Data | Data transfer register (PIO mode) |
| `$17` | Status | SCSI bus phase and completion status |

### SCSI Commands for CD-ROM

The CD-ROM drive responds to standard SCSI-2 commands:

| Command | Opcode | Use |
|---|---|---|
| `TEST UNIT READY` | `$00` | Check drive presence |
| `READ(6)` | `$08` | Read data sectors (Mode 1) |
| `READ(10)` | `$28` | Read data sectors (extended addressing) |
| `READ TOC` | `$43` | Read Table of Contents |
| `PLAY AUDIO(10)` | `$45` | Play CD-DA audio tracks |
| `PAUSE/RESUME` | `$4B` | Pause/resume audio playback |
| `READ SUB-CHANNEL` | `$42` | Read current position, ISRC, UPC/EAN |

### AmigaOS Access

Under AmigaOS, the CD-ROM is accessed through `scsi.device` loaded from Extended ROM:

```
Application → dos.library → cdfs (CD filesystem handler) → scsi.device → DMAC → WD33C93 → CD-ROM
```

---

## Extended ROM

The CDTV includes **512 KB of additional ROM** mapped at `$E00000`–`$E7FFFF`, split across two 256 KB banks. This ROM contains:

| Bank | Address Range | Contents |
|---|---|---|
| Bank 1 | `$E00000`–`$E3FFFF` | CD filesystem (CDFS), audio player UI, bookmark manager |
| Bank 2 | `$E40000`–`$E7FFFF` | DMAC/WD33C93 device driver (`scsi.device`), boot sequence, system initialization |

The Extended ROM is **not present** on standard A500/A2000 machines. Software that detects CDTV typically checks for the presence of `cdtv.device` or reads the Extended ROM base.

### Boot Sequence

1. Kickstart 1.3 loads from ROM (`$F80000`)
2. Extended ROM at `$E00000` is detected and initialized
3. `scsi.device` from Extended ROM initializes DMAC + WD33C93
4. CD-ROM drive is probed for a bootable disc
5. If a valid Amiga boot block is found on the CD → boot from CD
6. If no CD → fall through to standard floppy boot (if external floppy present)

---

## NVRAM (Non-Volatile Storage)

### Hardware

The CDTV includes **64 KB of battery-backed SRAM** mapped at `$F00000`–`$F3FFFF`. This is fundamentally different from the CD32's tiny serial EEPROM — the CDTV has substantially more storage.

| Parameter | Value |
|---|---|
| Type | Battery-backed SRAM |
| Capacity | 64 KB (512 Kbit) |
| Address | `$F00000`–`$F0FFFF` (64 KB usable within 256 KB window) |
| Persistence | Battery-backed (internal lithium cell) |
| Access | Direct memory-mapped (byte-addressable) |
| Typical use | Bookmarks, game saves, user preferences |

### Access

Unlike the CD32's I²C EEPROM, CDTV NVRAM is **directly memory-mapped** — the CPU reads and writes it like normal RAM:

```asm
; Read a byte from NVRAM
    move.b  $F00000, d0         ; read first byte of NVRAM

; Write a byte to NVRAM
    move.b  d0, $F00000         ; write to NVRAM — persists across power cycles
```

### AmigaOS Interface

The CDTV provides `bookmark.device` for structured NVRAM access:

```c
/* CDTV bookmark access — stores named data blocks in NVRAM */
struct IOStdReq *io;
/* ... open bookmark.device ... */
io->io_Command = CMD_WRITE;
io->io_Data    = save_data;
io->io_Length  = data_length;
DoIO((struct IORequest *)io);
```

---

## Infrared Remote Controller

### Hardware

The CDTV includes a dedicated IR receiver module and ships with a full remote control unit. The remote provides media playback buttons, a numeric keypad, and navigation controls.

### Protocol

The CDTV uses a **proprietary IR protocol** (not NEC, not RC-5):

| Parameter | Value |
|---|---|
| Carrier frequency | 40 kHz |
| Frame size | 12-bit command + 12-bit inverted (24-bit total) |
| Header | 9 ms pulse + 4.5 ms space |
| Bit encoding | 400 µs pulse + variable space (400 µs = 0, 1200 µs = 1) |
| Repeat | 9 ms pulse + 2.1 ms space + 400 µs end (every ~60 ms) |
| Receiver | Dedicated module tuned for 40 kHz (TSOP38240 compatible) |

### Button Mapping

| Button | Code | Function |
|---|---|---|
| Play/Pause | `$01` | Media playback toggle |
| Stop | `$02` | Stop playback |
| Forward | `$03` | Next track / fast forward |
| Rewind | `$04` | Previous track / rewind |
| Vol+ | `$05` | Volume up |
| Vol− | `$06` | Volume down |
| 0–9 | `$10`–`$19` | Numeric keypad |
| Enter | `$1A` | Confirm / select |
| Escape | `$1B` | Cancel / back |
| Up/Down/Left/Right | `$1C`–`$1F` | Navigation |
| A / B | `$20` / `$21` | Assignable (game buttons) |

> [!NOTE]
> The IR receiver connects to the system as a keyboard-like input device. AmigaOS treats remote button presses as `IECLASS_RAWKEY` input events with dedicated qualifier codes. Standard `input.device` handlers receive these events transparently.

---

## Real-Time Clock

The CDTV includes an **Oki MSM6242B** RTC chip at `$DC0000`:

| Address | Register | Description |
|---|---|---|
| `$DC0001` | Seconds (units) | BCD 0–9 |
| `$DC0003` | Seconds (tens) | BCD 0–5 |
| `$DC0005` | Minutes (units) | BCD 0–9 |
| `$DC0007` | Minutes (tens) | BCD 0–5 |
| `$DC0009` | Hours (units) | BCD 0–9 |
| `$DC000B` | Hours (tens) | BCD 0–2 |
| `$DC000D` | Day (units) | BCD 0–9 |
| `$DC000F` | Day (tens) | BCD 0–3 |
| `$DC0011` | Month (units) | BCD 0–9 |
| `$DC0013` | Month (tens) | BCD 0–1 |
| `$DC0015` | Year (units) | BCD 0–9 |
| `$DC0017` | Year (tens) | BCD 0–9 |
| `$DC0019` | Day of week | 0–6 |
| `$DC001B` | Control D | AM/PM, 12/24 mode |
| `$DC001D` | Control E | IRQ enable, test |
| `$DC001F` | Control F | Reset, busy flag |

> [!NOTE]
> The same MSM6242B RTC is used in the A2000 and A3000. The register layout is identical across all models.

---

## CDTV vs A500 — Hardware Comparison

| Feature | A500 | CDTV |
|---|---|---|
| CPU | 68000 @ 7.09 MHz | 68000 @ 7.09 MHz |
| Chipset | OCS | OCS (identical) |
| Chip RAM | 512 KB–1 MB | 1 MB |
| ROM | 256 KB Kickstart | 256 KB Kickstart + **512 KB Extended ROM** |
| Storage | Internal floppy (880 KB) | **CD-ROM** (1×, 680 MB) + 64 KB NVRAM |
| Input | Keyboard + mouse + joystick | **IR remote** + optional ext. keyboard |
| Audio | Paula 4-channel | Paula + **CD-DA passthrough** |
| Video output | RGB (DB23) | Composite, S-Video, RF |
| Expansion | Trapdoor + side | None visible (internal A2000-compatible) |
| RTC | None stock (add-on) | **Oki MSM6242B** |

### Software Compatibility

The CDTV runs standard AmigaOS 1.3 software from CD or external floppy. The Extended ROM adds CD-specific functionality but does not break compatibility. Most A500 games work unmodified when loaded from compatible media.

## References

- Commodore CDTV Technical Reference Manual (internal)
- WD33C93 SCSI Bus Interface Controller datasheet (Western Digital)
- Oki MSM6242B Real-Time Clock datasheet
- WinUAE source: CDTV emulation code (Toni Wilen)
- [Big Book of Amiga Hardware — CDTV](https://bigbookofamigahardware.com/)
- ADCD 2.1: `scsi.device` Autodocs

## See Also

- [OCS Chipset](chipset_ocs.md) — Agnus/Denise/Paula (shared with CDTV)
- [Memory Types](../common/memory_types.md) — CDTV memory configuration
- [Address Space](../common/address_space.md) — CDTV address map with Extended ROM and NVRAM regions
- [CIA Chips](../common/cia_chips.md) — CIA A/B (shared across all models)
