[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Palette & Color System

## Overview

AGA provides **256 color registers** (COLOR00–COLOR255), each **24-bit RGB** (8 bits per channel). This replaces OCS/ECS's 32 registers with 12-bit color.

## Color Register Layout

```
ADDRESS:  $DFF180 + (n × 2)    for register n (0–255)
```

AGA extends the register space:
```
$DFF180–$DFF1BE  COLOR00–COLOR31   (same addresses as OCS/ECS)
$DFF180–$DFF3BE  COLOR00–COLOR255  (full AGA range — needs BPLCON4 bank select)
```

The 256 color registers are accessed in 64-register **banks** selected by `BPLCON4`.

## Writing 24-bit Colors

Each color register holds 12 bits directly (OCS/ECS compatible). The upper 12 bits (the "low nibble") are written via a second access with `LOCT` set in BPLCON3.

### Manual 24-bit write sequence:

```asm
; Write color $FF8040 (R=$FF, G=$80, B=$40) to COLOR00

; Step 1: Write high nibble ($F84 = top 4 bits of R,G,B)
move.w  #$0F84, COLOR00+custom   ; $0RGB high nibble

; Step 2: Set LOCT bit in BPLCON3 to enable low nibble write
bset    #9, BPLCON3+custom+1     ; bit 9

; Step 3: Write low nibble ($F04 = low 4 bits of R,G,B → $0F, $08, $04 → $F84 again!)
; Actually: low nibble of FF = F, low nibble of 80 = 0, low nibble of 40 = 0
move.w  #$0F00, COLOR00+custom   ; low nibble

; Step 4: Clear LOCT
bclr    #9, BPLCON3+custom+1
```

### Using LoadRGB32()

The preferred OS call:
```c
#include <graphics/view.h>
#include <proto/graphics.h>

/* Table: count, index, then 0x00RRGGBB values, terminated by ~0 */
ULONG table[] = {
    4, 0,             /* 4 colors starting at index 0 */
    0x00FF0000,       /* COLOR00: red   */
    0x0000FF00,       /* COLOR01: green */
    0x000000FF,       /* COLOR02: blue  */
    0x00FFFFFF,       /* COLOR03: white */
    ~0UL              /* terminator */
};
LoadRGB32(viewport, table);
```

`LoadRGB32()` (graphics.library LVO -$192) is the AGA-correct way to set colors. It handles the two-write LOCT protocol internally and is available from OS 3.0+.

### Using LoadRGB4() — OCS/ECS compatible (12-bit)

```c
UWORD colors[32] = { 0x000, 0xF00, 0x0F0, ... };
LoadRGB4(viewport, colors, 32);  /* sets 32 colors from 12-bit table */
```

`LoadRGB4()` is safe on all chipsets but only provides 12-bit precision on AGA.

## HAM8 Mode (Hold-And-Modify, 8-bit)

HAM8 is the AGA extension of OCS's HAM6. It uses 8 bitplanes:

- **Bits 7-6** of each pixel: mode select
  - `00` = index mode (look up COLOR00–COLOR63)
  - `01` = modify blue channel
  - `10` = modify red channel
  - `11` = modify green channel
- **Bits 5-0**: 6-bit value for the selected channel (or 6-bit color index)

Result: 2^18 = **262,144 simultaneous colors** from adjacent-pixel modification.

Enabling HAM8:
```asm
; BPLCON0: 8 planes (BPU=8, BPU3=1, BPU2-0=000), HAM=1, ECSENA=1
move.w  #$9811, BPLCON0+custom
```

## Color Modes Summary

| Mode | Planes | Colors | Method |
|---|---|---|---|
| Standard | 1–8 | 2–256 | Direct palette lookup |
| EHB | 6 | 64 | Extra Half-Brite (OCS/ECS compat) |
| HAM6 | 6 | 4096 | Hold-and-modify 4-bit channels |
| HAM8 | 8 | 262,144 | Hold-and-modify 6-bit channels |
| Dual Playfield | 3+3 | 8+8 | Two independent 8-color layers |

## Color Bank Selection (BPLCON4)

The 256 color registers are split into 4 banks of 64:

| BPLAM | Bank | Registers |
|---|---|---|
| $00 | 0 | COLOR00–COLOR63 |
| $40 | 1 | COLOR64–COLOR127 |
| $80 | 2 | COLOR128–COLOR191 |
| $C0 | 3 | COLOR192–COLOR255 |

Dual playfield can use BPLCON4 to give each playfield a different 64-color bank.

## OS Color Management

`graphics.library` manages palette via the `ColorMap` structure attached to a `ViewPort`:

```c
struct ColorMap *cm = GetColorMap(256);     /* allocate 256-entry AGA map */
SetRGB32(vp, n, r, g, b);                  /* set one color (24-bit each) */
LoadRGB32(vp, table);                       /* bulk load */
FreeColorMap(cm);
```

## References

- NDK39: `graphics/view.h` — ColorMap, LoadRGB32
- ADCD 2.1 Autodocs: graphics — LoadRGB32, SetRGB32
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node02B4.html
- AmigaMail Vol. 2 — AGA color system articles
