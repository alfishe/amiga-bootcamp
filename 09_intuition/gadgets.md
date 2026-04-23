[← Home](../README.md) · [Intuition](README.md)

# Gadgets — GadTools and BOOPSI

## Overview

Intuition gadgets are the UI controls: buttons, string fields, sliders, checkboxes, listviews, etc. OS 2.0+ provides **GadTools** (high-level toolkit) and **BOOPSI** (object-oriented framework).

---

## GadTools Gadget Types

| Kind | Constant | Description |
|---|---|---|
| Button | `BUTTON_KIND` | Simple push button |
| Checkbox | `CHECKBOX_KIND` | Toggle on/off |
| Integer | `INTEGER_KIND` | Numeric entry field |
| Listview | `LISTVIEW_KIND` | Scrollable list |
| MX | `MX_KIND` | Mutually exclusive (radio buttons) |
| Number | `NUMBER_KIND` | Read-only number display |
| Cycle | `CYCLE_KIND` | Pop-up cycle selector |
| Palette | `PALETTE_KIND` | Colour picker |
| Scroller | `SCROLLER_KIND` | Scroll bar |
| Slider | `SLIDER_KIND` | Value slider |
| String | `STRING_KIND` | Text entry field |
| Text | `TEXT_KIND` | Read-only text display |

---

## Creating a GadTools Layout

```c
struct Screen *scr = LockPubScreen(NULL);
APTR vi = GetVisualInfo(scr, TAG_DONE);
struct Gadget *glist = NULL;
struct NewGadget ng;
struct Gadget *gad = CreateContext(&glist);

ng.ng_LeftEdge   = 20;
ng.ng_TopEdge    = 30;
ng.ng_Width      = 100;
ng.ng_Height     = 14;
ng.ng_GadgetText = "OK";
ng.ng_GadgetID   = 1;
ng.ng_VisualInfo = vi;
ng.ng_Flags      = 0;
ng.ng_TextAttr   = NULL;

gad = CreateGadget(BUTTON_KIND, gad, &ng, TAG_DONE);

ng.ng_TopEdge += 20;
ng.ng_GadgetText = "Cancel";
ng.ng_GadgetID   = 2;
gad = CreateGadget(BUTTON_KIND, gad, &ng, TAG_DONE);

/* Open window with gadgets: */
struct Window *win = OpenWindowTags(NULL,
    WA_Gadgets, glist,
    WA_IDCMP,   IDCMP_GADGETUP | IDCMP_CLOSEWINDOW | BUTTONIDCMP,
    /* ... */
    TAG_DONE);

/* Event loop: */
/* on IDCMP_GADGETUP: */
/*   struct Gadget *gad = (struct Gadget *)imsg->IAddress; */
/*   switch (gad->GadgetID) { case 1: ... case 2: ... } */

/* Cleanup: */
CloseWindow(win);
FreeGadgets(glist);
FreeVisualInfo(vi);
UnlockPubScreen(NULL, scr);
```

---

## BOOPSI (Basic Object-Oriented Programming System for Intuition)

BOOPSI provides class-based gadgets with message dispatch:

```c
/* Create a BOOPSI string gadget: */
Object *strObj = NewObject(NULL, "strgclass",
    GA_Left,     20,
    GA_Top,      50,
    GA_Width,    200,
    GA_Height,   14,
    GA_ID,       3,
    STRINGA_Buffer, myBuffer,
    STRINGA_MaxChars, 64,
    TAG_DONE);

/* Add to window: */
AddGadget(win, (struct Gadget *)strObj, -1);
RefreshGadgets((struct Gadget *)strObj, win, NULL);

/* Cleanup: */
RemoveGadget(win, (struct Gadget *)strObj);
DisposeObject(strObj);
```

---

## References

- NDK39: `libraries/gadtools.h`, `intuition/classusr.h`
- ADCD 2.1: `CreateGadget`, `CreateContext`, `GetVisualInfo`
