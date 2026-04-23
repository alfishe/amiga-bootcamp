[← Home](../README.md) · [Intuition](README.md)

# BOOPSI — Basic Object-Oriented Programming System

## Overview

BOOPSI is AmigaOS's class-based object system for Intuition gadgets and images. Objects receive messages via `DoMethod()` and support inheritance and notification.

---

## Core Methods

| Method | Description |
|---|---|
| `OM_NEW` | Create new object |
| `OM_DISPOSE` | Destroy object |
| `OM_SET` | Set attributes |
| `OM_GET` | Get attributes |
| `OM_UPDATE` | Attribute changed notification |
| `OM_NOTIFY` | Send notification to targets |
| `GM_RENDER` | Render the gadget |
| `GM_GOACTIVE` | Gadget activated by user |
| `GM_HANDLEINPUT` | Process input while active |
| `GM_GOINACTIVE` | Gadget deactivated |

---

## Built-in Classes

| Class | Description |
|---|---|
| `rootclass` | Base class for all BOOPSI objects |
| `gadgetclass` | Base gadget class |
| `imageclass` | Base image class |
| `strgclass` | String entry gadget |
| `buttongclass` | Button gadget |
| `propgclass` | Proportional slider |
| `groupgclass` | Group container |
| `frbuttonclass` | Framed button |
| `frameiclass` | Frame image |
| `sysiclass` | System images (checkmark, etc.) |
| `icclass` | Interconnection (maps attributes) |
| `modelclass` | Model for MVC pattern |

---

## Creating and Using Objects

```c
Object *button = NewObject(NULL, "frbuttonclass",
    GA_Left,     20,
    GA_Top,      40,
    GA_Width,    100,
    GA_Height,   20,
    GA_Text,     "Click Me",
    GA_ID,       42,
    GA_RelVerify, TRUE,
    TAG_DONE);

AddGadget(win, (struct Gadget *)button, -1);
RefreshGadgets((struct Gadget *)button, win, NULL);

/* Set attribute: */
SetGadgetAttrs((struct Gadget *)button, win, NULL,
    GA_Disabled, TRUE,
    TAG_DONE);

/* Get attribute: */
ULONG value;
GetAttr(GA_Disabled, button, &value);

/* Cleanup: */
RemoveGadget(win, (struct Gadget *)button);
DisposeObject(button);
```

---

## Writing a Custom Class

```c
Class *myclass = MakeClass(NULL, "gadgetclass", NULL,
                           sizeof(struct MyData), 0);
myclass->cl_Dispatcher.h_Entry = (HOOKFUNC)myDispatcher;

ULONG myDispatcher(Class *cl, Object *o, Msg msg) {
    switch (msg->MethodID) {
        case OM_NEW:    return myNew(cl, o, (struct opSet *)msg);
        case OM_DISPOSE: return myDispose(cl, o, msg);
        case GM_RENDER: return myRender(cl, o, (struct gpRender *)msg);
        default:        return DoSuperMethodA(cl, o, msg);
    }
}
```

---

## References

- NDK39: `intuition/classusr.h`, `intuition/classes.h`
- ADCD 2.1: `NewObject`, `DisposeObject`, `SetAttrs`, `GetAttr`, `DoMethod`
