[← Home](../README.md) · [Graphics](README.md)

# Blitter — DMA Engine, Minterms, BltBitMap

## Overview

The **Blitter** is a DMA engine in the custom chips that performs bulk memory operations: block copies, line drawing, area fills, and arbitrary boolean combinations of up to three source bitmaps. It operates independently of the CPU, freeing the 68k for other work.

---

## Channels

The blitter has four DMA channels:

| Channel | Name | Direction | Description |
|---|---|---|---|
| A | Source A | Read | First source bitmap |
| B | Source B | Read | Second source (often mask/pattern) |
| C | Source C | Read | Third source (typically destination for read-modify-write) |
| D | Destination | Write | Output |

Each channel has: pointer register, modulo register, shift register (A/B only), and first/last word masks (A only).

---

## Minterm Logic

The blitter combines A, B, C inputs using an 8-bit **minterm** value. Each bit selects whether the output is 1 for a specific combination:

| Bit | A | B | C | Common Use |
|---|---|---|---|---|
| 7 | 1 | 1 | 1 | — |
| 6 | 1 | 1 | 0 | — |
| 5 | 1 | 0 | 1 | — |
| 4 | 1 | 0 | 0 | — |
| 3 | 0 | 1 | 1 | — |
| 2 | 0 | 1 | 0 | — |
| 1 | 0 | 0 | 1 | — |
| 0 | 0 | 0 | 0 | — |

Common minterm values:

| Minterm | Hex | Operation |
|---|---|---|
| `$F0` | `A` | Copy A to D (straight copy) |
| `$CA` | `AB + ~AC` | Cookie-cut: A=mask, B=source, C=background |
| `$3C` | `A XOR C` | XOR blit (sprite toggle) |
| `$0F` | `NOT A` | Invert source |
| `$00` | `0` | Clear destination |
| `$FF` | `1` | Fill destination with 1s |

---

## Register Map

| Address | Name | Description |
|---|---|---|
| `$DFF040` | `BLTCON0` | Control: use-channels + minterm + shift-A |
| `$DFF042` | `BLTCON1` | Control: direction, fill mode, line mode |
| `$DFF044` | `BLTAFWM` | First word mask for channel A |
| `$DFF046` | `BLTALWM` | Last word mask for channel A |
| `$DFF048` | `BLTCPT` | Channel C pointer (high word) |
| `$DFF04A` | `BLTCPT` | Channel C pointer (low word) |
| `$DFF04C` | `BLTBPT` | Channel B pointer |
| `$DFF050` | `BLTAPT` | Channel A pointer |
| `$DFF054` | `BLTDPT` | Channel D pointer (destination) |
| `$DFF058` | `BLTSIZE` | Size and start: `(height << 6) | width_words` |
| `$DFF064` | `BLTCMOD` | Channel C modulo |
| `$DFF062` | `BLTBMOD` | Channel B modulo |
| `$DFF060` | `BLTAMOD` | Channel A modulo |
| `$DFF066` | `BLTDMOD` | Channel D modulo |

---

## OS-Level Blitter Functions

```c
/* graphics.library */

/* Copy rectangular region between bitmaps: */
LONG BltBitMap(
    struct BitMap *srcBM, WORD srcX, WORD srcY,
    struct BitMap *dstBM, WORD dstX, WORD dstY,
    WORD sizeX, WORD sizeY,
    UBYTE minterm,             /* usually $C0 = copy */
    UBYTE mask,                /* plane mask */
    APTR tempA                 /* temp buffer or NULL */
);

/* Blit into RastPort (clips to layer): */
void BltBitMapRastPort(struct BitMap *src, WORD srcX, WORD srcY,
                       struct RastPort *rp, WORD dstX, WORD dstY,
                       WORD sizeX, WORD sizeY, UBYTE minterm);

/* Wait for blitter completion: */
void WaitBlit(void);   /* must call before freeing blit buffers */

/* Gain exclusive blitter access: */
void OwnBlitter(void);
void DisownBlitter(void);
```

---

## References

- HRM: *Amiga Hardware Reference Manual* — Blitter chapter
- NDK39: `hardware/blit.h`, `graphics/gfx.h`
- ADCD 2.1: `BltBitMap`, `BltBitMapRastPort`, `OwnBlitter`
