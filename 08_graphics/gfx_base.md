[← Home](../README.md) · [Graphics](README.md)

# GfxBase — Graphics Library Global State

## Overview

`graphics.library` manages all display output, drawing primitives, and custom chip programming. `GfxBase` is the library base containing display state, chip revision info, and the system copper lists.

---

## struct GfxBase (Key Fields)

```c
/* graphics/gfxbase.h — NDK39 */
struct GfxBase {
    struct Library   LibNode;
    struct View     *ActiView;        /* currently active View */
    struct copinit   *copinit;        /* system copper list init */
    LONG            *cia;             /* CIA base (deprecated) */
    LONG            *blitter;         /* blitter base (deprecated) */
    UWORD           *LOFlist;         /* long-frame copper list pointer */
    UWORD           *SHFlist;         /* short-frame copper list (interlace) */
    struct bltnode  *blthd;           /* blitter queue head */
    struct bltnode  *blttl;           /* blitter queue tail */
    struct bltnode  *bsblthd;
    struct bltnode  *bsblttl;
    struct Interrupt vbsrv;           /* vertical blank server list */
    struct Interrupt timsrv;
    struct Interrupt bltsrv;
    struct List      TextFonts;       /* system font list */
    struct TextFont *DefaultFont;     /* default system font */
    UWORD           Modes;            /* current display mode bits */
    BYTE            VBlankFrequency;  /* 50 (PAL) or 60 (NTSC) */
    BYTE            DisplayFlags;     /* PAL/NTSC/GENLOCK flags */
    UWORD           NormalDisplayColumns;
    UWORD           NormalDisplayRows;
    UWORD           MaxDisplayColumn;
    UWORD           MaxDisplayRow;
    UWORD           ChipRevBits0;     /* chip revision flags */
    /* ... many more fields ... */
    struct MonitorSpec *monitor_id;
    struct List      MonitorList;
    struct List      ModesList;       /* display mode database */
    UBYTE            MemType;         /* memory type flags */
    /* OS 3.x additions */
    APTR             ChunkyToPlanarPtr; /* c2p conversion routine */
};
```

---

## Chip Revision Detection

```c
/* graphics/gfxbase.h */
#define GFXB_BIG_BLITS   0   /* big blitter (ECS Agnus) */
#define GFXB_HR_AGNUS    0   /* same — hi-res Agnus */
#define GFXB_HR_DENISE   1   /* ECS Denise (SuperHires, scan-doubling) */
#define GFXB_AA_ALICE    2   /* AGA Alice (A1200/A4000) */
#define GFXB_AA_LISA     3   /* AGA Lisa */
#define GFXB_AA_MLISA    4   /* AGA Lisa (modified) */

#define GFXF_BIG_BLITS  (1<<0)
#define GFXF_HR_AGNUS   (1<<0)
#define GFXF_HR_DENISE  (1<<1)
#define GFXF_AA_ALICE   (1<<2)
#define GFXF_AA_LISA    (1<<3)
#define GFXF_AA_MLISA   (1<<4)

/* Check for AGA: */
if (GfxBase->ChipRevBits0 & GFXF_AA_ALICE) {
    /* AGA chipset — 8-bit planar, 256 colours in indexed mode */
}
```

---

## PAL vs NTSC

```c
if (GfxBase->VBlankFrequency == 50)  /* PAL: 50Hz, 625 lines */
if (GfxBase->VBlankFrequency == 60)  /* NTSC: 60Hz, 525 lines */
```

---

## References

- NDK39: `graphics/gfxbase.h`
- ADCD 2.1: graphics.library autodocs
