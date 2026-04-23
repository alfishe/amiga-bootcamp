[← Home](../README.md) · [Intuition](README.md)

# Screens — OpenScreen, CloseScreen, SA_ Tags

## Overview

An Amiga **Screen** is a complete display context: a `ViewPort` with its own `BitMap`, colour palette, and resolution. Multiple screens can coexist and be dragged up/down to reveal each other.

---

## Screen Types

| Type | Constant | Description |
|---|---|---|
| Workbench | `WBENCHSCREEN` | The default desktop screen |
| Custom | `CUSTOMSCREEN` | Application-owned screen |
| Public | `PUBLICSCREEN` | Named screen other apps can open windows on |

---

## Opening a Screen (OS 2.0+ TagList)

```c
struct Screen *scr = OpenScreenTags(NULL,
    SA_Width,       640,
    SA_Height,      256,
    SA_Depth,       4,           /* 16 colours */
    SA_DisplayID,   HIRES_KEY,
    SA_Title,       "My Screen",
    SA_ShowTitle,   TRUE,
    SA_Type,        CUSTOMSCREEN,
    SA_Pens,        (ULONG)~0,  /* use 3D pen defaults */
    SA_Font,        &topaz8,
    TAG_DONE);
```

### Common SA_ Tags

| Tag | Description |
|---|---|
| `SA_Width`, `SA_Height` | Screen dimensions |
| `SA_Depth` | Bitplane count (1–8) |
| `SA_DisplayID` | ModeID from display database |
| `SA_Title` | Title bar text |
| `SA_ShowTitle` | Show/hide title bar |
| `SA_Type` | `CUSTOMSCREEN`, `PUBLICSCREEN` |
| `SA_Behind` | Open behind other screens |
| `SA_Quiet` | No title bar at all |
| `SA_AutoScroll` | Allow autoscrolling |
| `SA_Overscan` | Overscan type (`OSCAN_TEXT`, `OSCAN_STANDARD`, `OSCAN_MAX`) |
| `SA_Pens` | DrawInfo pen array (3D look) |
| `SA_Interleaved` | Use interleaved bitmap |
| `SA_Colors32` | 32-bit colour palette |
| `SA_PubName` | Public screen name |

---

## Closing

```c
CloseScreen(scr);
/* All windows must be closed first! */
```

---

## Public Screens

```c
/* Open a public screen: */
struct Screen *pub = OpenScreenTags(NULL,
    SA_Type,    PUBLICSCREEN,
    SA_PubName, "MYAPP",
    SA_Title,   "My Public Screen",
    TAG_DONE);
PubScreenStatus(pub, 0);  /* make it available */

/* From another process, open a window on it: */
struct Screen *found = LockPubScreen("MYAPP");
struct Window *win = OpenWindowTags(NULL,
    WA_PubScreen, found,
    WA_Title, "On MYAPP",
    TAG_DONE);
UnlockPubScreen(NULL, found);
```

---

## References

- NDK39: `intuition/screens.h`, `intuition/intuition.h`
- ADCD 2.1: `OpenScreenTagList`, `CloseScreen`, `LockPubScreen`
