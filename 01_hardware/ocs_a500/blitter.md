[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# Blitter

## Overview

The **Blitter** (Block Image Transferrer) is a DMA-driven coprocessor inside Agnus. It performs block copy, fill, and line-draw operations directly on Chip RAM without CPU involvement, at DMA bus speed.

## Channels

The Blitter has four channels:

| Channel | Role | Register Pointer |
|---|---|---|
| **A** | Source (with mask) | BLTAPTH/BLTAPTL |
| **B** | Source (with shift) | BLTBPTH/BLTBPTL |
| **C** | Source (destination content) | BLTCPTH/BLTCPTL |
| **D** | Destination | BLTDPTH/BLTDPTL |

Any channel can be disabled per operation. The result written to D is computed as a **minterm** (boolean function) of A, B, C.

## BLTCON0 — Control Register 0

```
bit 15-8: USEA, USEB, USEC, USED (enable channels A/B/C/D)
bit  7-0: LF (Logic Function / minterm) — 8-bit truth table
           Bit = result bit for combination of A,B,C
           Bit 7: !A!B!C
           Bit 6:  A!B!C
           Bit 5: !AB!C
           Bit 4:  AB!C
           Bit 3: !A!BC
           Bit 2:  A!BC
           Bit 1: !ABC
           Bit 0:  ABC
```

### Common Minterm Values

| Minterm | Hex | Operation |
|---|---|---|
| D = A AND B | $C0 | Mask copy |
| D = A | $F0 | Simple copy (A only) |
| D = A OR C | $FC | Overlay (A onto C) |
| D = A XOR C | $3C | XOR blit |
| D = NOT A | $0F | Invert A |
| D = (A AND B) OR (!A AND C) | $CA | Cookie-cut (transparency) |

### Cookie-Cut Example

Cookie-cut (transparent sprite blit):
```asm
; A = mask (1=opaque, 0=transparent)
; B = sprite data
; C = background
; D = result: background where mask=0, sprite where mask=1
; Minterm: D = (A AND B) OR (!A AND C) = $CA

move.w  #$09F0, BLTCON0    ; USE A,B,C,D; minterm=$CA
move.w  #$0000, BLTCON1
```

## BLTCON1 — Control Register 1

```
bit 15:  DOFF   — disable D write (dry run for fill detection)
bit  4:  IFE    — inclusive fill enable
bit  3:  EFE    — exclusive fill enable
bit  2:  FCI    — fill carry in (start state)
bit  1:  DESC   — descending mode (blit from bottom-right)
bit  0:  LINE   — line draw mode
```

## BLTSIZE — Start Blitter

```
BLTSIZE = (height << 6) | width_in_words
```

Writing to BLTSIZE starts the blit operation immediately. The blitter holds the bus until complete.

Example — blit 16×16 pixels (1 word wide, 16 lines):
```asm
move.w  #((16<<6)|1), BLTSIZE
```

Example — blit 320×256 (20 words wide, 256 lines):
```asm
move.w  #((256<<6)|20), BLTSIZE
```

## Modulo Registers

Modulo is the number of **bytes** to skip at the end of each row (to move to the start of the next row in a larger bitmap):

```
BLTxMOD = (bytes_per_row_in_bitmap) - (width_of_blit_in_bytes)
```

For a 320-pixel wide (40-byte row) bitmap, blitting a 32-pixel (4-byte) wide section:
```
Modulo = 40 - 4 = 36
```

## First/Last Word Masks

`BLTAFWM` (first word mask) and `BLTALWM` (last word mask) mask the A channel for the first and last word of each blit row, allowing sub-word-aligned blitting.

For a fully aligned blit with no partial words:
```asm
move.w  #$FFFF, BLTAFWM
move.w  #$FFFF, BLTALWM
```

## Line Draw Mode (BLTCON1 bit 0)

In line mode, the blitter draws a line between two points using the Bresenham algorithm:
- A channel provides the single pixel pattern (usually $8000 for MSB)
- D channel is the destination bitmap
- BLTSIZE specifies the line length (height=octant length, width=2)
- BLTCON1 encodes octant, sign flags, and texture data

Line mode is used by `graphics.library` `Draw()` calls internally.

## Fill Mode (BLTCON1 IFE/EFE)

**Exclusive fill (EFE):** Each set bit toggles the fill state — produces XOR fill (like polygon rasterisation).
**Inclusive fill (IFE):** Set bit turns fill on, stays on until end of row — used for solid polygon fill.

Fill operates in D channel only (no source channels active). BLTCON1 `DESC` bit = 1 when filling bottom-up.

## Waiting for Blitter Completion

```asm
; Busy-wait on BLTCON0 busy bit
WaitBlit:
    btst    #6, DMACONR+1    ; test BBUSY bit (bit 14 of DMACONR, byte=bit6)
    bne.s   WaitBlit
```

Or via exec (preferred):
```c
WaitBlit();   /* graphics.library — waits and resets to safe state */
```

> [!CAUTION]
> Never start a blit while the blitter is busy. Always call `WaitBlit()` or poll `DMACONR[BBUSY]` before setting up new blit registers.

## References

- ADCD 2.1 Hardware Manual — Blitter chapter
- NDK39: `hardware/blit.h`, `graphics/blitattr.h`
- graphics.library Autodocs: `BltBitMap`, `BltTemplate`, `BltClear`
- http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node006D.html
