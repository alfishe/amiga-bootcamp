[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# ECS Register Deltas vs OCS

This file documents registers that are **new or changed in ECS** versus OCS. OCS registers not listed here are unchanged.

## New Registers

### BEAMCON0 — $DFF1DC (ECS only)

The most significant new ECS register. Controls display sync generation and timing mode.

```
bit 15: HARDDIS  — disable hard limits on display window
bit 14: LPENDIS  — disable light pen latch
bit 13: VARVBEN  — enable variable VBlank
bit 12: LOLDIS   — disable long line sync
bit 11: CSCBEN   — composite sync on color burst
bit 10: VARVSYEN — variable vertical sync
bit  9: VARHSYEN — variable horizontal sync
bit  8: VARBEAMEN— variable beam enable
bit  7: DUAL     — dual sync (separate composite + RGB)
bit  6: PAL      — 1 = PAL timing, 0 = NTSC timing
bit  5: VARCSYEN — variable composite sync
bit  4: BLANKEN  — enable blanking signal
bit  3: CSYTRUE  — composite sync polarity
bit  2: VSYTRUE  — vertical sync polarity
bit  1: HSYTRUE  — horizontal sync polarity
bit  0: MONCSYEN — monochrome composite sync enable
```

**Default OCS behavior** is replicated by writing $0000 to BEAMCON0 on ECS.

**PAL/NTSC software switch:**
```asm
move.w  #$0020, $DFF1DC    ; BEAMCON0 = PAL mode
move.w  #$0000, $DFF1DC    ; BEAMCON0 = NTSC mode
```

**Productivity mode (31 kHz):**
```asm
move.w  #$0A00, $DFF1DC    ; VARBEAMEN + VARVSYEN (31 kHz VGA-like)
```

### BPLCON3 — $DFF106 (ECS Denise only)

New bitplane/sprite control register — see [chipset_ecs.md](chipset_ecs.md) for full bit definition.

### DENISEID — $DFF07C (read only, ECS+)

Chip identification — see [chipset_ecs.md](chipset_ecs.md).

## Changed / Extended Registers

### BPLCON0 — $DFF100

OCS BPLCON0 bit 0 (`ECSENA`) is reserved (must be 0) on OCS. On ECS:
```
bit 0: ECSENA — 1 = enable ECS features (required to use BPLCON3 etc.)
```

Must set `ECSENA=1` before programming ECS-specific display modes.

### DIWSTRT / DIWSTOP — $DFF08E / $DFF090

OCS: 8-bit vertical and 8-bit horizontal (limited range).

ECS: `DIWHIGH` ($DFF1E4) extends these to full 12-bit resolution:

### DIWHIGH — $DFF1E4 (ECS only)

```
bit 15:   FLOP1  — playfield 1 window high bit
bit 7:    FLOP0  — playfield 0 window high bit
bit 13-8: HB7-2  — horizontal window stop bits [7:2]
bit 5-0:  HS7-2  — horizontal window start bits [7:2]
```

Allows the display window to be positioned anywhere in the extended beam range, enabling full overscan without copper tricks.

### FMODE — $DFF1FC (ECS read, AGA write)

On ECS, `$DFF1FC` is reserved. On AGA it becomes the `FMODE` register (see AGA section).

## ECS-Only DMA Extended Mode

Super Agnus extends the chip bus to allow DMA access across the full 2 MB range. No register change is needed — the chip detects the extended address automatically based on the installed RAM size and its internal revision.

## Programming Notes

> [!WARNING]
> **OCS compatibility:** Never write to `BEAMCON0`, `BPLCON3`, or `DIWHIGH` on OCS hardware — the addresses are not decoded on OCS and writes may corrupt adjacent chip state or have undefined effects. Always check `GfxBase->ChipRevBits0` before writing ECS registers.

Safe ECS register programming pattern:
```c
#include <graphics/gfxbase.h>

extern struct GfxBase *GfxBase;

void set_pal_mode(void) {
    if (GfxBase->ChipRevBits0 & (1 << GFXB_HR_AGNUS)) {
        /* Safe to write BEAMCON0 */
        volatile UWORD *beamcon0 = (UWORD *)0xDFF1DC;
        *beamcon0 = 0x0020;  /* PAL */
    }
}
```

## References

- ADCD 2.1 Hardware Manual — ECS register descriptions
- NDK39: `hardware/custom.h` (note: some ECS registers not in OCS struct)
- AmigaMail Vol. 2 — ECS programming tutorials
- *Amiga Hardware Reference Manual* 3rd ed. — Appendix F
