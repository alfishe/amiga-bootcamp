[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Blitter — What It Is, What It Does, and 64-bit Bus Mode

## What Is the Blitter?

The **Blitter** (Block Image Transfer) is a dedicated DMA hardware engine inside every Amiga, designed to move and transform rectangular blocks of bitmap data **without CPU intervention**. While the CPU handles game logic, AI, physics, and sound setup, the Blitter does the heavy graphical lifting in the background.

Think of it as a **hardware GPU for 2D raster operations** — years before PC graphics cards existed.

### What the Blitter Can Do

| Capability | Description | Typical Use |
|---|---|---|
| **Block copy** | Move rectangular bitmap regions | Scrolling backgrounds, restoring screen areas |
| **Cookie-cut blit** | Stamp a shape onto a background using a mask | Drawing game sprites (BOBs) with transparency |
| **Area fill** | Fill arbitrary shapes | Flood-filling polygons, UI element backgrounds |
| **Line drawing** | Draw lines using hardware Bresenham | Vector graphics, wireframe 3D |
| **Clear/set memory** | Zero or fill large memory blocks | Screen clearing between frames |
| **Logic operations** | Combine 3 inputs with any Boolean function | XOR cursors, shadow effects, masking |
| **Shifting** | Shift source data 0–15 pixels | Sub-word-aligned sprite positioning |

### What the Blitter Cannot Do

| Limitation | Detail |
|---|---|
| No scaling | Cannot resize images — fixed 1:1 pixel mapping |
| No rotation | Cannot rotate — must be pre-rendered in software |
| No 3D | No perspective, texture mapping, or Z-buffer |
| No chunky pixels | Operates on **planar** bitplanes only (1 plane at a time) |
| No colour blending | Pure Boolean logic — no alpha, no transparency gradients |
| Word-aligned width | Minimum operation width is 16 pixels (1 word) |

### How Software Uses It

**Games** — The blitter draws BOBs (Blitter Objects = software sprites) by cookie-cutting character graphics onto the playfield. A typical game frame:
1. Blitter restores background behind old sprite positions
2. Game logic updates positions
3. Blitter draws sprites at new positions using cookie-cut
4. Copper switches display to the newly drawn buffer (double-buffering)

**Demos** — Demoscene coders exploit every blitter trick: interleaved bitplane blits, fill-mode for filled vector polygons, line-mode for wireframes, and careful DMA scheduling to run blitter and CPU in parallel.

**Applications** — Workbench uses `BltBitMap()` for window dragging, scrolling text, and refreshing damaged screen areas. The `layers.library` damage repair system depends entirely on blitter operations.

---

## AGA Enhancements

AGA's Alice chip extends the blitter with a **64-bit data bus mode** controlled by the `FMODE` register. This allows the blitter to fetch 2 or 4 words per DMA cycle, dramatically increasing fill and copy throughput for large bitmap operations.

## FMODE Configuration

`FMODE` ($DFF1FC) controls blitter, bitplane, and sprite DMA fetch widths independently:

```
bits 9-8: BLT_FMODE — blitter fetch mode
  00 = 16-bit (OCS compatible)
  01 = 32-bit
  10 = 64-bit
  11 = reserved

bits 13-12: BPL_FMODE — bitplane fetch mode (same encoding)
bits 15-14: SPR_FMODE — sprite fetch mode (same encoding)
```

Setting 64-bit blitter mode:
```asm
move.w  #$0300, $DFF1FC    ; BLT_FMODE = 10 (64-bit)
```

> [!IMPORTANT]
> FMODE must be set **before** loading blitter registers and starting the blit. Changing FMODE mid-blit causes undefined behaviour.

## Width Calculation with FMODE

When using wider fetch modes, **BLTSIZE widths must be adjusted**:

| FMODE | Width unit | Width formula |
|---|---|---|
| 1× (16-bit) | 1 word = 16 bits | `width_in_words` |
| 2× (32-bit) | 2 words = 32 bits | `(width_in_words + 1) / 2` |
| 4× (64-bit) | 4 words = 64 bits | `(width_in_words + 3) / 4` |

Example: blitting 320 pixels wide (20 words):
- 1× mode: BLTSIZE width = 20
- 2× mode: BLTSIZE width = 10
- 4× mode: BLTSIZE width = 5

**Modulo values are still in bytes** regardless of FMODE.

## Performance Comparison

For a typical 320×200 blit (simple copy, 1 bitplane):

| Mode | FMODE | Approx time (7 MHz) |
|---|---|---|
| OCS/ECS | 1× | ~1.8 ms |
| AGA 2× | 2× | ~0.9 ms |
| AGA 4× | 4× | ~0.45 ms |

## Alignment Requirements

Wider fetch modes impose alignment constraints on source/destination pointers:

| FMODE | Required alignment |
|---|---|
| 1× | 2 bytes (word) |
| 2× | 4 bytes (long) |
| 4× | 8 bytes (quadword) |

Misaligned pointers with 2× or 4× FMODE produce incorrect blit results.

## Using graphics.library

The OS `BltBitMap()` / `BltBitMapRastPort()` calls are FMODE-aware in OS 3.1+ on AGA hardware:

```c
BltBitMap(src_bm, srcx, srcy, dst_bm, dstx, dsty, width, height,
          0xC0, 0xFF, NULL);  /* minterm $C0 = copy, all planes */
```

`graphics.library` automatically selects the optimal FMODE for the current hardware.

## BLTCON0 / BLTCON1 — Unchanged in AGA

The minterm logic (`BLTCON0`) and fill/line mode (`BLTCON1`) registers are functionally identical to OCS/ECS. AGA only adds bandwidth, not new logical capabilities.

## Direct AGA Blitter Example (64-bit clear)

```asm
; Clear 320×256 bitmap at address $100000 (20 words wide, 256 lines)
; Using AGA 4× FMODE (5 quads wide)

move.w  #$0300, $DFF1FC       ; FMODE: BLT_FMODE = 4×

move.w  #$0100, BLTCON0+custom ; USE D only, minterm $00 (fill with zero)
move.w  #$0000, BLTCON1+custom

move.w  #$FFFF, BLTAFWM+custom ; first word mask
move.w  #$FFFF, BLTALWM+custom ; last word mask

move.l  #$00100000, BLTDPTH+custom+$00  ; dest high word
; (split into high/low)
move.w  #$0010, BLTDPTH+custom
move.w  #$0000, BLTDPTL+custom

move.w  #0, BLTDMOD+custom     ; modulo = 0 (contiguous)

; BLTSIZE = (256 lines << 6) | 5 quads width = (256*64)|5 = $4005
move.w  #((256<<6)|5), BLTSIZE+custom  ; start blit

; wait for completion
WaitBlit:
    btst    #6, DMACONR+custom+1
    bne.s   WaitBlit

; Restore FMODE to 1× for safety
move.w  #$0000, $DFF1FC
```

## References

- ADCD 2.1 Hardware Manual — AGA blitter section
- NDK39: `hardware/blit.h`, `hardware/custom.h`
- Commodore A1200/A4000 Technical Reference Manuals — Alice section
- graphics.library Autodocs: BltBitMap, BltClear
