[← Home](../../README.md) · [Hardware](../README.md)

# Amiga Address Space

## Overview

The Amiga uses a **24-bit physical address bus** on OCS/ECS machines (68000/68020 effective), giving 16 MB of addressable space. AGA machines with 68030/040 and 32-bit-clean software can address the full 4 GB, but Chip RAM and custom registers remain in the lower 16 MB.

## Memory Map — 24-bit (OCS/ECS, A500/A600/A3000)

```
$000000–$1FFFFF  Chip RAM (max 2 MB on ECS, 512 KB on OCS A500)
$200000–$9FFFFF  Fast RAM (expansion via Zorro II autoconfig)
$A00000–$BEFFFF  Zorro II I/O space
$BFD000–$BFDFFF  CIA-B  (8520, keyboard, floppy motor, disk side)
$BFE001–$BFE1FF  CIA-A  (8520, parallel port, serial flags, timer)
$C00000–$C7FFFF  Slow RAM ("Ranger", DMA-visible but not fast)
$C80000–$CFFFFF  Zorro II expansion I/O (boards)
$D00000–$D7FFFF  Zorro II expansion I/O
$D80000–$DBFFFF  Reserved / board-specific
$DC0000–$DCFFFF  Real-Time Clock (MSM6242B / RF5C01A)
$DD0000–$DEFFFF  Reserved
$DF0000–$DFFFFF  Custom chip registers ($DFF000–$DFF1FE)
$E00000–$E7FFFF  Kick memory (WCS / Ranger slow RAM mirror)
$E80000–$EFFFFF  Autoconfig space (Zorro II probe)
$F00000–$F7FFFF  Extended Kickstart ROM (OS 3.1: second 256 KB)
$F80000–$FFFFFF  Kickstart ROM (512 KB mirror at top of 16 MB)
```

## Memory Map — 32-bit (AGA, A1200/A4000)

```
$000000–$1FFFFF  2 MB Chip RAM
$200000–$07FFFFFF Fast RAM (on-board: 4–16 MB via Ramsey on A4000)
                   Trapdoor/PCMCIA on A1200
$A00000–$BEFFFF  Zorro II I/O
$BFD000          CIA-B
$BFE001          CIA-A
$C00000–$CFFFFF  Slow RAM / board I/O
$D80000–$D8FFFF  IDE / Gayle (A1200/A4000)
$DA0000–$DA3FFF  PCMCIA attribute memory (A1200)
$DC0000          RTC
$DFF000–$DFFFFF  Custom registers
$E00000–$E7FFFF  Kick mirror / WCS
$F00000–$F7FFFF  Extended ROM
$F80000–$FFFFFF  Kickstart ROM (512 KB)
$01000000+       Zorro III expansion (32-bit, A3000/A4000 only)
```

## Memory Type Classification

AmigaOS classifies memory by access flags used in `AllocMem()`:

| MEMF Flag | Value | Description |
|---|---|---|
| `MEMF_ANY` | 0 | No constraint |
| `MEMF_PUBLIC` | 1<<0 | Accessible to all tasks and DMA |
| `MEMF_CHIP` | 1<<1 | Chip RAM — accessible to custom chips (DMA) |
| `MEMF_FAST` | 1<<2 | Fast RAM — CPU-only, no DMA, faster |
| `MEMF_LOCAL` | 1<<8 | Not mapped out (always present) |
| `MEMF_24BITDMA` | 1<<9 | Addressable within 24-bit space |
| `MEMF_CLEAR` | 1<<16 | Zero-fill before returning |
| `MEMF_REVERSE` | 1<<17 | Allocate from top of memory |
| `MEMF_LARGEST` | 1<<18 | Return size of largest free block |
| `MEMF_TOTAL` | 1<<19 | Return total memory of type |

### Chip RAM Requirement

Custom chip DMA can only access **Chip RAM** (`MEMF_CHIP`). This means:
- Graphics bitmaps rendered by Blitter/Copper must be in Chip RAM
- Audio sample data must be in Chip RAM
- Copper lists must be in Chip RAM
- Sprite data must be in Chip RAM

Fast RAM is **CPU-only** — generally used for code, non-DMA data structures, and stacks.

## Diagram

```mermaid
block-beta
    columns 1
    block:chip["Chip RAM\n$000000–$1FFFFF\n(DMA accessible)"]
    block:fast["Fast RAM\n$200000–$9FFFFF\n(CPU only, faster)"]
    block:zio["Zorro II I/O\n$A00000–$BEFFFF"]
    block:cia["CIA-A/B\n$BFD000/$BFE001"]
    block:slow["Slow/Ranger RAM\n$C00000–$C7FFFF"]
    block:rtc["RTC $DC0000"]
    block:custom["Custom Registers\n$DFF000–$DFFFFF"]
    block:rom["Kickstart ROM\n$F80000–$FFFFFF"]
```

## Key Chip RAM Addresses

| Address | Content |
|---|---|
| $000000–$000400 | Exception vector table (copied from ROM) |
| $000004 | `SysBase` pointer (exec library base) |
| $000100 | Copper list scratch area (boot) |
| $000400–$001000 | Reserved by OS |
| $001000+ | Free Chip RAM (AvailMem result) |

> [!WARNING]
> Writing to $000000–$000400 corrupts the exception table. Writing to $000004 corrupts `SysBase`. These addresses must never be allocated by user code; exec reserves them.

## References

- NDK39: `exec/memory.h` — MEMF_ flag definitions
- ADCD 2.1 Hardware Manual: memory map chapter
- Commodore A1200/A4000 Technical Reference Manuals (local archive)
- See also: [memory_types.md](memory_types.md) — Chip RAM vs Fast RAM vs Slow RAM, DMA accessibility, per-model configurations
- See also: [chip_ram_expansion.md](../ecs_a600_a3000/chip_ram_expansion.md) — 2 MB Chip RAM with Super Agnus
