[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Core Concepts

## Naming Conventions

MUI uses a strict prefix system defined in `libraries/mui.h`. Every identifier type has its own prefix:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `MUIC_` | Class name | `MUIC_Area`, `MUIC_Window` |
| `MUIM_` | Method | `MUIM_Draw`, `MUIM_AskMinMax` |
| `MUIP_` | Method parameter structure | `MUIP_Draw`, `MUIP_AskMinMax` |
| `MUIV_` | Special method/attribute value | `MUIV_Application_ReturnID_Quit` |
| `MUIA_` | Attribute | `MUIA_Window_Title` |
| `MUIE_` | Error return code | `MUIE_OutOfMemory` |
| `MUII_` | Standard MUI image | `MUII_BACKGROUND`, `MUII_SHADOW` |
| `MUIX_` | Control code for text strings | `MUIX_C` (center), `MUIX_B` (bold) |
| `MUIO_` | Object type for `MUI_MakeObject()` | `MUIO_Button`, `MUIO_HBar` |

Learning these prefixes makes reading MUI code significantly easier.

## Attributes

Attributes are the properties of MUI objects. Each attribute definition in `libraries/mui.h` is followed by a comment with the letters **I**, **S**, and/or **G**:

- **I** - Can be specified at object creation time
- **S** - Can be changed later with `SetAttrs()` or the `set()` macro
- **G** - Can be read with `GetAttr()` or the `get()` macro

Example:

```c
#define MUIA_Window_Title 0x8042c21d /* ISG */
```

This means `MUIA_Window_Title` can be set at creation, changed later, and queried at any time.

### Setting Attributes

At creation time, attributes are passed as tag-value pairs:

```c
app = ApplicationObject,
    MUIA_Application_Title, "MyApp",
    MUIA_Application_Base , "MYAPP",
    TAG_DONE;
```

After creation, use `set()`:

```c
set(window, MUIA_Window_Open, TRUE);
```

Or use `SetAttrs()` directly:

```c
SetAttrs(window, MUIA_Window_Open, TRUE, TAG_DONE);
```

### Getting Attributes

```c
ULONG is_open;
get(window, MUIA_Window_Open, &is_open);
```

## Object Creation Macros

MUI provides convenience macros that look like function calls but expand into `NewObject()` calls with the appropriate class and tags. These macros make code readable and maintainable.

### Common Creation Macros

```c
/* Application and Window */
ApplicationObject, ... , TAG_DONE;
WindowObject, ... , TAG_DONE;

/* Groups */
VGroup, ... , End;
HGroup, ... , End;
GroupObject, ... , End;

/* Widgets */
TextObject, ... , End;
StringObject, ... , End;
ListviewObject, ... , End;
ListObject, ... , End;
SliderObject, ... , End;
CycleObject, ... , End;
RadioObject, ... , End;
GaugeObject, ... , End;
ScaleObject, ... , End;
ImageObject, ... , End;
BitmapObject, ... , End;
ColorfieldObject, ... , End;
PaletteObject, ... , End;

/* Popups */
PopstringObject, ... , End;
PopaslObject, ... , End;
PopobjectObject, ... , End;
PoplistObject, ... , End;

/* Special helpers */
SimpleButton("Label")
HSpace(x)
VSpace(x)
```

The pattern is consistent: the macro name corresponds to the class, attributes follow as tag-value pairs, and the object is terminated with `End` or `TAG_DONE`.

## Tag-Based Construction

MUI objects are created using the Amiga tag system. Tags are 32-bit values where the upper bits identify the attribute and the lower bits hold the value (or a pointer).

```c
app = ApplicationObject,
    MUIA_Application_Title      , "Demo",
    MUIA_Application_Version    , "$VER: Demo 1.0",
    MUIA_Application_Copyright  , "1997 Author",
    MUIA_Application_Author     , "Author",
    MUIA_Application_Description, "A demo program",
    MUIA_Application_Base       , "DEMO",
    SubWindow, window = WindowObject,
        MUIA_Window_Title, "Demo Window",
        MUIA_Window_ID   , MAKE_ID('D','E','M','O'),
        WindowContents, VGroup,
            Child, TextObject,
                TextFrame,
                MUIA_Background, MUII_TextBack,
                MUIA_Text_Contents, "Hello",
                End,
            End,
        End,
    End;
```

Notice how nesting works: `ApplicationObject` contains `SubWindow`, which contains `WindowObject`, which contains `WindowContents`, which contains a `VGroup`, which contains `Child` widgets.

## Methods

Methods are operations you perform on objects. The universal way to invoke a method is `DoMethod()`:

```c
DoMethod(obj, MUIM_MethodName, arg1, arg2, ...);
```

### Common Methods

| Method | Purpose |
|--------|---------|
| `MUIM_Application_NewInput` | Process input events (preferred loop) |
| `MUIM_Application_Input` | Process input events (legacy loop) |
| `MUIM_Application_ReturnID` | Trigger a return ID |
| `MUIM_Notify` | Set up attribute notifications |
| `MUIM_CallHook` | Invoke a callback hook |
| `MUIM_Set` | Set an attribute (method form) |
| `MUIM_Get` | Get an attribute (method form) |
| `MUIM_Draw` | Render an object |
| `MUIM_AskMinMax` | Query minimum/maximum sizes |

## Object Lifecycle

### Creation

Objects are created with the macro constructors. The constructor returns a pointer or `NULL` on failure.

```c
APTR obj = TextObject,
    MUIA_Text_Contents, "Hello",
    End;

if (!obj)
    /* handle error */;
```

### Usage

Objects are manipulated through attributes and methods. They exist within a parent container (usually a Group) which manages their layout and visibility.

### Disposal

When an object is no longer needed, dispose it:

```c
MUI_DisposeObject(obj);
```

For the top-level Application object, disposing it automatically disposes all child Windows and their contents. This is the normal shutdown pattern:

```c
MUI_DisposeObject(app);  /* disposes entire tree */
```

For custom classes, you must also delete the class itself:

```c
MUI_DeleteCustomClass(mcc);
```

## The `Child` Keyword

When adding widgets to a Group, the `Child` tag is used to introduce each child object:

```c
VGroup,
    Child, widget1,
    Child, widget2,
    Child, HGroup,
        Child, subwidget1,
        Child, subwidget2,
        End,
    End,
```

`Child` is not a macro for a class; it is a tag that tells the Group class to add the following object to its internal list of children.

## Special Attribute Values

MUI defines several special values used across multiple attributes:

| Value | Meaning |
|-------|---------|
| `MUIV_EveryTime` | Trigger notification on any attribute change |
| `MUIV_TriggerValue` | Pass the triggering value as an argument |
| `MUIV_Notification_Value` | Use the value from the notification setup |

These are used primarily with `MUIM_Notify` to create flexible event bindings.

---

Previous: [Getting Started](03-getting-started.md)
Next: [Layout System](05-layout-system.md)
