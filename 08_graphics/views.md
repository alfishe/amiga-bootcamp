[← Home](../README.md) · [Graphics](README.md)

# Views and ViewPorts — Display Construction

## Overview

The AmigaOS display system builds the actual screen image through a hierarchy: `View` → `ViewPort` → `RasInfo` → `BitMap`. The `MakeVPort`/`MrgCop`/`LoadView` pipeline compiles this into a Copper list that programs the custom chips.

---

## Key Structures

```c
/* graphics/view.h — NDK39 */
struct View {
    struct ViewPort *ViewPort;  /* first viewport in chain */
    struct cprlist  *LOFCprList; /* long-frame copper list */
    struct cprlist  *SHFCprList; /* short-frame copper list */
    WORD            DyOffset;   /* vertical scroll offset */
    WORD            DxOffset;   /* horizontal scroll offset */
    UWORD           Modes;      /* display mode flags */
};

struct ViewPort {
    struct ViewPort *Next;       /* next viewport in chain */
    struct ColorMap *ColorMap;   /* palette for this viewport */
    struct CopList  *DspIns;     /* display copper instructions */
    struct CopList  *SprIns;     /* sprite copper instructions */
    struct CopList  *ClrIns;     /* colour copper instructions */
    struct CopList  *UCopIns;    /* user copper instructions */
    WORD            DWidth;      /* display width */
    WORD            DHeight;     /* display height */
    WORD            DxOffset;
    WORD            DyOffset;
    UWORD           Modes;       /* HIRES, LACE, HAM, EHB, etc. */
    UBYTE           SpritePriorities;
    UBYTE           ExtendedModes;
    struct RasInfo  *RasInfo;    /* linked bitmap info */
};

struct RasInfo {
    struct RasInfo *Next;        /* for dual-playfield */
    struct BitMap  *BitMap;      /* the actual bitmap */
    WORD           RxOffset;     /* horizontal scroll within bitmap */
    WORD           RyOffset;     /* vertical scroll within bitmap */
};
```

---

## Display Mode Flags

```c
/* graphics/view.h */
#define HIRES       0x8000   /* 640 pixel mode */
#define LACE        0x0004   /* interlaced */
#define HAM         0x0800   /* Hold-And-Modify (4096 colours) */
#define EXTRA_HALFBRITE 0x0080 /* Extra Half-Brite (64 colours) */
#define DUALPF      0x0400   /* dual playfield */
#define PFBA        0x0040   /* playfield B has priority */
#define SUPERHIRES  0x0020   /* 1280 pixel mode (ECS+) */
#define VP_HIDE     0x2000   /* viewport is hidden */
```

---

## Building a Display

```c
struct View view;
struct ViewPort vp;
struct RasInfo ri;
struct BitMap *bm = AllocBitMap(320, 256, 5, BMF_DISPLAYABLE|BMF_CLEAR, NULL);

InitView(&view);
InitVPort(&vp);
view.ViewPort = &vp;
vp.RasInfo = &ri;
ri.BitMap = bm;
vp.DWidth = 320;
vp.DHeight = 256;
vp.Modes = 0;   /* lores */

/* Build colour map: */
vp.ColorMap = GetColorMap(32);

/* Compile to copper: */
MakeVPort(&view, &vp);
MrgCop(&view);

/* Activate: */
LoadView(&view);
WaitTOF();

/* Cleanup: */
LoadView(GfxBase->ActiView);  /* restore system view */
FreeVPortCopLists(&vp);
FreeCprList(view.LOFCprList);
FreeColorMap(vp.ColorMap);
FreeBitMap(bm);
```

---

## References

- NDK39: `graphics/view.h`
- ADCD 2.1: `InitView`, `InitVPort`, `MakeVPort`, `MrgCop`, `LoadView`
- HRM: display construction chapter
