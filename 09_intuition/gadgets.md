[← Home](../README.md) · [Intuition](README.md)

# Gadgets

## What Is a Gadget?

A gadget is Intuition's fundamental interactive UI element — the Amiga equivalent of a widget, control, or component. Every button, checkbox, slider, text field, and scrollbar in an Amiga application is a gadget. Gadgets handle their own rendering, hit-testing, and state management, delivering results to the application via [IDCMP](idcmp.md) messages.

The gadget system evolved through three major generations:

| Generation | Era | API | Key Feature |
|---|---|---|---|
| **Raw Intuition** | 1985 (OS 1.x) | `struct Gadget` + manual imagery | Full control, maximum boilerplate |
| **GadTools** | 1990 (OS 2.0) | `CreateGadget()` + `NewGadget` | Standard OS look-and-feel with minimal code |
| **[BOOPSI](boopsi.md)** | 1990 (OS 2.0) | `NewObject()` + OOP dispatchers | Object-oriented, interconnectable, extensible |

Most applications should use **GadTools** for standard UI or **BOOPSI** for custom behavior. Raw Intuition gadgets are only necessary for OS 1.x compatibility or extreme customization.

---

## Gadget Types

### System Gadgets

Built into every window — controlled by `WA_Flags`:

| Gadget | Flag | IDCMP Event | Description |
|---|---|---|---|
| Close | `WFLG_CLOSEGADGET` | `IDCMP_CLOSEWINDOW` | "×" button — window close request |
| Depth | `WFLG_DEPTHGADGET` | — (handled by Intuition) | Front/back toggle |
| Zoom | `WFLG_HASZOOM` | — | Alternate-size toggle (OS 2.0+) |
| Drag | `WFLG_DRAGBAR` | — | Title bar drag area |
| Size | `WFLG_SIZEGADGET` | `IDCMP_NEWSIZE` | Resize handle |

### Application Gadgets

Created by the application and attached to windows:

| Type | GadTools Kind | Description | IDCMP |
|---|---|---|---|
| **Button** | `BUTTON_KIND` | Click action | `IDCMP_GADGETUP` |
| **Checkbox** | `CHECKBOX_KIND` | Boolean toggle | `IDCMP_GADGETUP` |
| **Cycle** | `CYCLE_KIND` | Drop-down selector (cycles through options) | `IDCMP_GADGETUP` |
| **Integer** | `INTEGER_KIND` | Numeric text field | `IDCMP_GADGETUP` |
| **ListView** | `LISTVIEW_KIND` | Scrollable list of items | `IDCMP_GADGETUP` |
| **MX** (Mutual Exclude) | `MX_KIND` | Radio button group | `IDCMP_GADGETUP` |
| **Number** | `NUMBER_KIND` | Read-only numeric display | — |
| **Palette** | `PALETTE_KIND` | Color picker from screen palette | `IDCMP_GADGETUP` |
| **Scroller** | `SCROLLER_KIND` | Scrollbar | `IDCMP_GADGETUP` / `MOUSEMOVE` |
| **Slider** | `SLIDER_KIND` | Horizontal/vertical value slider | `IDCMP_GADGETUP` / `MOUSEMOVE` |
| **String** | `STRING_KIND` | Text input field | `IDCMP_GADGETUP` |
| **Text** | `TEXT_KIND` | Read-only text display | — |

---

## GadTools — Standard Gadget Creation (OS 2.0+)

### Setup

GadTools requires a **VisualInfo** handle (ties gadgets to a specific screen's look):

```c
#include <libraries/gadtools.h>
#include <proto/gadtools.h>

struct Library *GadToolsBase = OpenLibrary("gadtools.library", 39);
struct Screen *scr = LockPubScreen(NULL);
APTR vi = GetVisualInfo(scr, TAG_DONE);
```

### Creating a Gadget List

GadTools gadgets are created in a **linked list** using a context pointer:

```c
struct Gadget *glist = NULL;
struct Gadget *gad;

/* Initialize the context — creates a hidden "anchor" gadget */
gad = CreateContext(&glist);

/* Define gadget layout */
struct NewGadget ng = {
    .ng_LeftEdge   = 20,
    .ng_TopEdge    = 30,
    .ng_Width      = 200,
    .ng_Height     = 14,
    .ng_GadgetText = "Name:",
    .ng_TextAttr   = &topaz8,
    .ng_GadgetID   = GAD_NAME,
    .ng_Flags      = PLACETEXT_LEFT,
    .ng_VisualInfo = vi,
};

/* String gadget */
gad = CreateGadget(STRING_KIND, gad, &ng,
    GTST_MaxChars, 64,
    GTST_String,   "Default",
    TAG_DONE);

/* Button below it */
ng.ng_TopEdge += 20;
ng.ng_GadgetText = "OK";
ng.ng_GadgetID = GAD_OK;
ng.ng_Flags = PLACETEXT_IN;

gad = CreateGadget(BUTTON_KIND, gad, &ng, TAG_DONE);

/* Attach to window */
struct Window *win = OpenWindowTags(NULL,
    WA_Title,    "GadTools Demo",
    WA_Gadgets,  glist,       /* Attach gadget list */
    WA_IDCMP,    IDCMP_CLOSEWINDOW | IDCMP_GADGETUP |
                 IDCMP_REFRESHWINDOW,
    WA_Flags,    WFLG_CLOSEGADGET | WFLG_DRAGBAR |
                 WFLG_DEPTHGADGET | WFLG_ACTIVATE |
                 WFLG_SMART_REFRESH,
    TAG_DONE);

/* Render gadget borders (required for GadTools!) */
GT_RefreshWindow(win, NULL);
```

### Event Handling

```c
struct IntuiMessage *msg;
while ((msg = GT_GetIMsg(win->UserPort)))
{
    ULONG class = msg->Class;
    UWORD code  = msg->Code;
    struct Gadget *gad = (struct Gadget *)msg->IAddress;

    GT_ReplyIMsg(msg);

    switch (class)
    {
        case IDCMP_GADGETUP:
            switch (gad->GadgetID)
            {
                case GAD_NAME:
                {
                    /* Read string value */
                    STRPTR name;
                    GT_GetGadgetAttrs(gad, win, NULL,
                        GTST_String, &name, TAG_DONE);
                    Printf("Name: %s\n", name);
                    break;
                }
                case GAD_OK:
                    running = FALSE;
                    break;
            }
            break;

        case IDCMP_REFRESHWINDOW:
            GT_BeginRefresh(win);
            GT_EndRefresh(win, TRUE);
            break;
    }
}
```

### Cleanup

```c
/* Order matters: window first, then gadgets, then visual info */
CloseWindow(win);
FreeGadgets(glist);
FreeVisualInfo(vi);
UnlockPubScreen(NULL, scr);
CloseLibrary(GadToolsBase);
```

---

## Updating Gadget State at Runtime

### GadTools Gadgets

```c
/* Update a slider value */
GT_SetGadgetAttrs(sliderGad, win, NULL,
    GTSL_Level, 75,
    TAG_DONE);

/* Disable a button */
GT_SetGadgetAttrs(okGad, win, NULL,
    GA_Disabled, TRUE,
    TAG_DONE);

/* Read current value */
LONG level;
GT_GetGadgetAttrs(sliderGad, win, NULL,
    GTSL_Level, &level,
    TAG_DONE);
```

### Raw Intuition Gadgets

For non-GadTools gadgets, you must manually remove/re-add to avoid rendering glitches:

```c
/* Remove gadget from window */
UWORD pos = RemoveGadget(win, myGadget);

/* Modify gadget fields */
myGadget->Flags |= GFLG_DISABLED;

/* Re-add at same position */
AddGadget(win, myGadget, pos);

/* Refresh the display */
RefreshGList(myGadget, win, NULL, 1);
```

---

## Raw Intuition Gadgets (struct Gadget)

For cases where GadTools or BOOPSI are insufficient — direct hardware-level control:

### struct Gadget

```c
struct Gadget {
    struct Gadget  *NextGadget;     /* Linked list */
    WORD            LeftEdge, TopEdge;
    WORD            Width, Height;
    UWORD           Flags;          /* GFLG_* */
    UWORD           Activation;     /* GACT_* */
    UWORD           GadgetType;     /* GTYP_* */
    APTR            GadgetRender;   /* Image or Border for normal state */
    APTR            SelectRender;   /* Image or Border for selected state */
    struct IntuiText *GadgetText;   /* Label */
    LONG            MutualExclude;
    APTR            SpecialInfo;    /* StringInfo, PropInfo, etc. */
    UWORD           GadgetID;       /* Application-defined ID */
    APTR            UserData;       /* Application-defined pointer */
};
```

### Gadget Flags (GFLG_*)

| Flag | Value | Description |
|---|---|---|
| `GFLG_GADGHCOMP` | `0x0000` | Highlight by complementing select box |
| `GFLG_GADGHBOX` | `0x0001` | Highlight by drawing box around gadget |
| `GFLG_GADGHIMAGE` | `0x0002` | Use `SelectRender` image when selected |
| `GFLG_GADGHNONE` | `0x0003` | No highlighting |
| `GFLG_GADGIMAGE` | `0x0004` | `GadgetRender` is `struct Image *`, not `struct Border *` |
| `GFLG_RELBOTTOM` | `0x0008` | Position relative to bottom edge |
| `GFLG_RELRIGHT` | `0x0010` | Position relative to right edge |
| `GFLG_RELWIDTH` | `0x0020` | Width relative to window width |
| `GFLG_RELHEIGHT` | `0x0040` | Height relative to window height |
| `GFLG_SELECTED` | `0x0080` | Gadget is currently selected |
| `GFLG_DISABLED` | `0x0100` | Gadget is grayed out / inactive |

### Activation Flags (GACT_*)

| Flag | Value | Description |
|---|---|---|
| `GACT_RELVERIFY` | `0x0001` | Send `IDCMP_GADGETUP` only if mouse released inside |
| `GACT_IMMEDIATE` | `0x0002` | Send `IDCMP_GADGETDOWN` on press |
| `GACT_ENDGADGET` | `0x0004` | Deactivate requester when gadget released |
| `GACT_FOLLOWMOUSE` | `0x0008` | Report mouse while gadget is active |
| `GACT_TOGGLESELECT` | `0x0100` | Toggle selected state on each click |
| `GACT_LONGINT` | `0x0800` | String gadget contains a long integer |

### Gadget Types (GTYP_*)

| Type | Value | SpecialInfo | Description |
|---|---|---|---|
| `GTYP_BOOLGADGET` | `0x0001` | — | Simple click button |
| `GTYP_STRGADGET` | `0x0004` | `struct StringInfo *` | Text input field |
| `GTYP_PROPGADGET` | `0x0003` | `struct PropInfo *` | Proportional (slider/scrollbar) |
| `GTYP_CUSTOMGADGET` | `0x0005` | Class-specific | BOOPSI custom class |

---

## Proportional (Slider) Gadgets

Prop gadgets are used for scrollbars and sliders. They have their own state structure:

```c
struct PropInfo {
    UWORD  Flags;        /* AUTOKNOB, FREEHORIZ, FREEVERT */
    UWORD  HorizPot;     /* Horizontal position (0–0xFFFF) */
    UWORD  VertPot;      /* Vertical position (0–0xFFFF) */
    UWORD  HorizBody;    /* Horizontal knob size (0–0xFFFF) */
    UWORD  VertBody;     /* Vertical knob size (0–0xFFFF) */
    /* ... internal fields ... */
};

/* Calculate body size for a scrollbar:
   visible = number of visible items
   total   = total number of items */
UWORD body = (visible >= total) ? MAXBODY
           : (UWORD)((ULONG)MAXBODY * visible / total);

/* Calculate pot (position) from current top item:
   top = first visible item index */
UWORD pot = (total <= visible) ? 0
          : (UWORD)((ULONG)MAXPOT * top / (total - visible));
```

---

## String Gadgets

Text input gadgets use `StringInfo`:

```c
UBYTE buffer[128] = "Default text";
UBYTE undoBuffer[128];

struct StringInfo si = {
    .Buffer      = buffer,
    .UndoBuffer  = undoBuffer,
    .BufferPos   = 0,
    .MaxChars    = sizeof(buffer),
};

/* Read the result after GADGETUP: */
Printf("User entered: %s\n", si.Buffer);
```

With GadTools, this is much simpler:

```c
gad = CreateGadget(STRING_KIND, gad, &ng,
    GTST_MaxChars, 128,
    GTST_String,   "Default text",
    TAG_DONE);
```

---

## Relative Positioning

Gadgets can be positioned relative to window edges — they automatically move when the window resizes:

```c
/* Scrollbar on the right edge */
myGadget.LeftEdge = -16;    /* 16 pixels from right */
myGadget.TopEdge  = 0;
myGadget.Width    = 16;
myGadget.Height   = -16;    /* Extends to 16px from bottom */
myGadget.Flags    = GFLG_RELRIGHT | GFLG_RELHEIGHT;
```

| Flag | Effect |
|---|---|
| `GFLG_RELRIGHT` | `LeftEdge` is offset from right edge (use negative values) |
| `GFLG_RELBOTTOM` | `TopEdge` is offset from bottom edge |
| `GFLG_RELWIDTH` | `Width` is added to window width |
| `GFLG_RELHEIGHT` | `Height` is added to window height |

---

## Pitfalls

### 1. Forgetting GT_RefreshWindow

GadTools gadgets won't render properly without the initial `GT_RefreshWindow(win, NULL)` call. The window appears to have no gadgets.

### 2. Using GetMsg Instead of GT_GetIMsg

GadTools internally sends messages for gadget sub-events (e.g., ListView scrolling). Using `GetMsg()` directly breaks GadTools' internal state machine.

### 3. Modifying Gadgets Without Remove/Add

Changing a raw gadget's position, flags, or imagery while it's attached to a window causes rendering corruption. Always `RemoveGadget()` → modify → `AddGadget()` → `RefreshGList()`.

### 4. Not Setting GACT_RELVERIFY

Without `GACT_RELVERIFY`, the application never receives `IDCMP_GADGETUP`. The gadget appears to "eat" clicks silently.

### 5. String Gadget Buffer Overrun

The `MaxChars` field includes the null terminator. If your buffer is 64 bytes, set `MaxChars` to 64 (not 63). The gadget handles null termination.

---

## Best Practices

1. **Use GadTools** for standard UI — it provides the correct OS look-and-feel automatically
2. **Use `GT_GetIMsg()`/`GT_ReplyIMsg()`** — never mix raw `GetMsg()` with GadTools
3. **Always call `GT_RefreshWindow()`** after opening a window with GadTools gadgets
4. **Free in reverse order**: `CloseWindow()` → `FreeGadgets()` → `FreeVisualInfo()` → `UnlockPubScreen()`
5. **Use `GA_Disabled`** to gray out gadgets instead of removing them — maintains layout stability
6. **Set `PLACETEXT_LEFT/RIGHT/ABOVE`** for label placement — don't hardcode text positions
7. **Handle `IDCMP_REFRESHWINDOW`** with `GT_BeginRefresh()`/`GT_EndRefresh()`
8. **Give every gadget a unique `GadgetID`** — this is how you identify the source in `IDCMP_GADGETUP`

---

## References

- NDK 3.9: `intuition/intuition.h`, `intuition/gadgetclass.h`, `libraries/gadtools.h`
- ADCD 2.1: `CreateGadget()`, `GT_SetGadgetAttrs()`, `GT_GetGadgetAttrs()`
- AmigaOS Reference Manual (RKRM): Libraries, Chapter 7 — Gadgets
- See also: [BOOPSI](boopsi.md), [IDCMP](idcmp.md), [Windows](windows.md)
