[← Home](../README.md) · [Graphics](README.md)

# RastPort — Drawing Primitives and Layers

## Overview

`RastPort` is the primary drawing context in AmigaOS. All graphics primitives (pixel, line, rectangle, polygon, text) operate through a `RastPort`, which links a `BitMap`, drawing pen colours, pattern, font, and optional `Layer` for clipping.

---

## struct RastPort

```c
/* graphics/rastport.h — NDK39 */
struct RastPort {
    struct Layer   *Layer;       /* associated layer (NULL = no clipping) */
    struct BitMap  *BitMap;      /* target bitmap */
    UWORD          *AreaPtrn;   /* area fill pattern */
    struct TmpRas  *TmpRas;     /* temp raster for area fills/floods */
    struct AreaInfo *AreaInfo;   /* area fill vertex buffer */
    struct GelsInfo *GelsInfo;   /* GEL (BOB/VSprite) list */
    UBYTE           Mask;        /* plane mask (which planes to draw to) */
    BYTE            FgPen;       /* foreground pen colour index */
    BYTE            BgPen;       /* background pen colour index */
    BYTE            AOlPen;      /* area outline pen */
    BYTE            DrawMode;    /* JAM1, JAM2, COMPLEMENT, INVERSVID */
    BYTE            AreaPtSz;    /* area pattern size (log2) */
    BYTE            linpatcnt;   /* line pattern counter */
    BYTE            dummy;
    UWORD           Flags;       /* FRST_DOT etc. */
    UWORD           LinePtrn;    /* 16-bit line dash pattern */
    WORD            cp_x, cp_y;  /* current pen position */
    UWORD           minterms[8];
    WORD            PenWidth;
    WORD            PenHeight;
    struct TextFont *Font;       /* current text font */
    UBYTE           AlgoStyle;   /* algorithmic style flags */
    UBYTE           TxFlags;
    UWORD           TxHeight;
    UWORD           TxWidth;
    UWORD           TxBaseline;
    WORD            TxSpacing;
    APTR           *RP_User;
    /* ... */
};
```

---

## Draw Modes

```c
#define JAM1        0   /* draw FgPen only; background transparent */
#define JAM2        1   /* draw FgPen and BgPen (opaque) */
#define COMPLEMENT  2   /* XOR with existing pixels */
#define INVERSVID   4   /* invert video (swap fg/bg for text) */
```

---

## Drawing Primitives

```c
/* Set pen colour: */
SetAPen(rp, 1);       /* foreground = colour 1 */
SetBPen(rp, 0);       /* background = colour 0 */
SetDrMd(rp, JAM1);    /* transparent background */

/* Move to position: */
Move(rp, 100, 50);

/* Draw line from current position to (x,y): */
Draw(rp, 200, 100);

/* Write pixel: */
WritePixel(rp, 160, 120);

/* Read pixel: */
LONG colour = ReadPixel(rp, 160, 120);

/* Filled rectangle: */
RectFill(rp, 10, 10, 100, 50);

/* Draw text at current position: */
Move(rp, 20, 30);
Text(rp, "Hello", 5);

/* Blitter copy between RastPorts: */
ClipBlit(srcRP, sx, sy, dstRP, dx, dy, w, h, minterm);
```

---

## Layers

When `rp->Layer != NULL`, all drawing is clipped to the layer's bounds and damage regions. Layers are managed by `layers.library`:

```c
struct Layer_Info *li = NewLayerInfo();
struct Layer *layer = CreateUpfrontLayer(li, bm, x1, y1, x2, y2, flags, NULL);
rp = layer->rp;   /* use this RastPort for drawing */
/* ... draw ... */
DeleteLayer(0, layer);
DisposeLayerInfo(li);
```

---

## References

- NDK39: `graphics/rastport.h`, `graphics/gfxmacros.h`
- ADCD 2.1: `SetAPen`, `Move`, `Draw`, `Text`, `RectFill`, `ClipBlit`
