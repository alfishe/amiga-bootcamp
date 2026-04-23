[← Home](../README.md) · [Intuition](README.md)

# IDCMP — IntuiMessage Classes

## Overview

**IDCMP** (Intuition Direct Communication Message Ports) is the mechanism by which Intuition delivers input events to windows. Each window has a `UserPort` (MsgPort) where `IntuiMessage` structures are queued.

---

## struct IntuiMessage

```c
/* intuition/intuition.h — NDK39 */
struct IntuiMessage {
    struct Message   ExecMessage;
    ULONG            Class;        /* IDCMP_* class */
    UWORD            Code;         /* class-specific code */
    UWORD            Qualifier;    /* key/mouse qualifiers */
    APTR             IAddress;     /* class-specific address (e.g. gadget) */
    WORD             MouseX;       /* mouse X relative to window */
    WORD             MouseY;       /* mouse Y relative to window */
    ULONG            Seconds;      /* timestamp seconds */
    ULONG            Micros;       /* timestamp microseconds */
    struct Window   *IDCMPWindow;  /* window that received this */
    struct IntuiMessage *SpecialLink;
};
```

---

## IDCMP Class Constants

| Constant | Hex | Description |
|---|---|---|
| `IDCMP_SIZEVERIFY` | `$0001` | Window is about to be resized |
| `IDCMP_NEWSIZE` | `$0002` | Window was resized |
| `IDCMP_REFRESHWINDOW` | `$0004` | Window needs refresh |
| `IDCMP_MOUSEBUTTONS` | `$0008` | Mouse button pressed/released |
| `IDCMP_MOUSEMOVE` | `$0010` | Mouse moved (if REPORTMOUSE) |
| `IDCMP_GADGETDOWN` | `$0020` | Gadget pressed |
| `IDCMP_GADGETUP` | `$0040` | Gadget released |
| `IDCMP_REQSET` | `$0080` | Requester activated |
| `IDCMP_MENUPICK` | `$0100` | Menu item selected |
| `IDCMP_CLOSEWINDOW` | `$0200` | Close gadget clicked |
| `IDCMP_RAWKEY` | `$0400` | Raw keyboard event |
| `IDCMP_REQVERIFY` | `$0800` | Requester about to open |
| `IDCMP_REQCLEAR` | `$1000` | Requester closed |
| `IDCMP_MENUVERIFY` | `$2000` | Menu about to open |
| `IDCMP_NEWPREFS` | `$4000` | Preferences changed |
| `IDCMP_DISKINSERTED` | `$8000` | Disk inserted |
| `IDCMP_DISKREMOVED` | `$10000` | Disk removed |
| `IDCMP_ACTIVEWINDOW` | `$40000` | Window activated |
| `IDCMP_INACTIVEWINDOW` | `$80000` | Window deactivated |
| `IDCMP_DELTAMOVE` | `$100000` | Delta mouse movement |
| `IDCMP_VANILLAKEY` | `$200000` | Translated ASCII keypress |
| `IDCMP_INTUITICKS` | `$400000` | ~10Hz timer tick |
| `IDCMP_IDCMPUPDATE` | `$800000` | BOOPSI gadget update |
| `IDCMP_CHANGEWINDOW` | `$2000000` | Window moved/resized |

---

## Qualifier Flags

| Constant | Hex | Description |
|---|---|---|
| `IEQUALIFIER_LSHIFT` | `$0001` | Left Shift |
| `IEQUALIFIER_RSHIFT` | `$0002` | Right Shift |
| `IEQUALIFIER_CAPSLOCK` | `$0004` | Caps Lock |
| `IEQUALIFIER_CONTROL` | `$0008` | Control |
| `IEQUALIFIER_LALT` | `$0010` | Left Alt |
| `IEQUALIFIER_RALT` | `$0020` | Right Alt |
| `IEQUALIFIER_LCOMMAND` | `$0040` | Left Amiga |
| `IEQUALIFIER_RCOMMAND` | `$0080` | Right Amiga |
| `IEQUALIFIER_LEFTBUTTON` | `$4000` | LMB |
| `IEQUALIFIER_MIDBUTTON` | `$1000` | MMB |
| `IEQUALIFIER_RBUTTON` | `$8000` | RMB (not standard) |

---

## References

- NDK39: `intuition/intuition.h`, `devices/inputevent.h`
- ADCD 2.1: IDCMP reference
