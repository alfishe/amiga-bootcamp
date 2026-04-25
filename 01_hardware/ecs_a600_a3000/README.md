[← Home](../../README.md) · [Hardware](../README.md)

# ECS Chipset — A600 / A3000 / A500+

## Overview

The **Enhanced Chip Set** (ECS) is a significant revision of OCS, shipping from 1990 onward. It adds 2 MB Chip RAM addressing, programmable display timing, and extended registers while maintaining full backward compatibility with OCS software.

## Chip Summary

| Chip | Part | Changes from OCS |
|---|---|---|
| **Super Agnus** | MOS 8372A | Addresses 2 MB Chip RAM, extended DMA window |
| **ECS Denise** | MOS 8373 | BPLCON3, border blank, programmable sync |
| **Paula** | MOS 8364 | Unchanged |

## Contents

| File | Topic |
|---|---|
| [chipset_ecs.md](chipset_ecs.md) | Super Agnus and ECS Denise internals |
| [ecs_registers_delta.md](ecs_registers_delta.md) | New/changed registers vs OCS |
| [productivity_modes.md](productivity_modes.md) | Multiscan/productivity display modes |
| [gary_system_controller.md](gary_system_controller.md) | Gary — A3000 bus controller, DMA arbitration, SCSI glue |
| [Gayle IDE & PCMCIA](../common/gayle_ide_pcmcia.md) | A600 Gayle: IDE and PCMCIA (shared with A1200) |
| [chip_ram_expansion.md](chip_ram_expansion.md) | 2 MB Chip RAM with Super Agnus |

## ECS vs OCS — Key Differences

| Feature | OCS | ECS |
|---|---|---|
| Max Chip RAM | 1 MB (Fat Agnus) | **2 MB** (Super Agnus) |
| Display sync | Fixed NTSC/PAL | **BEAMCON0** — programmable |
| Bitplane scroll | 4-bit (BPLCON1) | Extended (ECS Denise) |
| Border blank | No | **BPLCON3** border control |
| Hires sprites | No | ECS Denise extended sprite control |
| DMA window | Smaller | Extended: wider bitplane fetch |

## Identifying ECS at Runtime

```c
#include <exec/execbase.h>

struct ExecBase *SysBase = *((struct ExecBase **)4);
/* AttnFlags does not directly identify chipset */

/* Use graphics.library GfxBase->ChipRevBits0 */
#include <graphics/gfxbase.h>
struct GfxBase *GfxBase = (struct GfxBase *)OpenLibrary("graphics.library", 0);
if (GfxBase->ChipRevBits0 & GFXB_BIG_BLITTER) { /* ECS+ */ }
if (GfxBase->ChipRevBits0 & GFXB_HR_AGNUS)    { /* Super Agnus */ }
if (GfxBase->ChipRevBits0 & GFXB_HR_DENISE)   { /* ECS Denise */ }
```

## Machines Using ECS

| Model | Notes |
|---|---|
| A3000 | Super Agnus + ECS Denise; 68030; SCSI; Zorro III |
| A500+ | Super Agnus (1 MB variant); ECS Denise; no IDE |
| A600 | Super Agnus (1 MB variant); ECS Denise; Gayle; IDE; PCMCIA |
| A2000 (late) | Some late rev boards shipped with ECS chips |

## References

- ADCD 2.1 Hardware Manual — ECS extension chapters
- NDK39: `graphics/gfxbase.h` — ChipRevBits0 flags
- *Amiga Hardware Reference Manual* 3rd ed. — ECS appendix
