[← Home](../README.md) · [Intuition](README.md)

# Windows — OpenWindow, IDCMP, WA_ Tags

## Overview

A **Window** is a rectangular region on a Screen where an application renders and receives input. Windows are managed by Intuition and provide title bars, borders, close/zoom/depth gadgets, sizing, and IDCMP message delivery.

---

## Opening a Window (OS 2.0+)

```c
struct Window *win = OpenWindowTags(NULL,
    WA_Left,        50,
    WA_Top,         30,
    WA_Width,       400,
    WA_Height,      200,
    WA_Title,       "My Window",
    WA_Flags,       WFLG_CLOSEGADGET | WFLG_DRAGBAR | WFLG_DEPTHGADGET |
                    WFLG_SIZEGADGET | WFLG_ACTIVATE | WFLG_GIMMEZEROZERO,
    WA_IDCMP,       IDCMP_CLOSEWINDOW | IDCMP_MOUSEBUTTONS | IDCMP_VANILLAKEY,
    WA_CustomScreen, myScreen,
    TAG_DONE);
```

### Common WA_ Tags

| Tag | Description |
|---|---|
| `WA_Left`, `WA_Top` | Position |
| `WA_Width`, `WA_Height` | Size |
| `WA_MinWidth`, `WA_MaxWidth` | Size limits |
| `WA_Title` | Window title string |
| `WA_Flags` | `WFLG_*` flags |
| `WA_IDCMP` | IDCMP class mask |
| `WA_CustomScreen` | Screen to open on |
| `WA_PubScreen` | Public screen to open on |
| `WA_SuperBitMap` | Use super-bitmap scrolling |
| `WA_Gadgets` | First gadget in chain |
| `WA_Checkmark` | Custom checkmark image |
| `WA_Borderless` | No borders |

---

## Window Flags (`WFLG_*`)

```c
#define WFLG_SIZEGADGET    (1<<0)
#define WFLG_DRAGBAR       (1<<1)
#define WFLG_DEPTHGADGET   (1<<2)
#define WFLG_CLOSEGADGET   (1<<3)
#define WFLG_SIZEBRIGHT    (1<<4)   /* right-side sizing */
#define WFLG_SIZEBBOTTOM   (1<<5)
#define WFLG_SMART_REFRESH (0)       /* refresh type */
#define WFLG_SIMPLE_REFRESH (1<<6)
#define WFLG_SUPER_BITMAP  (1<<7)
#define WFLG_BACKDROP      (1<<8)
#define WFLG_REPORTMOUSE   (1<<9)
#define WFLG_GIMMEZEROZERO (1<<10)   /* inner area starts at 0,0 */
#define WFLG_BORDERLESS    (1<<11)
#define WFLG_ACTIVATE      (1<<12)
#define WFLG_RMBTRAP       (1<<16)   /* trap right-button clicks */
#define WFLG_NOCAREREFRESH (1<<17)
```

---

## Event Loop

```c
BOOL running = TRUE;
while (running) {
    WaitPort(win->UserPort);
    struct IntuiMessage *imsg;
    while ((imsg = (struct IntuiMessage *)GetMsg(win->UserPort))) {
        switch (imsg->Class) {
            case IDCMP_CLOSEWINDOW:
                running = FALSE;
                break;
            case IDCMP_VANILLAKEY:
                Printf("Key: %lc\n", imsg->Code);
                break;
        }
        ReplyMsg((struct Message *)imsg);
    }
}
CloseWindow(win);
```

---

## References

- NDK39: `intuition/intuition.h`
- ADCD 2.1: `OpenWindowTagList`, `CloseWindow`
- `09_intuition/idcmp.md` — IDCMP message classes
