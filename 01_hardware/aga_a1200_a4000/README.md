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
| [cpu_030_040.md](cpu_030_040.md) | 68030/040 on A3000/A4000: cache, MMU, FPU |
| [gayle_ide_a1200.md](gayle_ide_a1200.md) | A1200 Gayle: IDE and PCMCIA specifics |

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

## AGA Machines

| Model | CPU | Notes |
|---|---|---|
| A1200 | 68020 14 MHz | Budget AGA; Gayle IDE; PCMCIA; 2 MB Chip |
| A4000 | 68030/040 25 MHz | High-end; Zorro III; IDE; 2 MB Chip + Fast |
| A4000T | 68040/060 | Tower variant; SCSI |
| CD32 | 68020 14 MHz | Game console; CD-ROM; SX-1 expansion |

## References

- ADCD 2.1 Hardware Manual — AGA chapters
- NDK39: `graphics/gfxbase.h`, `hardware/custom.h`
- Commodore A1200/A4000 Technical Reference Manuals (local archive)
