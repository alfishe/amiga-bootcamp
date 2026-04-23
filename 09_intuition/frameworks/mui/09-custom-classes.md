[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Custom Classes

## Why Create Custom Classes?

Custom classes let you encapsulate reusable behavior and rendering. Instead of writing the same notification setup and hook logic repeatedly, you create a class that handles everything internally. Examples include:

- A custom chart or graph widget
- A specialized list with drag-and-drop rules
- A rendering area with custom graphics
- A compound widget that bundles multiple controls

Custom classes are standard BOOPSI classes with MUI-specific methods.

## Creating a Custom Class

### Step 1: Define Instance Data

Instance data is a structure that holds per-object state. MUI allocates it for each object automatically.

```c
struct MyData
{
    LONG dummy;
    /* add your own fields here */
};
```

### Step 2: Implement Methods

At minimum, most visual custom classes implement two methods:

- `MUIM_AskMinMax` - Report size requirements
- `MUIM_Draw` - Render the object

#### AskMinMax

Called before layout. You must add your size requirements to what the superclass already calculated.

```c
SAVEDS ULONG mAskMinMax(struct IClass *cl, Object *obj, struct MUIP_AskMinMax *msg)
{
    /* Let superclass fill in base values (frame, spacing, etc.) */
    DoSuperMethodA(cl, obj, msg);

    /* Add our own requirements */
    msg->MinMaxInfo->MinWidth  += 100;
    msg->MinMaxInfo->DefWidth  += 120;
    msg->MinMaxInfo->MaxWidth  += 500;

    msg->MinMaxInfo->MinHeight += 40;
    msg->MinMaxInfo->DefHeight += 90;
    msg->MinMaxInfo->MaxHeight += 300;

    return 0;
}
```

Important: Use `+=` to add to the superclass values, not `=` to replace them.

#### Draw

Called whenever MUI needs you to render.

```c
SAVEDS ULONG mDraw(struct IClass *cl, Object *obj, struct MUIP_Draw *msg)
{
    int i;

    /* Let superclass draw frame, background, etc. */
    DoSuperMethodA(cl, obj, msg);

    /* If MADF_DRAWOBJECT isn't set, don't draw content */
    if (!(msg->flags & MADF_DRAWOBJECT))
        return 0;

    /* Render within the object's rectangle */
    SetAPen(_rp(obj), _dri(obj)->dri_Pens[TEXTPEN]);

    for (i = _mleft(obj); i <= _mright(obj); i += 5)
    {
        Move(_rp(obj), _mleft(obj), _mbottom(obj));
        Draw(_rp(obj), i, _mtop(obj));
        Move(_rp(obj), _mright(obj), _mbottom(obj));
        Draw(_rp(obj), i, _mtop(obj));
    }

    return 0;
}
```

Key macros for rendering:

| Macro | Meaning |
|-------|---------|
| `_rp(obj)` | RastPort for drawing |
| `_dri(obj)` | DrawInfo (pens, fonts) |
| `_mleft(obj)` | Left edge of render area |
| `_mtop(obj)` | Top edge of render area |
| `_mright(obj)` | Right edge of render area |
| `_mbottom(obj)` | Bottom edge of render area |
| `_mwidth(obj)` | Width of render area |
| `_mheight(obj)` | Height of render area |

### Step 3: Create the Dispatcher

The dispatcher is a switch statement that routes methods to your handlers.

```c
SAVEDS ASM ULONG MyDispatcher(REG(a0) struct IClass *cl,
                               REG(a2) Object *obj,
                               REG(a1) Msg msg)
{
    switch (msg->MethodID)
    {
        case MUIM_AskMinMax: return mAskMinMax(cl, obj, (APTR)msg);
        case MUIM_Draw:      return mDraw(cl, obj, (APTR)msg);
    }

    return DoSuperMethodA(cl, obj, msg);
}
```

Unknown methods are passed to the superclass via `DoSuperMethodA()`.

### Step 4: Register the Class

```c
struct MUI_CustomClass *mcc;

mcc = MUI_CreateCustomClass(NULL,      /* library base (usually NULL) */
                            MUIC_Area, /* superclass */
                            NULL,      /* private data (usually NULL) */
                            sizeof(struct MyData),
                            MyDispatcher);

if (!mcc)
    fail(NULL, "Could not create custom class.");
```

`MUI_CreateCustomClass` returns a `struct MUI_CustomClass *`, not a raw `struct IClass *`. The `mcc_Class` member contains the actual class pointer for `NewObject()`.

### Step 5: Use the Class

```c
MyObj = NewObject(mcc->mcc_Class, NULL,
    TextFrame,
    MUIA_Background, MUII_BACKGROUND,
    TAG_DONE);
```

### Step 6: Cleanup

When your application exits, delete the custom class:

```c
MUI_DeleteCustomClass(mcc);
```

Do this after disposing all objects of that class.

## Complete Minimal Custom Class Example

```c
#include "demo.h"

struct MyData
{
    LONG dummy;
};

SAVEDS ULONG mAskMinMax(struct IClass *cl, Object *obj, struct MUIP_AskMinMax *msg)
{
    DoSuperMethodA(cl, obj, msg);

    msg->MinMaxInfo->MinWidth  += 100;
    msg->MinMaxInfo->DefWidth  += 120;
    msg->MinMaxInfo->MaxWidth  += 500;
    msg->MinMaxInfo->MinHeight += 40;
    msg->MinMaxInfo->DefHeight += 90;
    msg->MinMaxInfo->MaxHeight += 300;

    return 0;
}

SAVEDS ULONG mDraw(struct IClass *cl, Object *obj, struct MUIP_Draw *msg)
{
    DoSuperMethodA(cl, obj, msg);

    if (!(msg->flags & MADF_DRAWOBJECT))
        return 0;

    SetAPen(_rp(obj), _dri(obj)->dri_Pens[TEXTPEN]);
    RectFill(_rp(obj), _mleft(obj), _mtop(obj), _mright(obj), _mbottom(obj));

    return 0;
}

SAVEDS ASM ULONG MyDispatcher(REG(a0) struct IClass *cl,
                               REG(a2) Object *obj,
                               REG(a1) Msg msg)
{
    switch (msg->MethodID)
    {
        case MUIM_AskMinMax: return mAskMinMax(cl, obj, (APTR)msg);
        case MUIM_Draw:      return mDraw(cl, obj, (APTR)msg);
    }
    return DoSuperMethodA(cl, obj, msg);
}

int main(int argc, char *argv[])
{
    APTR app, window, MyObj;
    struct MUI_CustomClass *mcc;

    init();

    mcc = MUI_CreateCustomClass(NULL, MUIC_Area, NULL,
                                sizeof(struct MyData), MyDispatcher);
    if (!mcc)
        fail(NULL, "Could not create custom class.");

    app = ApplicationObject,
        MUIA_Application_Title, "CustomClassDemo",
        ...
        SubWindow, window = WindowObject,
            ...
            WindowContents, VGroup,
                Child, MyObj = NewObject(mcc->mcc_Class, NULL,
                    TextFrame,
                    MUIA_Background, MUII_BACKGROUND,
                    TAG_DONE),
                End,
            End,
        End;

    if (!app)
        fail(app, "Failed to create Application.");

    DoMethod(window, MUIM_Notify, MUIA_Window_CloseRequest, TRUE,
        app, 2, MUIM_Application_ReturnID, MUIV_Application_ReturnID_Quit);

    set(window, MUIA_Window_Open, TRUE);

    {
        ULONG sigs = 0;
        while (DoMethod(app, MUIM_Application_NewInput, &sigs)
               != MUIV_Application_ReturnID_Quit)
        {
            if (sigs)
            {
                sigs = Wait(sigs | SIGBREAKF_CTRL_C);
                if (sigs & SIGBREAKF_CTRL_C) break;
            }
        }
    }

    set(window, MUIA_Window_Open, FALSE);
    MUI_DisposeObject(app);
    MUI_DeleteCustomClass(mcc);
    fail(NULL, NULL);
}
```

## Advanced Custom Class Methods

Beyond `AskMinMax` and `Draw`, custom classes often implement:

| Method | Purpose |
|--------|---------|
| `OM_NEW` | Initialize instance data when object is created |
| `OM_DISPOSE` | Clean up instance data before deletion |
| `OM_SET` | Handle attribute changes |
| `OM_GET` | Handle attribute queries |
| `MUIM_Setup` | Prepare for rendering (allocate resources) |
| `MUIM_Cleanup` | Release rendering resources |
| `MUIM_HandleEvent` | Handle raw input events |
| `MUIM_DragQuery` | Accept or reject drag operations |
| `MUIM_DragDrop` | Handle dropped objects |

## Inheritance Notes

- `DoSuperMethodA()` forwards a method to the superclass with the original message
- `DoSuperMethod()` forwards with a variable argument list
- `DoSuperNew()` is a helper for forwarding `OM_NEW` with tag lists
- Always call the superclass first in `AskMinMax` and `Draw` unless you intend to completely replace its behavior

---

Previous: [Menus](08-menus.md)
Next: [Events and Notifications](10-events-and-notifications.md)
