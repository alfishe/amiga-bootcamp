[← Home](../../README.md) · [Hardware](../README.md)

# OCS Chipset — A500 / A1000 / A2000

## Overview

The **Original Chip Set** (OCS) ships in the Amiga 1000 (1985), A500 (1987), and early A2000 boards. It consists of three custom chips: **Agnus**, **Denise**, and **Paula**, supported by the MOS 8520 CIA pair.

## Chip Summary

| Chip | MOS Part | Primary Responsibilities |
|---|---|---|
| **Agnus** | 8361 (PAL), 8367 (NTSC) | DMA controller, Copper coprocessor, Blitter, address generation |
| **Denise** | 8362 | Display: bitplane fetch decode, sprite decode, colour output |
| **Paula** | 8364 | Audio DMA (4 channels), floppy disk I/O, serial port, interrupts |

## Contents

| File | Topic |
|---|---|
| [chipset_ocs.md](chipset_ocs.md) | Chip internals, DMA priorities, bus arbitration |
| [custom_registers.md](custom_registers.md) | Full OCS register map $DFF000–$DFF1FE |
| [copper.md](copper.md) | Copper coprocessor: WAIT/SKIP/MOVE, copperlist format |
| [blitter.md](blitter.md) | Blitter: channels A/B/C/D, minterms, line mode, fill |
| [paula_audio.md](paula_audio.md) | Audio DMA: AUDxLCH/LCL/LEN/PER/VOL, interrupt |
| [paula_serial.md](paula_serial.md) | Serial port: SERPER/SERDATR, baud rate |
| [sprites.md](sprites.md) | Hardware sprites: SPRxPTH, control words, attach mode |
| [cdtv_hardware.md](cdtv_hardware.md) | CDTV platform: DMAC, CD-ROM, IR remote, NVRAM |

---

## OCS Machines — Per-Model Details

### A1000 (1985) — Writable Control Store

The A1000 is the original Amiga. Its most distinctive feature is the **Writable Control Store (WCS)** — Kickstart is loaded from floppy into RAM at every cold boot, rather than residing in ROM.

| Feature | Details |
|---|---|
| CPU | 68000 @ 7.09 MHz |
| Chip RAM | 256 KB base (daughterboard adds 256 KB = 512 KB total) |
| Kickstart | Loaded from floppy into 256 KB WCS RAM at `$F80000` |
| Bootstrap ROM | 256 bytes at `$FC0000` — just enough to load Kickstart from floppy |
| Expansion | 86-pin sidecar bus (predecessor to Zorro) |

**WCS boot process:**
1. Power on → bootstrap ROM displays "Insert Kickstart disk"
2. User inserts Kickstart 1.x floppy
3. Bootstrap loads 256 KB Kickstart image into WCS RAM
4. Hardware write-protect latch activates → WCS becomes read-only
5. System resets and boots from the now-protected WCS as if it were ROM

> [!NOTE]
> The WCS is the reason the A1000 can run different Kickstart versions without swapping ROM chips. Third-party "Kickstart Eliminators" add actual ROM chips, bypassing the floppy-loading step entirely.

The A1000 daughterboard (256 KB Chip RAM expansion) sits inside the case on top of the motherboard. The 86-pin sidecar connector on the right side accepts external expansion chassis for memory, hard drives, and other peripherals.

### A2000 (1987) — The Expandable Workhorse

The A2000 is the first "big-box" Amiga, designed for professional expansion. It shipped in two major variants:

| Variant | Board Revisions | Chipset | Chip RAM | Notes |
|---|---|---|---|---|
| **A2000-A** (German) | Rev 3.x | OCS (Agnus 8361) | 512 KB | Original design by Commodore Germany |
| **A2000-B** (US) | Rev 4.x | OCS (Fat Agnus 8370/8372) | 512 KB + 512 KB slow | Redesigned for US market |
| **A2000-C** | Rev 6.x | ECS (Super Agnus 8372A) | 1 MB Chip | Late production with ECS chips |

#### Expansion Architecture

| Slot Type | Count | Bus Width | Address Space | Description |
|---|---|---|---|---|
| **Zorro II** | 5 | 16-bit | `$200000`–`$9FFFFF` (8 MB) | Autoconfig expansion cards |
| **CPU slot** | 1 | Direct 68000 | — | Directly wired to CPU socket — accepts accelerators (A2630, GVP G-Force) |
| **Video slot** | 1 | 36-pin | — | Internal video signals for genlocks and framebuffers |
| **ISA (PC bridgeboard)** | 2 | 8/16-bit | — | For A2088/A2286 PC compatibility cards |

The CPU slot is the A2000's most important expansion feature. Accelerator cards plug directly into the 68000 socket, replacing the CPU with 68020/030/040/060 processors. This makes the A2000 the most upgradeable classic Amiga.

> [!NOTE]
> Late A2000 boards (rev 6+) shipped with ECS chips and are sometimes listed under ECS. Architecturally they remain A2000 boards with the same Zorro II bus and expansion layout.

### CDTV (1991) — CD-ROM Set-Top Box

The CDTV is an A500-class OCS computer in a consumer set-top box form factor. See the dedicated article: **[CDTV Platform Hardware](cdtv_hardware.md)** — covers the DMAC/WD33C93 SCSI CD-ROM controller, 512 KB Extended ROM, 64 KB NVRAM, infrared remote, and real-time clock.

---

## OCS Limitations vs ECS/AGA

- Max **512 KB Chip RAM** on A500 rev 5 and earlier (Agnus 8361/8367 addresses 512 KB only)
- A500 rev 6+ allows 1 MB with Fat Agnus (part of later OCS run)
- No productivity display modes (ECS adds BEAMCON0)
- 32 colours max (or 64 EHB, or HAM 12-bit) in standard bitplane modes
- Blitter is 16-bit; no 64-bit fetch (AGA adds FMODE)
- No ECS Denise border features

## References

- ADCD 2.1 Hardware Manual: http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node0000.html
- *Amiga Hardware Reference Manual* 3rd ed., Chapter 5–8
