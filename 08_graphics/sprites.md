[← Home](../README.md) · [Graphics](README.md)

# Hardware Sprites — SimpleSprite, MoveSprite

## Overview

The Amiga has **8 hardware sprites**, each 16 pixels wide with 3 colours + transparent. Sprites are DMA-driven — the Copper sets their pointers each frame and the display hardware renders them with zero CPU overhead.

---

## Sprite DMA Data Format

Each sprite scanline is two words (4 bytes):

```
Word 0 (DATA): bits 15–0 = pixel colour bit 0 for this line
Word 1 (DATB): bits 15–0 = pixel colour bit 1 for this line

Pixel colour = (DATB_bit << 1) | DATA_bit
  00 = transparent
  01 = colour 1 (from sprite palette)
  10 = colour 2
  11 = colour 3
```

### Sprite Header

```
WORD 0: VSTART (vertical start position) + HSTART high bits
WORD 1: VSTOP  (vertical stop position) + control bits
```

### End marker
```
WORD 0: 0x0000
WORD 1: 0x0000
```

---

## Sprite Colour Palette

| Sprite pair | Colour registers | Custom addresses |
|---|---|---|
| 0–1 | `COLOR17`–`COLOR19` | `$DFF1A2`–`$DFF1A6` |
| 2–3 | `COLOR21`–`COLOR23` | `$DFF1AA`–`$DFF1AE` |
| 4–5 | `COLOR25`–`COLOR27` | `$DFF1B2`–`$DFF1B6` |
| 6–7 | `COLOR29`–`COLOR31` | `$DFF1BA`–`$DFF1BE` |

Sprite pairs can be **attached** to form a single 15-colour sprite (using both sets of 2 bits = 4 bits per pixel).

---

## OS-Level Sprite API

```c
/* graphics.library */
struct SimpleSprite ss;
WORD sprnum;

/* Obtain a free sprite: */
sprnum = GetSprite(&ss, -1);   /* -1 = any available */
if (sprnum >= 0) {
    ss.x = 100;
    ss.y = 50;
    ss.height = 16;

    /* Move sprite to position: */
    MoveSprite(NULL, &ss, 100, 50);

    /* Set sprite image data: */
    ChangeSprite(NULL, &ss, spriteData);

    /* Release: */
    FreeSprite(sprnum);
}
```

---

## Sprite Pointer Registers

| Register | Address | Sprite |
|---|---|---|
| `SPR0PTH/L` | `$DFF120–$DFF122` | Sprite 0 |
| `SPR1PTH/L` | `$DFF124–$DFF126` | Sprite 1 |
| `SPR2PTH/L` | `$DFF128–$DFF12A` | Sprite 2 |
| `SPR3PTH/L` | `$DFF12C–$DFF12E` | Sprite 3 |
| `SPR4PTH/L` | `$DFF130–$DFF132` | Sprite 4 |
| `SPR5PTH/L` | `$DFF134–$DFF136` | Sprite 5 |
| `SPR6PTH/L` | `$DFF138–$DFF13A` | Sprite 6 |
| `SPR7PTH/L` | `$DFF13C–$DFF13E` | Sprite 7 |

These must be set every frame — typically via the Copper list.

---

## References

- HRM: *Amiga Hardware Reference Manual* — Sprites chapter
- NDK39: `graphics/sprite.h`
- ADCD 2.1: `GetSprite`, `MoveSprite`, `ChangeSprite`, `FreeSprite`
