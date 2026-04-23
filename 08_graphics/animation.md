[← Home](../README.md) · [Graphics](README.md)

# Animation — GEL System: BOBs, VSprites, AnimObs

## Overview

The **GEL (Graphics ELement)** system provides high-level animated sprite and bitmap overlay support. It manages VSprites (virtual sprites that can use hardware or software rendering), BOBs (Blitter OBjects — arbitrary-sized bitmaps overlaid on a playfield), and AnimObs (animation objects with sequencing).

---

## VSprite

```c
/* graphics/gels.h — NDK39 */
struct VSprite {
    struct VSprite *NextVSprite;
    struct VSprite *PrevVSprite;
    struct VSprite *DrawPath;
    struct VSprite *ClearPath;
    WORD   OldY, OldX;        /* previous position */
    WORD   Flags;              /* VSPRITE, SAVEBACK, OVERLAY, MUSTDRAW */
    WORD   Y, X;               /* current position */
    WORD   Height;
    WORD   Width;              /* width in words */
    WORD   Depth;
    WORD   MeMask;             /* collision mask */
    WORD   HitMask;
    WORD   *ImageData;         /* sprite image */
    WORD   *BorderLine;        /* collision border */
    WORD   *CollMask;          /* collision mask data */
    WORD   *SprColors;         /* colour table */
    struct Bob *VSBob;         /* if this VSprite backs a BOB */
    BYTE   PlanePick;
    BYTE   PlaneOnOff;
    /* ... */
};
```

---

## BOB (Blitter Object)

```c
struct Bob {
    WORD   Flags;
    WORD   *SaveBuffer;       /* background save buffer */
    WORD   *ImageShadow;      /* shadow mask for cookie-cut */
    struct Bob *Before;
    struct Bob *After;
    struct VSprite *BobVSprite; /* associated VSprite */
    struct AnimComp *BobComp;   /* if part of animation */
    struct DBufPacket *DBuffer; /* double-buffer packet */
};
```

---

## Usage Pattern

```c
struct GelsInfo gi;
struct VSprite headVS, tailVS;

/* Initialise GEL system: */
InitGels(&headVS, &tailVS, &gi);
rp->GelsInfo = &gi;

/* Add a VSprite/BOB: */
AddVSprite(&myVSprite, rp);
/* or */
AddBob(&myBob, rp);

/* Each frame: */
SortGList(rp);       /* sort by Y position */
DrawGList(rp, &vp);  /* render all GELs */
WaitTOF();           /* sync to vertical blank */

/* Cleanup: */
RemVSprite(&myVSprite);
/* or */
RemBob(&myBob);
```

---

## AnimOb — Animation Sequences

```c
struct AnimOb {
    struct AnimOb *NextOb;
    struct AnimOb *PrevOb;
    LONG   Clock;           /* frame counter */
    WORD   AnOldY, AnOldX;
    WORD   AnY, AnX;        /* current position */
    WORD   YVel, XVel;      /* velocity */
    WORD   YAccel, XAccel;  /* acceleration */
    WORD   RingYTrans;      /* ring buffer Y translation */
    WORD   RingXTrans;
    struct AnimComp *HeadComp; /* component chain */
    /* ... */
};
```

---

## References

- NDK39: `graphics/gels.h`, `graphics/gelsinternal.h`
- ADCD 2.1: `InitGels`, `AddVSprite`, `AddBob`, `SortGList`, `DrawGList`
- *Amiga ROM Kernel Reference Manual: Libraries* — GELs chapter
