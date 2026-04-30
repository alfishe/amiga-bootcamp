[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Sprite Enhancements

## Overview

AGA Lisa extends the [ECS sprite hardware](../ecs_a600_a3000/ecs_sprites.md) with substantial changes to width, color depth, and DMA data format. While the fundamental 8-channel architecture and position/control register layout remain OCS-compatible, AGA sprites can be **4× wider** and draw from **any 16-color slice** of the 256-color palette.

## What Changed from ECS

| Feature | ECS (Denise 8373) | AGA (Lisa) | Register |
|---|---|---|---|
| Maximum width | 16 pixels | **16, 32, or 64 pixels** | `FMODE` bits 15-14 |
| Color palette | COLOR16–COLOR31 fixed | **Any 16-color bank** of 256 | `BPLCON4` bits 7-0 |
| Even/odd bank | Same bank for pair | **Independent** even/odd banks | `BPLCON4` ESPRM/OSPRM |
| Scan doubling | Not available | **SSCAN2** for 31kHz displays | `BPLCON0` |
| Border sprites | BRDSPRT (inherited) | Same, over 256-color backgrounds | `BPLCON3` bit 3 |

---

## FMODE — Sprite Fetch Width ($DFF1FC)

The `FMODE` register controls DMA fetch width for sprites independently of bitplanes and blitter. Bits 15-14 (`SPR_FMODE`) set the sprite width:

| SPR_FMODE (bits 15-14) | Sprite Width | Words per Line | DMA Slots per Channel | Alignment |
|---|---|---|---|---|
| `00` | 16 pixels | 2 (DATA + DATB) | 2 | Word (2-byte) |
| `01` | 32 pixels | 4 (2 longwords) | 4 | Long (4-byte) |
| `10` | 64 pixels | 8 (4 longwords) | 8 | Quad (8-byte) |
| `11` | Reserved | — | — | — |

```asm
; Enable 64-pixel wide sprites
    move.w  #$C000, $DFF1FC     ; FMODE: SPR_FMODE = %10 (64px)
                                ; (preserves BPL_FMODE and BLT_FMODE at 1×)
```

> [!WARNING]
> `SPR_FMODE` is a **global setting** — all 8 sprite channels use the same width. You cannot mix 16px and 64px sprites in the same display. The Copper can change FMODE mid-frame but this requires careful DMA timing.

### DMA Data Format Changes

At wider FMODE settings, the sprite data block in memory grows proportionally:

**16px (SPR_FMODE = 00) — OCS-compatible:**
```
POS word | CTL word
DATA_A   | DATB_A          ← 1 pair per line (2 words)
...
$0000    | $0000            ← terminator
```

**32px (SPR_FMODE = 01):**
```
POS word | CTL word
DATA_A0  | DATA_A1 | DATB_A0 | DATB_A1    ← 2 pairs per line (4 words)
...
$0000    | $0000                            ← terminator
```

**64px (SPR_FMODE = 10):**
```
POS word | CTL word
DATA_A0  | DATA_A1 | DATA_A2 | DATA_A3 |
DATB_A0  | DATB_A1 | DATB_A2 | DATB_A3    ← 4 pairs per line (8 words)
...
$0000    | $0000                            ← terminator
```

> [!CAUTION]
> Sprite data pointers (`SPRxPTH/L`) must be aligned to the fetch width boundary. Misaligned pointers produce **corrupted sprite data** — the DMA engine reads incorrect word boundaries.
>
> | SPR_FMODE | Required Pointer Alignment |
> |---|---|
> | 1× (16px) | 2-byte (word) |
> | 2× (32px) | 4-byte (longword) |
> | 4× (64px) | 8-byte (quadword) |

### DMA Budget Impact

Wider sprites consume proportionally more DMA bandwidth:

| SPR_FMODE | DMA Slots (all 8 channels) | Bus Budget Impact |
|---|---|---|
| 1× (16px) | 16 slots/line | ~7% of scanline |
| 2× (32px) | 32 slots/line | ~14% of scanline |
| 4× (64px) | 64 slots/line | ~28% of scanline |

At 4× mode, sprite DMA alone consumes nearly a third of available bus bandwidth, leaving significantly less for bitplanes, blitter, and CPU.

---

## BPLCON4 — Sprite Color Bank Selection ($DFF10C)

AGA separates sprite color bank selection for even and odd channels, allowing each half of a sprite pair to draw from a different 16-color slice of the 256-color palette:

```
bits 7-4:  ESPRM7:4    Even sprite color bank (upper nibble of color index)
bits 3-0:  OSPRM7:4    Odd sprite color bank (upper nibble of color index)
```

### Color Index Calculation

The final 8-bit color register index for a sprite pixel is:

```
Even sprite: color_index = {ESPRM[7:4], sprite_pixel[3:0]}
Odd sprite:  color_index = {OSPRM[7:4], sprite_pixel[3:0]}
```

| ESPRM/OSPRM Value | Color Registers Used | Palette Slice |
|---|---|---|
| `$0` | COLOR0–COLOR15 | Shares with bitplane colors! |
| `$1` | COLOR16–COLOR31 | OCS-compatible default |
| `$2` | COLOR32–COLOR47 | — |
| ... | ... | ... |
| `$F` | COLOR240–COLOR255 | — |

```asm
; Even sprites use colors 64-79, odd sprites use colors 128-143
    move.w  #$0048, $DFF10C     ; BPLCON4: ESPRM = $4, OSPRM = $8
```

> [!WARNING]
> Setting `ESPRM` or `OSPRM` to `$0` causes sprite colors to overlap with **bitplane palette entries** (COLOR0–COLOR15). This is rarely intentional and can produce confusing visual artifacts.

### Attached Sprite Color Banks

In attached mode (15-color pairs), the 4-bit pixel index uses the **odd** channel's `OSPRM` value as the color bank, since the combined pixel index spans 0-15 within that bank.

---

## SSCAN2 — Sprite Scan Doubling

On AGA machines using 31kHz (VGA-compatible) display modes, the `SSCAN2` mechanism doubles each sprite scanline vertically to maintain correct aspect ratio. This is handled automatically by the display system when using `graphics.library` screen modes — direct hardware programming requires manual configuration.

---

## Programming Example

Complete example: 64px wide sprite using color bank 3 (COLOR48–COLOR63):

```asm
; Prerequisites: AGA machine, system taken over, custom registers accessible

; 1. Set sprite fetch mode to 64px
    move.w  #$C000, $DFF1FC         ; FMODE: SPR_FMODE = 10 (64px)

; 2. Set color bank for sprite 0 (even channel)
    move.w  #$0031, $DFF10C         ; BPLCON4: ESPRM = $3, OSPRM = $1

; 3. Point sprite 0 to quad-word aligned data in Chip RAM
    move.l  #SpriteData, d0
    move.w  d0, SPR0PTL+$DFF000
    swap    d0
    move.w  d0, SPR0PTH+$DFF000

; 4. Enable sprite DMA
    move.w  #$8020, $DFF096         ; DMACON: SET + SPREN

; ... SpriteData must be 8-byte aligned and use 64px data format
```

---

## See Also

- [OCS Sprite Hardware](../ocs_a500/sprites.md) — base register reference (SPRxPOS/CTL/DATA, color mapping, position formula)
- [ECS Sprite Enhancements](../ecs_a600_a3000/ecs_sprites.md) — border sprites, independent resolution (SPRES)
- [Sprites — Graphics Programming Guide](../../08_graphics/sprites.md) — OS API, techniques, decision guides, antipatterns
- [AGA Chipset Internals](chipset_aga.md) — Alice/Lisa overview, FMODE architecture
- [AGA Register Deltas](aga_registers_delta.md) — complete BPLCON4 definition
- [DMA Architecture](../common/dma_architecture.md) — FMODE bandwidth impact, sprite DMA slot budget, bus arbitration
- [AGA Palette](aga_palette.md) — 256-register 24-bit color system

## References

- *Amiga Hardware Reference Manual* 3rd ed. — AGA sprite extensions
- ADCD 2.1 Hardware Manual — AGA sprite chapter
- NDK39: `hardware/custom.h` — FMODE, BPLCON4 definitions
- Commodore A1200 Technical Reference Manual — Lisa sprite section
