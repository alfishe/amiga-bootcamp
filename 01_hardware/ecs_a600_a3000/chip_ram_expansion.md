[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# 2 MB Chip RAM with Super Agnus

## Overview

The original Agnus (8361/8367) could address only **512 KB** of Chip RAM. The Fat Agnus (later OCS revision) addressed **1 MB**. Super Agnus (8372A) extends the DMA address bus to **21 bits**, allowing **2 MB** of Chip RAM to be addressed by all DMA channels.

## Requirements for 2 MB Chip RAM

All of the following must be present:

1. **Super Agnus 8372A** — 2 MB variant (not all 8372A chips support 2 MB; check marking)
2. **2 MB of Chip RAM physically installed** — requires modified A3000 or a third-party board
3. **OS 2.0 or later** — earlier OS does not manage the extended Chip RAM

On the A3000, 2 MB Chip RAM is the standard configuration. On A500/A2000 with Super Agnus, it requires a RAM expansion that adds 1 MB in the Chip RAM window.

## Address Space Layout with 2 MB Chip RAM

```
$000000–$1FFFFF   2 MB Chip RAM (DMA accessible by all channels)
$200000+          Fast RAM (CPU only)
```

The Chip RAM extends from $000000 to $1FFFFF. Previously, $100000–$1FFFFF was "ranger" slow RAM, not DMA-accessible.

## OS Detection and Use

AmigaOS automatically discovers Chip RAM size via the exec memory list:

```c
/* Check available Chip RAM */
ULONG chip_free  = AvailMem(MEMF_CHIP);
ULONG chip_total = AvailMem(MEMF_CHIP | MEMF_TOTAL);
```

The exec memory list is built at boot time from the chip RAM size detected by the ROM initialisation code, which queries Agnus's internal address counter.

## AmigaOS ROM Initialisation (Exec init)

During cold boot, the Kickstart ROM probes Chip RAM size:

1. Write a test pattern to $100000 (top of 1 MB range)
2. Read back — if the value matches, 2 MB Chip RAM is present
3. The exec `MemHeader` for Chip RAM is extended to $1FFFFF

This is performed in the `RomBoot()` → `InitCode()` sequence before the exec memory system is fully initialised.

## Implications for Programming

- **Bitplane pointers** can address any location in the 2 MB range
- **Copper lists, sprite data, audio samples** can all use the upper 1 MB
- `AllocMem(size, MEMF_CHIP)` will draw from the full 2 MB pool
- **MEMF_24BITDMA** is set on Chip RAM to indicate DMA accessibility within the 24-bit space

## Common Pitfall: 1 MB vs 2 MB Super Agnus

Some Super Agnus chips (8372A rev 1) are hardware-limited to 1 MB despite the ECS part number. Identifying the 2 MB variant:

```asm
; Read the Agnus chip ID from VPOSR
move.w  $DFF004, d0     ; VPOSR
and.w   #$7F00, d0      ; mask to chip ID bits
cmp.w   #$2300, d0      ; 8372A 2MB = ID $23?
beq     .is_2mb_agnus
```

Software should not assume 2 MB Chip RAM — always use `AvailMem()` to determine the actual size.

## References

- Commodore A3000 Technical Reference Manual — memory section
- AmigaMail Vol. 2 — Chip RAM expansion articles
- NDK39: `exec/memory.h` — MEMF flags
- ADCD 2.1 Hardware Manual — memory map section
- See also: [memory_types.md](../common/memory_types.md) — comprehensive Chip/Fast/Slow RAM comparison, per-model configurations
