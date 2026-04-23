[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# Hardware Sprites

## Overview

The OCS/ECS chipset provides **8 hardware sprites**, each 16 pixels wide and arbitrarily tall. They are managed by Agnus's DMA and rendered by Denise independently of the bitplane display. Sprites are commonly used for the mouse pointer, weapons, overlays, and animated objects that must not disturb the background.

## Sprite Properties (OCS)

| Property | OCS Value |
|---|---|
| Count | 8 sprites |
| Width | 16 pixels fixed |
| Height | Programmable (any number of lines) |
| Colours | 3 (+1 transparent) per sprite |
| Colour source | Sprite colour registers (COLOR16–COLOR31) |
| Attach mode | Pairs 0/1, 2/3, 4/5, 6/7 → 15 colours |

## Sprite Registers

Each sprite `n` (0–7) has four registers at `$DFF120 + n×$08`:

| Offset | Name | Description |
|---|---|---|
| +$00/$01 | SPRnPTH/SPRnPTL | Sprite DMA pointer (high/low) |
| +$04 | SPRnPOS | Vertical start, horizontal position |
| +$06 | SPRnCTL | Vertical stop, attach flag, H LSB |
| +$08 | SPRnDATA | Image data word A (current line) |
| +$0A | SPRnDATB | Image data word B (current line) |

## SPRnPOS — Position Register

```
bit 15-8:  VSTART[8:1]  Vertical start position (high 8 bits)
bit 7-0:   HSTART[8:1]  Horizontal position (bits 8..1, shifted right)
```

## SPRnCTL — Control Register

```
bit 15-8:  VSTOP[8:1]   Vertical stop position
bit 7:     ATT          Attach (pair this sprite with next)
bit 2:     HSTART[0]    Horizontal position LSB
bit 1:     VSTOP[0]     Vertical stop LSB
bit 0:     VSTART[0]    Vertical start LSB
```

## Horizontal Position Formula

```
H pixel = (HSTART[8:0]) - 1
```

Standard screen left edge is approximately H=128 (HSTART=$80).

## Sprite DMA Data Format

Each line of the sprite consists of two 16-bit words (DATA and DATB) fetched from Chip RAM:

```
For each scanline of sprite:
  Word 1 (DATA): bit 15..0 → pixel bit 1 (colour bit 1)
  Word 2 (DATB): bit 15..0 → pixel bit 0 (colour bit 0)

Pixel colour:
  DATA[bit] = 0, DATB[bit] = 0  → transparent
  DATA[bit] = 0, DATB[bit] = 1  → colour 1 (COLOR17 for sprite 0)
  DATA[bit] = 1, DATB[bit] = 0  → colour 2 (COLOR18)
  DATA[bit] = 1, DATB[bit] = 1  → colour 3 (COLOR19)
```

## Sprite Data in Memory

Agnus DMA reads the sprite from a memory block structured as:

```
  Word: SPRnPOS value (copied to register at DMA start)
  Word: SPRnCTL value (copied to register at DMA start)
  [Repeat for each line:]
  Word: SPRnDATA (image word A)
  Word: SPRnDATB (image word B)
  [End of sprite:]
  Word: $0000   (SPRnPOS = 0 → null position signals end)
  Word: $0000   (SPRnCTL = 0)
```

## Colour Mapping

Sprites share colour registers with bitplanes:

| Sprites | Colour Registers |
|---|---|
| 0 and 1 | COLOR16–COLOR19 |
| 2 and 3 | COLOR20–COLOR23 |
| 4 and 5 | COLOR24–COLOR27 |
| 6 and 7 | COLOR28–COLOR31 |

COLOR16 (the first colour of sprite pair 0/1) is always transparent — the sprite background. Only COLOR17–COLOR19 are visible for sprites 0/1.

## Attached Sprites (15 Colours)

Pairing two sprites (`ATT` bit in SPRnCTL of the even sprite) combines their DATA/DATB bits to produce a 4-bit colour index (16 colours, one transparent):

```
4-bit colour = {SPR_even.DATA[bit], SPR_even.DATB[bit],
                SPR_odd.DATA[bit],  SPR_odd.DATB[bit]}
```

This gives 15 visible colours per pair, using COLOR16–COLOR31 for pair 0/1.

## BPLCON2 — Sprite Priority

`BPLCON2` ($DFF104) controls the display priority of sprites vs bitplanes:

```
bit 5-3: PF2PRI, PF2P2-0  — Playfield 2 priority
bit 2-0: PF1PRI, PF1P2-0  — Playfield 1 and sprite priority
```

Default: sprites appear in front of all bitplanes.

## OS Mouse Pointer

AmigaOS's Intuition uses sprite 0 (and 1 in attached mode for colour pointer) for the mouse pointer. Intuition calls `SetPointer()` / `ClearPointer()` on a Window to install custom pointer sprites.

```c
SetPointer(window, pointer_data, height, width, x_offset, y_offset);
ClearPointer(window);  /* restore system default */
```

## References

- ADCD 2.1 Hardware Manual — Sprites chapter
- NDK39: `hardware/sprite.h`, `intuition/intuition.h` (SetPointer)
- http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node00D7.html
