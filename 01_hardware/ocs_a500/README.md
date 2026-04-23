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
