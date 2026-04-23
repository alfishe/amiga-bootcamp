[← Home](../README.md) · [Intuition](README.md)

# Input Events — InputEvent, input.device, Commodities

## Overview

All user input (keyboard, mouse, joystick) flows through `input.device` as `InputEvent` structures. Commodities Exchange provides a high-level API for hotkeys and input filtering.

---

## struct InputEvent

```c
/* devices/inputevent.h — NDK39 */
struct InputEvent {
    struct InputEvent *ie_NextEvent;
    UBYTE   ie_Class;       /* IECLASS_* */
    UBYTE   ie_SubClass;
    UWORD   ie_Code;        /* keycode or button code */
    UWORD   ie_Qualifier;   /* IEQUALIFIER_* flags */
    union {
        struct { WORD ie_x, ie_y; } ie_xy;
        APTR   ie_addr;
        struct { UBYTE ie_prev1DownCode, ie_prev1DownQual;
                 UBYTE ie_prev2DownCode, ie_prev2DownQual; } ie_dead;
    } ie_position;
    struct timeval ie_TimeStamp;
};
```

---

## Event Classes

| Class | Constant | Description |
|---|---|---|
| `IECLASS_RAWKEY` | `$01` | Raw keyboard event |
| `IECLASS_RAWMOUSE` | `$02` | Raw mouse button/movement |
| `IECLASS_EVENT` | `$03` | Cooked event from Intuition |
| `IECLASS_POINTERPOS` | `$04` | Absolute pointer position |
| `IECLASS_TIMER` | `$06` | Timer event |
| `IECLASS_GADGETDOWN` | `$07` | Gadget pressed |
| `IECLASS_GADGETUP` | `$08` | Gadget released |
| `IECLASS_DISKINSERTED` | `$09` | Disk inserted |
| `IECLASS_DISKREMOVED` | `$0A` | Disk removed |
| `IECLASS_NEWPREFS` | `$0C` | Preferences changed |

---

## Commodities Exchange

```c
struct Library *CxBase = OpenLibrary("commodities.library", 37);

/* Create a hotkey filter: */
CxObj *broker = CxBroker(&nb, NULL);
CxObj *filter = CxFilter("ctrl alt d");        /* hotkey string */
CxObj *sender = CxSender(port, CX_HOTKEY_ID);  /* send msg to port */
AttachCxObj(filter, sender);
AttachCxObj(broker, filter);
ActivateCxObj(broker, TRUE);

/* In event loop: */
CxMsg *msg;
while ((msg = (CxMsg *)GetMsg(port))) {
    ULONG type = CxMsgType(msg);
    ULONG id   = CxMsgID(msg);
    ReplyMsg((struct Message *)msg);
    if (type == CXM_COMMAND && id == CXCMD_KILL) running = FALSE;
    if (type == CXM_IEVENT && id == CX_HOTKEY_ID) /* hotkey pressed */;
}

DeleteCxObjAll(broker);
CloseLibrary(CxBase);
```

---

## Input Handler Installation

```c
/* Add a custom input handler (runs in input.device context): */
struct Interrupt handler;
handler.is_Code = (APTR)myInputHandler;
handler.is_Data = myData;
handler.is_Node.ln_Pri = 51;  /* priority (above Intuition=50) */
handler.is_Node.ln_Name = "MyHandler";

struct IOStdReq *inputReq;
/* ... open input.device ... */
inputReq->io_Command = IND_ADDHANDLER;
inputReq->io_Data = &handler;
DoIO((struct IORequest *)inputReq);

/* Handler function: */
struct InputEvent * __saveds myInputHandler(
    struct InputEvent *events __asm("a0"),
    APTR data __asm("a1"))
{
    struct InputEvent *ev;
    for (ev = events; ev; ev = ev->ie_NextEvent) {
        if (ev->ie_Class == IECLASS_RAWKEY && ev->ie_Code == 0x45) {
            ev->ie_Class = IECLASS_NULL;  /* swallow ESC key */
        }
    }
    return events;
}
```

---

## References

- NDK39: `devices/inputevent.h`, `libraries/commodities.h`
- ADCD 2.1: `CxBroker`, `CxFilter`, `CxSender`, input.device
