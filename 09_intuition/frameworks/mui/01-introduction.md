[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Introduction

## What is MUI?

MUI (Magic User Interface) is a system for generating and maintaining graphical user interfaces on Amiga computers. Created by Stefan Stuntz between 1992 and 1997, it provides an object-oriented framework built on top of AmigaOS's native BOOPSI (Basic Object-Oriented Programming System for Intuition) subsystem.

MUI's defining characteristic is that end users can customize the appearance of any MUI application through a central preferences program. Developers define the structure and behavior; users control the visual style.

## Key Features

- **Object-oriented design** - Every UI element is an object with attributes and methods
- **BOOPSI integration** - Inherits from and extends AmigaOS's native class system
- **User customization** - Skinnable via the MUI preferences program without code changes
- **Layout management** - Automatic and custom layout systems handle widget positioning
- **Notification system** - Declarative event binding between objects
- **Comprehensive widget set** - Text, strings, lists, sliders, buttons, gauges, palettes, and more
- **Custom class support** - Developers can create reusable components by subclassing existing classes

## MUI in the Amiga Software Stack

```
+---------------------------+
|     Your Application      |
+---------------------------+
|           MUI             |
|  (classes, layout, events)|
+---------------------------+
|         BOOPSI            |
|  (Intuition classes)      |
+---------------------------+
|       Intuition           |
|  (windows, input)         |
+---------------------------+
|       Graphics            |
|  (drawing, rastports)     |
+---------------------------+
|        Exec               |
|  (tasks, signals)         |
+---------------------------+
```

### BOOPSI (Basic Object-Oriented Programming System for Intuition)

BOOPSI is AmigaOS's native object system introduced in AmigaOS 2.0 (V37). It provides the foundational mechanisms that MUI extends:

- **Class registry** - BOOPSI maintains a system-wide database of classes via `AddClass()` and `FindClass()`
- **Object instantiation** - Objects are created with `NewObjectA()` using tag-based attribute lists
- **Method dispatch** - Methods are invoked through `DoMethod()`, which routes calls through a class dispatcher
- **Inheritance** - Classes specify a superclass and inherit methods and default attributes

MUI's entire class hierarchy (Notify, Area, Group, Window, Application, etc.) is built as a BOOPSI class tree. Every MUI object is a BOOPSI object. When you call `DoMethod(obj, MUIM_Draw, ...)` you are using BOOPSI dispatch. When MUI creates objects internally, it calls `NewObjectA()` against its own class IDs. The `libraries/mui.h` header defines `MUIC_*` constants that resolve to BOOPSI class names registered with Intuition.

MUI adds three major capabilities on top of BOOPSI:

1. **Layout engine** - BOOPSI has no concept of automatic layout; MUI's Group classes compute sizes and positions
2. **Notification system** - BOOPSI has no built-in attribute monitoring; MUI's `MUIM_Notify` adds declarative event binding
3. **Extended attribute system** - MUI standardizes attribute naming (MUIA_*) and documents I/S/G flags

### Intuition

Intuition is AmigaOS's windowing and input subsystem. It is the layer below BOOPSI and the direct interface to the display hardware through the Graphics library.

MUI's relationship to Intuition:

- **Windows** - MUI's Window class creates and manages an Intuition window internally. You never call `OpenWindowTagList()` directly; MUI handles it when you set `MUIA_Window_Open` to `TRUE`. The `WindowObject` macro configures Intuition window properties (title, ID, screen) through MUI attributes.
- **Input handling** - Intuition captures mouse and keyboard events and routes them through its IDCMP (Intuition Direct Communication Message Port) system. MUI intercepts these events at the Window level and dispatches them to the appropriate widget via `MUIM_HandleEvent` or attribute changes.
- **Gadgets** - Intuition provides basic gadget types (boolean, string, proportional). MUI's Gadget subclass wraps Intuition gadgets but replaces their rendering and behavior with MUI's own system. The Boopsi class allows embedding native BOOPSI gadgets inside MUI layouts.
- **Screens** - MUI windows open on Intuition screens. You can specify a public screen with `MUIA_Window_Screen` or let MUI use the default Workbench screen.
- **RastPorts** - When a custom class renders in `MUIM_Draw`, it draws into an Intuition RastPort obtained via MUI's `_rp(obj)` macro. MUI manages clipping, layer locking, and damage regions.

Key Intuition structures you encounter when reading MUI code:

| Structure | Role in MUI |
|-----------|-------------|
| `struct Window` | Underlying Intuition window managed by MUI Window class |
| `struct RastPort` | Drawing context for custom rendering |
| `struct DrawInfo` | Pen colors and fonts via `_dri(obj)` |
| `struct Screen` | Display surface for windows |
| `struct Gadget` | Base structure for Intuition gadgets |

### GadTools

GadTools is AmigaOS's higher-level widget library built on top of Intuition gadgets. It provides standardized buttons, checkboxes, sliders, and menus with a consistent look.

MUI's relationship to GadTools:

- **Menu compatibility** - MUI can consume GadTools `NewMenu` structures directly via `MUI_MakeObject(MUIO_MenustripNM, newmenu, 0)`. This parses the GadTools menu definition and converts it into MUI's own Menustrip/Menu/Menuitem object tree. This compatibility layer made it easy for existing applications to adopt MUI without rewriting menu code.
- **Gadget avoidance** - MUI generally does not use GadTools gadgets for its own widgets. MUI's Area, Text, String, and Button classes are fully independent implementations with their own rendering and input handling. This is why MUI widgets can be skinned through the MUI preferences program while GadTools gadgets have a fixed appearance.
- **Requesters** - MUI's Popasl class can invoke GadTools ASL (Amiga Standard Library) file and font requesters as popup subwindows.
- **Shared concepts** - Both GadTools and MUI use tag-based construction, so developers familiar with `GTTagList` patterns find MUI's `TAG_DONE` object creation intuitive.

The official MUI examples demonstrate the GadTools bridge explicitly in `Menus.c`, where a conventional `NewMenu` array is passed to MUI and then manipulated with MUI notifications.

### Summary of Dependencies

| Layer | What MUI Uses From It | What MUI Adds |
|-------|----------------------|---------------|
| **Exec** | Tasks, signals, memory allocation, message ports | Application event loop integration |
| **Graphics** | RastPort drawing, pens, regions, fonts | Automatic clipping and damage handling |
| **Intuition** | Windows, screens, IDCMP input, layers | Object-oriented window management |
| **BOOPSI** | Class registry, `NewObjectA()`, `DoMethodA()` | Layout, notification, extended attributes |
| **GadTools** | `NewMenu` structures, ASL requesters | Independent widget rendering and skinning |

## Version History

The material in this bootcamp corresponds to **MUI 3.8**, the developer release. Key version details:

- `muimaster.library` name and version requirements:
  - Minimum version: **V11** (`MUIMASTER_VMIN`)
  - Latest version at release: **V19** (`MUIMASTER_VLATEST`)
- Some macros in `libraries/mui.h` require V11 or above
- The developer package requires AmigaOS 2.0 (v37.175) include files and linker libraries

## Distribution and Licensing

MUI was distributed as shareware. The developer package (`mui38dev.lha`) contained autodocs, C examples, includes, and FD files. The user package (`mui38usr.lha`) contained the runtime libraries, preferences program, and demo applications.

Applications using MUI were encouraged to include a credit file indicating MUI usage.

## Why MUI Still Matters

For retrocomputing, emulation, and FPGA platforms like MiSTer, MUI remains relevant because:

- It represents one of the most sophisticated GUI toolkits available on classic Amiga hardware
- Its source code and examples demonstrate mature 1990s C and BOOPSI patterns
- Many Amiga applications were built with MUI and understanding it helps with porting and preservation
- The architecture influenced later GUI frameworks in its separation of structure from presentation

---

Next: [Architecture](02-architecture.md)
