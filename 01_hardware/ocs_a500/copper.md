[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# Copper Coprocessor

## Overview

The **Copper** (co-processor) is built into Agnus. It executes a simple instruction list (the **copperlist**) in sync with the video beam, allowing precise per-scanline changes to any writable custom register — without CPU intervention.

The Copper can only write to custom registers (it cannot access Chip RAM directly), but it can change bitplane pointers, colours, BPLCON0, sprite pointers, and any other `$DFF0xx` register on a cycle-accurate basis.

## Copper Instruction Set

The Copper has exactly **three instructions**, each exactly **32 bits** (two 16-bit words):

### 1. MOVE — Write a Register

```
Word 1:  [RRR RRRR RRR0]   Destination register address (must be even, bit 0 = 0)
Word 2:  [DDDD DDDD DDDD]  Data to write
```

Example — set COLOR00 to red at scanline 100:
```
DC.W  $0180, $0F00    ; MOVE COLOR00, $0F00 (red)
```

### 2. WAIT — Wait for Beam Position

```
Word 1:  [VVVV VVVH HHHH HH1]   Vertical pos[8:1], Horizontal pos[8:3], bit0=1
Word 2:  [EVVV VVVH HHHH HHx0]  Enable, VP mask, HP mask, bit0=0
```

The Copper stalls until the beam reaches `(V,H) AND (Vmask,Hmask)`.

Standard full-precision WAIT:
```
DC.W  $6401, $FF00    ; WAIT for line $64 (100), any H — full V mask
```

WAIT for end of frame (copper stop):
```
DC.W  $FFFF, $FFFE    ; WAIT $FF,$FF — impossible position → stop copper
```

### 3. SKIP — Conditional Skip

```
Word 1:  [VVVV VVVH HHHH HH1]   Same format as WAIT
Word 2:  [EVVV VVVH HHHH HHx1]  Same as WAIT but bit 0 = 1 (SKIP flag)
```

If beam has passed the position, skip the next instruction. Used for double-buffered copper switching.

## Copperlist Format

A copperlist is an array of 32-bit instruction pairs in **Chip RAM**, terminated by:
```
DC.W  $FFFF, $FFFE
```

Example — colour cycle on vertical blank:
```asm
Copperlist:
    DC.W  $0180, $0000   ; COLOR00 = black
    DC.W  $4401, $FF00   ; WAIT line 68 (display area start)
    DC.W  $0180, $0F00   ; COLOR00 = red
    DC.W  $6401, $FF00   ; WAIT line 100
    DC.W  $0180, $00F0   ; COLOR00 = green
    DC.W  $FFFF, $FFFE   ; END
```

## Copper Pointers and Control

| Register | Offset | Description |
|---|---|---|
| COP1LCH | $080 | Copper list 1 pointer high word |
| COP1LCL | $082 | Copper list 1 pointer low word |
| COP2LCH | $084 | Copper list 2 pointer high word |
| COP2LCL | $086 | Copper list 2 pointer low word |
| COPJMP1 | $088 | Strobe: restart copper from list 1 (any write) |
| COPJMP2 | $08A | Strobe: restart copper from list 2 |
| COPCON | $02E | Copper danger bit (CDANG) |

**COPCON** bit 1 (`CDANG`): When set, Copper is allowed to write to registers `$40`–`$7F` (blitter registers). Should be 0 in normal use to prevent runaway copperlists from corrupting the blitter.

## Activating the Copper

```asm
; Load copperlist address into copper list 1
move.l  #Copperlist, d0
move.w  d0, COP1LCL+custom    ; low word
swap    d0
move.w  d0, COP1LCH+custom    ; high word

; Restart copper (triggers on next VBlank)
move.w  d0, COPJMP1+custom    ; value irrelevant, strobe only

; Enable copper DMA
move.w  #$8280, DMACON+custom ; SET + MASTER + COPEN
```

## Dual-Playfield and HAM via Copper

Common copper techniques:

**Split-screen different palettes:** Change `COLOR00`–`COLOR31` registers mid-screen via a WAIT at the split scanline.

**Mid-screen bitplane pointer change:** Redirect `BPL1PTH/BPL1PTL` to a different bitmap half-way through the display — used for large vertical scrolling without double-buffering the full screen.

**BPLCON0 mid-screen:** Switch between `HIRES` and `LORES`, or between 6-plane and 4-plane modes, on different lines.

**Raster bars:** Write a different colour to COLOR00 on every scanline using sequential WAIT+MOVE pairs.

## Graphics Library vs Direct Copper

AmigaOS's `graphics.library` manages the Copper list internally:
- `MrgCop()` merges system and user copper lists
- `LoadView()` installs a View structure's copper list
- `WaitTOF()` waits for the top-of-frame (VBlank) before the copper restarts

Direct copper access should be done via `GetColorMap()`, `SetRGB4()` and official graphics calls, or through a custom `View`/`ViewPort`/`ColorMap` structure passed to `LoadView()`.

## References

- ADCD 2.1 Hardware Manual — Copper chapter
- NDK39: `hardware/custom.h`, `graphics/copper.h`
- *Amiga Hardware Reference Manual* 3rd ed., Chapter 6
