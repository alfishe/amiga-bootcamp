[← Home](../README.md) · [Graphics](README.md)

# BitMap — Planar Bitmap Structure and Layout

## Overview

Amiga display memory uses **planar** layout: each bitplane is a separate contiguous memory region. A pixel's colour index is formed by reading one bit from each plane at the same x,y position. This is fundamentally different from chunky (packed-pixel) or interleaved formats.

---

## struct BitMap

```c
/* graphics/gfx.h — NDK39 */
struct BitMap {
    UWORD  BytesPerRow;    /* bytes per row per plane (must be even) */
    UWORD  Rows;           /* height in pixels */
    UBYTE  Flags;          /* BMF_* flags */
    UBYTE  Depth;          /* number of bitplanes (1–8) */
    UWORD  pad;
    PLANEPTR Planes[8];    /* pointers to each bitplane buffer */
};
```

---

## BMF_ Flags

```c
#define BMF_CLEAR        (1<<0)  /* clear planes on allocation */
#define BMF_DISPLAYABLE  (1<<1)  /* allocated in displayable (Chip) RAM */
#define BMF_INTERLEAVED  (1<<2)  /* planes are interleaved in memory */
#define BMF_STANDARD     (1<<3)  /* use standard allocation */
#define BMF_MINPLANES    (1<<4)  /* minimum number of planes */
```

---

## Planar Memory Layout

For a 320×256×4 display (16 colours):

```
BytesPerRow = 320/8 = 40 bytes
Rows = 256
Depth = 4

Plane 0: 40 × 256 = 10,240 bytes  (bit 0 of colour index)
Plane 1: 40 × 256 = 10,240 bytes  (bit 1)
Plane 2: 40 × 256 = 10,240 bytes  (bit 2)
Plane 3: 40 × 256 = 10,240 bytes  (bit 3)

Total = 4 × 10,240 = 40,960 bytes
```

Pixel colour at (x, y):
```
bit0 = (Planes[0][y * BytesPerRow + x/8] >> (7 - x%8)) & 1
bit1 = (Planes[1][y * BytesPerRow + x/8] >> (7 - x%8)) & 1
bit2 = (Planes[2][y * BytesPerRow + x/8] >> (7 - x%8)) & 1
bit3 = (Planes[3][y * BytesPerRow + x/8] >> (7 - x%8)) & 1
colour_index = (bit3 << 3) | (bit2 << 2) | (bit1 << 1) | bit0
```

---

## Allocation

```c
/* OS 3.0+ — AllocBitMap: */
struct BitMap *bm = AllocBitMap(320, 256, 4,
                                BMF_CLEAR | BMF_DISPLAYABLE, NULL);
/* Always in Chip RAM when BMF_DISPLAYABLE */

/* Manual allocation (OS 1.x compatible): */
struct BitMap bm;
InitBitMap(&bm, 4, 320, 256);
for (int i = 0; i < 4; i++)
    bm.Planes[i] = AllocRaster(320, 256);  /* MEMF_CHIP */

/* Free: */
FreeBitMap(bm);  /* or FreeRaster per plane */
```

---

## Interleaved BitMaps

With `BMF_INTERLEAVED`, all planes are stored sequentially row by row:
```
Row 0, Plane 0: 40 bytes
Row 0, Plane 1: 40 bytes
Row 0, Plane 2: 40 bytes
Row 0, Plane 3: 40 bytes
Row 1, Plane 0: 40 bytes
...
```

BytesPerRow becomes `40 × Depth = 160`, and each `Planes[i]` pointer is offset by `i * 40` from the base. This layout is more cache-friendly and allows single-pass blits.

---

## AGA 8-Bit Bitmaps

AGA (A1200/A4000) supports up to 8 bitplanes = 256 colours:
```c
struct BitMap *bm = AllocBitMap(320, 256, 8, BMF_CLEAR | BMF_DISPLAYABLE, NULL);
/* 8 planes × 10,240 = 81,920 bytes of Chip RAM */
```

---

## References

- NDK39: `graphics/gfx.h`
- ADCD 2.1: `AllocBitMap`, `FreeBitMap`, `InitBitMap`
- HRM: *Amiga Hardware Reference Manual* — bitplane DMA chapter
- See also: [memory_types.md](../01_hardware/common/memory_types.md) — why bitmaps must be in Chip RAM (DMA accessibility)
