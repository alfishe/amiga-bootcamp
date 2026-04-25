[← Home](../../README.md) · [Hardware](../README.md)

# AGA Chipset — A1200 / A4000 / CD32

## Overview

The **Advanced Graphics Architecture** (AGA) is the final custom chipset developed by Commodore, shipping from 1992. It dramatically expands colour depth, palette size, sprite capabilities, and blitter bandwidth while retaining full OCS/ECS backward compatibility.

## Chip Summary

| Chip | Name | Changes from ECS |
|---|---|---|
| **Alice** | MOS 8374 | Super Agnus successor: 64-bit bus, FMODE register |
| **Lisa** | (unnamed MOS) | ECS Denise successor: 8-bit palette, 256 colours |
| **Paula** | MOS 8364 | Unchanged from OCS/ECS |

## Contents

| File | Topic |
|---|---|
| [chipset_aga.md](chipset_aga.md) | Alice and Lisa internals, AGA architecture |
| [aga_registers_delta.md](aga_registers_delta.md) | New/changed registers vs ECS |
| [aga_palette.md](aga_palette.md) | 24-bit colour system, 256 registers |
| [aga_display_modes.md](aga_display_modes.md) | HAM8, 256-colour, doublescan, VGA |
| [aga_blitter.md](aga_blitter.md) | 64-bit blitter bus, FMODE |
| [aga_copper.md](aga_copper.md) | AGA Copper programming guide |
| [cpu_030_040.md](cpu_030_040.md) | 68030/040 on A3000/A4000: cache, MMU, FPU |
| [akiko_cd32.md](akiko_cd32.md) | CD32 Akiko chip: C2P conversion, CD-ROM, NVRAM |
| [Gayle IDE & PCMCIA](../common/gayle_ide_pcmcia.md) | A1200 Gayle: IDE and PCMCIA (shared with A600) |

## AGA vs ECS — Key Differences

| Feature | ECS | AGA |
|---|---|---|
| Colour registers | 32 (12-bit) | **256 (24-bit)** |
| Max simultaneous colours | 64 EHB / HAM | **256** (or HAM8: 262,144) |
| Blitter bus | 16-bit | **64-bit** (FMODE) |
| Sprite width | 16 px | **64 px** |
| Sprite colours | 3+transparent | **15+transparent** (64-colour attached) |
| Bitplane depth | 6 planes max | **8 planes** |
| Palette select | 1 bank | **4 bitplane banks, 4 sprite banks** |

## Identifying AGA at Runtime

```c
#include <graphics/gfxbase.h>

extern struct GfxBase *GfxBase;

BOOL is_aga = (GfxBase->ChipRevBits0 & (1 << GFXB_AA_ALICE)) != 0;
```

| ChipRevBits0 bit | Flag | Meaning |
|---|---|---|
| 4 | `GFXB_AA_ALICE` | AGA Alice present |
| 5 | `GFXB_AA_LISA` | AGA Lisa present |

---

## AGA Machines — Per-Model Details

| Model | CPU | Notes |
|---|---|---|
| A1200 | 68EC020 14 MHz | Budget AGA; Gayle IDE; PCMCIA; 2 MB Chip |
| A4000 | 68030/040 25 MHz | High-end; Zorro III; IDE; 2 MB Chip + Fast |
| A4000T | 68040/060 | Tower variant; SCSI |
| CD32 | 68EC020 14 MHz | Game console; Akiko C2P; CD-ROM; no keyboard |

### CD32 (1993) — AGA Game Console

The CD32 uses the **identical AGA chipset** (Alice + Lisa + Paula) as the A1200, but adds the **Akiko** custom chip — a unique ASIC providing:

- **Chunky-to-Planar (C2P) hardware conversion** — converts 8-bit linear pixel data to planar bitplane format
- **CD-ROM controller** — drives the internal double-speed CD-ROM via PIO (no SCSI, no IDE)
- **NVRAM interface** — I²C controller for 128-byte onboard EEPROM

The CD32 has **no Gayle chip** — Akiko replaces all storage functions. It has no keyboard, no floppy, no Zorro slots, and no PCMCIA. The only expansion path is the rear port (SX-1/SX-32 add-on units) or the FMV module slot.

See the dedicated article: **[Akiko — CD32 Custom Chip](akiko_cd32.md)**

### A4000T (1994) — Tower Workstation

The A4000T is the tower variant of the A4000 desktop, adding:

| Feature | A4000 Desktop | A4000T Tower |
|---|---|---|
| CPU | 68030 @ 25 MHz or 68040 @ 25 MHz | 68040 @ 25 MHz or 68060 @ 50 MHz |
| SCSI | None | **NCR53C710** (Fast SCSI-2, bus-mastering DMA) |
| Drive bays | 1× 3.5" IDE | 3× 5.25" + 1× 3.5" |
| Zorro III | 4 slots | 5 slots |
| CPU slot | Yes | Yes (enhanced pinout) |
| Power supply | Internal 150W | Internal 300W |
| IDE | On-board (Gayle-less) | On-board + SCSI |

The A4000T's **NCR53C710** SCSI controller is a high-performance bus-mastering DMA controller — significantly faster than the WD33C93 used in the A3000 and CDTV. It supports up to 7 SCSI devices on an internal 50-pin ribbon cable.

> [!NOTE]
> The A4000T was the last Amiga produced by Commodore before the company's bankruptcy in April 1994. Very few units were manufactured, making it one of the rarest stock Amiga models.

---

## References

- ADCD 2.1 Hardware Manual — AGA chapters
- NDK39: `graphics/gfxbase.h`, `hardware/custom.h`
- Commodore A1200/A4000 Technical Reference Manuals (local archive)

