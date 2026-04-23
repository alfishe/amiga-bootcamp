[← Home](../README.md) · [Graphics](README.md)

# Blitter Programming — Deep Dive

## Overview

The **Blitter** (Block Image Transfer) is a DMA engine that performs raster operations on rectangular blocks of memory. It operates on up to **4 channels** (A, B, C → D) using programmable **minterm logic** and can work independently of the CPU. The Blitter is the workhorse for screen clearing, scrolling, cookie-cut sprites, line drawing, and area fill.

---

## Channel Architecture

```
Channel A ──→ ┐
Channel B ──→ ├──→ Minterm Logic ──→ Channel D (output)
Channel C ──→ ┘

A = mask/pattern (e.g., cookie shape, font glyph)
B = source image data
C = background / destination read-back
D = output destination
```

Each channel reads (or writes, for D) from a different memory pointer with independent modulo.

---

## Minterm Logic

The minterm is an **8-bit truth table** encoding the logical function of A, B, C:

```
Bit 7: ABC = 111  →  bit value
Bit 6: ABC = 110  →  bit value
Bit 5: ABC = 101  →  bit value
Bit 4: ABC = 100  →  bit value
Bit 3: ABC = 011  →  bit value
Bit 2: ABC = 010  →  bit value
Bit 1: ABC = 001  →  bit value
Bit 0: ABC = 000  →  bit value
```

### Common Minterms

| Minterm | Hex | Operation | Use Case |
|---|---|---|---|
| `D = A` | `$F0` | Copy A to D | Simple block copy |
| `D = B` | `$CC` | Copy B to D | Simple block copy |
| `D = C` | `$AA` | Copy C to D | Read-back |
| `D = A·B + (¬A)·C` | `$CA` | Cookie-cut | Masked sprite blit (B through A mask onto C) |
| `D = 0` | `$00` | Clear | Clear a memory region |
| `D = $FFFF` | `$FF` | Set all | Fill with 1s |
| `D = A XOR C` | `$5A` | XOR | Cursor blink, highlight |
| `D = A OR C` | `$FA` | OR | Overlay |
| `D = ¬A AND C` | `$0A` | Mask out | Erase through mask |
| `D = A·B` | `$C0` | AND (A,B) | Masked pattern |

### Cookie-Cut Explained

```
A = mask (1 = sprite pixel, 0 = transparent)
B = sprite image data
C = background
D = result

Minterm $CA:
  Where A=1: D = B  (show sprite)
  Where A=0: D = C  (show background)
```

---

## Register Reference

| Reg | Offset | Description |
|---|---|---|
| `BLTCON0` | `$040` | Control: channels enabled (bits 11–8), ASH (bits 15–12), minterm (bits 7–0) |
| `BLTCON1` | `$042` | Control: BSH (bits 15–12), line mode (bit 0), fill mode (bits 3–2) |
| `BLTAFWM` | `$044` | First word mask for channel A |
| `BLTALWM` | `$046` | Last word mask for channel A |
| `BLTAPT` | `$050` | Channel A pointer (high+low) |
| `BLTBPT` | `$04C` | Channel B pointer |
| `BLTCPT` | `$048` | Channel C pointer |
| `BLTDPT` | `$054` | Channel D pointer |
| `BLTAMOD` | `$064` | Channel A modulo |
| `BLTBMOD` | `$062` | Channel B modulo |
| `BLTCMOD` | `$060` | Channel C modulo |
| `BLTDMOD` | `$066` | Channel D modulo |
| `BLTSIZE` | `$058` | Blit size + START (write triggers blit) |

### BLTCON0 Encoding

```
Bits 15–12: ASH (A shift, 0–15 pixels)
Bit  11:    USEA (enable channel A)
Bit  10:    USEB (enable channel B)
Bit   9:    USEC (enable channel C)
Bit   8:    USED (enable channel D, almost always 1)
Bits  7–0:  Minterm
```

### BLTSIZE Encoding (OCS/ECS)

```
Bits 15–6: Height in lines (1–1024, 0 means 1024)
Bits  5–0: Width in words (1–64, 0 means 64)
```

**Writing BLTSIZE starts the blit!**

---

## Complete Examples

### Example 1: Clear Screen (320×256, 1 bitplane)

```asm
    lea     $DFF000,a5

    ; Wait for blitter idle:
.bwait:
    btst    #14,$002(a5)    ; DMACONR bit 14 = BBUSY
    bne.s   .bwait

    ; D channel only, minterm $00 (clear):
    move.l  #$01000000,$040(a5)  ; BLTCON0: USED=1, minterm=$00
    clr.w   $042(a5)             ; BLTCON1: 0
    move.l  #ScreenMem,$054(a5)  ; BLTDPT
    clr.w   $066(a5)             ; BLTDMOD: 0 (contiguous)
    move.w  #(256<<6)|20,$058(a5) ; BLTSIZE: 256 lines × 20 words (320/16)
    ; Blit is now running!
```

### Example 2: Block Copy (No Shift)

```asm
    ; Copy 64×64 pixel block from source to dest (1 bitplane)
    ; Source and dest are in contiguous bitmap, 320 pixels wide

    ; Width = 64 pixels = 4 words
    ; Modulo = (320 - 64) / 16 = 16 words = 32 bytes

    lea     $DFF000,a5

.bwait:
    btst    #14,$002(a5)
    bne.s   .bwait

    move.l  #$09F00000,$040(a5)  ; BLTCON0: USEA+USED, minterm=$F0 (A→D)
    clr.w   $042(a5)             ; BLTCON1
    move.w  #$FFFF,$044(a5)      ; BLTAFWM = all bits
    move.w  #$FFFF,$046(a5)      ; BLTALWM = all bits
    move.l  #SourceAddr,$050(a5) ; BLTAPT
    move.l  #DestAddr,$054(a5)   ; BLTDPT
    move.w  #32,$064(a5)         ; BLTAMOD = 32 bytes
    move.w  #32,$066(a5)         ; BLTDMOD = 32 bytes
    move.w  #(64<<6)|4,$058(a5)  ; BLTSIZE: 64 lines × 4 words → GO!
```

### Example 3: Cookie-Cut Blit (Masked Sprite)

```asm
    ; Blit a 16×16 masked sprite onto background
    ; A = mask, B = sprite data, C = background, D = destination

    lea     $DFF000,a5

.bwait:
    btst    #14,$002(a5)
    bne.s   .bwait

    move.l  #$0FCA0000,$040(a5)  ; BLTCON0: A+B+C+D, minterm=$CA
    clr.w   $042(a5)             ; BLTCON1
    move.w  #$FFFF,$044(a5)      ; BLTAFWM
    move.w  #$FFFF,$046(a5)      ; BLTALWM
    move.l  #MaskData,$050(a5)   ; BLTAPT = mask
    move.l  #SpriteData,$04C(a5) ; BLTBPT = sprite imagery
    move.l  #ScreenPos,$048(a5)  ; BLTCPT = background (read-back)
    move.l  #ScreenPos,$054(a5)  ; BLTDPT = same as C (overwrite)
    clr.w   $064(a5)             ; BLTAMOD = 0 (mask is 16px = 1 word wide)
    clr.w   $062(a5)             ; BLTBMOD = 0
    move.w  #38,$060(a5)         ; BLTCMOD = (320-16)/8 = 38 bytes
    move.w  #38,$066(a5)         ; BLTDMOD = 38
    move.w  #(16<<6)|1,$058(a5)  ; BLTSIZE: 16 lines × 1 word → GO!
```

### Example 4: Line Drawing

```asm
    ; Draw a line from (x1,y1) to (x2,y2) using blitter line mode
    ; This is complex — blitter line mode uses a Bresenham-style algorithm
    ; implemented in hardware

    ; BLTCON1 bit 0 = LINE mode
    ; Channel A = single word (texture pattern)
    ; Channel C/D = destination bitmap

    ; See HRM for the full algorithm; here's the concept:
    move.l  #$0B4A0000,$040(a5)  ; BLTCON0: A+C+D, minterm=$4A (XOR), ASH=dx
    move.w  #$0001,$042(a5)      ; BLTCON1: LINE=1, octant bits set per slope
    move.w  #$8000,$074(a5)      ; BLTADAT: single pixel pattern
    move.w  #$FFFF,$044(a5)      ; BLTAFWM
    move.l  #StartPos,$048(a5)   ; BLTCPT: line start position in bitmap
    move.l  #StartPos,$054(a5)   ; BLTDPT: same
    move.w  #Modulo,$060(a5)     ; BLTCMOD
    move.w  #Modulo,$066(a5)     ; BLTDMOD
    move.w  #(len<<6)|2,$058(a5) ; BLTSIZE: length × 2 → GO!
```

---

## System-Friendly Blitter (via graphics.library)

```c
/* BltBitMap — the safe, OS-friendly way: */
BltBitMap(srcBitmap, srcX, srcY,
          dstBitmap, dstX, dstY,
          width, height,
          0xC0,     /* minterm: A AND B */
          0xFF,     /* all planes */
          NULL);    /* temp buffer */

/* BltMaskBitMapRastPort — cookie-cut with mask: */
BltMaskBitMapRastPort(srcBM, srcX, srcY,
                       rp, dstX, dstY,
                       width, height,
                       (ABC | ABNC | ANBC),  /* minterm for cookie */
                       maskPlane);

/* BltClear — fast memory clear: */
BltClear(memory, byteCount, 0);

/* OwnBlitter / DisownBlitter — exclusive access: */
OwnBlitter();    /* wait for and lock blitter */
/* ... direct register programming ... */
DisownBlitter(); /* release */
```

---

## Performance Notes

| Operation | Speed |
|---|---|
| Word copy | 4 DMA cycles per word (1 µs at 3.58 MHz) |
| Full 320×256 clear | ~1280 µs (~1.3 ms) |
| Cookie-cut blit | 4 channels = 4 cycles/word (same as copy) |
| CPU vs blitter | Blitter wins for moves > ~40 words |
| Nasty mode | `BLTPRI` in DMACON: blitter gets priority, CPU stalls |

---

## References

- HRM: *Blitter* chapter — complete register descriptions
- `01_hardware/ocs_a500/blitter.md` — hardware reference
- `08_graphics/blitter.md` — graphics.library BltBitMap API
