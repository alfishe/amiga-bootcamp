[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Windows and Applications

## The Application Object

Every MUI program needs exactly one Application object. It is the root of the object tree and manages:

- All windows (via `SubWindow`)
- The program's identity (title, version, author)
- The main input loop
- Iconification and AppMessage handling
- Return ID dispatching

### Creating an Application

```c
app = ApplicationObject,
    MUIA_Application_Title      , "MyApp",
    MUIA_Application_Version    , "$VER: MyApp 1.0 (01.01.97)",
    MUIA_Application_Copyright  , "1997 Author Name",
    MUIA_Application_Author     , "Author Name",
    MUIA_Application_Description, "Description of what this does",
    MUIA_Application_Base       , "MYAPP",

    SubWindow, window = WindowObject,
        MUIA_Window_Title, "Main Window",
        MUIA_Window_ID   , MAKE_ID('M','A','I','N'),
        WindowContents, VGroup,
            /* widgets */
            End,
        End,

    End;
```

### Application Attributes

| Attribute | Description |
|-----------|-------------|
| `MUIA_Application_Title` | Program title shown in system exchanges |
| `MUIA_Application_Version` | Version string, conventionally `$VER: Name Version (Date)` |
| `MUIA_Application_Copyright` | Copyright notice |
| `MUIA_Application_Author` | Author name |
| `MUIA_Application_Description` | Short description |
| `MUIA_Application_Base` | Base name for disk object, ARexx port, etc. |
| `MUIA_Application_Window` | Alternative to `SubWindow` for adding windows |
| `MUIA_Application_DropObject` | Object to receive icons dropped on app icon |

## The Window Object

Windows are children of the Application. Each Window contains a single root widget specified with `WindowContents`.

### Window Attributes

| Attribute | Description |
|-----------|-------------|
| `MUIA_Window_Title` | Window title bar text |
| `MUIA_Window_ID` | Four-byte identifier for state persistence |
| `MUIA_Window_Open` | Open or close the window (ISG) |
| `MUIA_Window_Screen` | Public screen to open on |
| `MUIA_Window_Menustrip` | Menu strip for this window |
| `MUIA_Window_AppWindow` | Accept Workbench icons (TRUE/FALSE) |
| `MUIA_Window_NoMenus` | Disable menus for this window |
| `MUIA_Window_ActiveObject` | Object to receive initial activation |
| `MUIA_Window_CloseRequest` | Set when user clicks close gadget (triggers notification) |

### Opening and Closing

```c
/* Open the window */
set(window, MUIA_Window_Open, TRUE);

/* Later, close it */
set(window, MUIA_Window_Open, FALSE);
```

Always close windows before disposing the Application.

## SubWindow vs Standalone Windows

The `SubWindow` tag inside `ApplicationObject` both creates the window and registers it with the application in one step. This is the recommended pattern:

```c
app = ApplicationObject,
    ...
    SubWindow, window = WindowObject, ... , End,
    SubWindow, window2 = WindowObject, ... , End,
    End;
```

Alternatively, you can create windows separately and add them later with `MUIA_Application_Window`, but `SubWindow` is more common in examples.

## Multiple Windows

An application can have multiple windows. Each window can be opened and closed independently:

```c
app = ApplicationObject,
    ...
    SubWindow, mainWin = WindowObject,
        MUIA_Window_Title, "Main",
        MUIA_Window_ID   , MAKE_ID('M','A','I','N'),
        ...
        End,

    SubWindow, helpWin = WindowObject,
        MUIA_Window_Title, "Help",
        MUIA_Window_ID   , MAKE_ID('H','E','L','P'),
        ...
        End,
    End;
```

Each window should have a unique `MUIA_Window_ID` so MUI can save and restore its position and size.

## AppWindows

An AppWindow accepts icons dragged from Workbench. Enable it with `MUIA_Window_AppWindow`:

```c
WindowObject,
    MUIA_Window_Title    , "Drop icons on me!",
    MUIA_Window_ID       , MAKE_ID('A','P','P','W'),
    MUIA_Window_AppWindow, TRUE,
    ...
    End,
```

When an icon is dropped, the object that received it gets an `AppMessage`. You can handle this with a notification:

```c
SAVEDS ASM LONG AppMsgFunc(REG(a2) APTR obj, REG(a1) struct AppMessage **x)
{
    struct AppMessage *amsg = *x;
    struct WBArg *ap;
    int i;
    static char buf[256];

    for (ap = amsg->am_ArgList, i = 0; i < amsg->am_NumArgs; i++, ap++)
    {
        NameFromLock(ap->wa_Lock, buf, sizeof(buf));
        AddPart(buf, ap->wa_Name, sizeof(buf));
        DoMethod(obj, MUIM_List_Insert, &buf, 1, MUIV_List_Insert_Bottom);
    }
    return 0;
}

static const struct Hook AppMsgHook = {
    { NULL, NULL }, (VOID *)AppMsgFunc, NULL, NULL
};

/* In setup: */
DoMethod(lv1, MUIM_Notify, MUIA_AppMessage, MUIV_EveryTime,
    lv1, 3, MUIM_CallHook, &AppMsgHook, MUIV_TriggerValue);
```

### DropObject

When the application is iconified, icons dropped on its AppIcon can be routed to a specific object:

```c
set(app, MUIA_Application_DropObject, targetList);
```

## Iconification

MUI handles iconification automatically. When the user clicks the zoom gadget (or uses the menu item), the application window closes and an AppIcon appears on Workbench. Pressing the AppIcon restores the window.

You can react to iconification state changes via notifications on `MUIA_Application_Iconified`.

## Window State Persistence

MUI automatically saves window positions and sizes using the `MUIA_Window_ID`. The ID is a four-byte value conventionally created with `MAKE_ID`:

```c
#define MAKE_ID(a,b,c,d) ((ULONG)(a)<<24 | (ULONG)(b)<<16 | (ULONG)(c)<<8 | (ULONG)(d))

MUIA_Window_ID, MAKE_ID('M','A','I','N'),
```

Each window in your application should have a unique ID. MUI stores positions in the `ENV:` directory.

## Common Window Patterns

### Centered Dialog

```c
WindowObject,
    MUIA_Window_Title, "Confirm",
    MUIA_Window_ID   , MAKE_ID('C','N','F','M'),
    MUIA_Window_Width, MUIV_Window_Width_MinMax(20),
    WindowContents, VGroup,
        Child, TextObject,
            TextFrame,
            MUIA_Text_Contents, "\33cAre you sure?",
            End,
        Child, HGroup,
            Child, SimpleButton("Yes"),
            Child, SimpleButton("No"),
            End,
        End,
    End,
```

### Modal Window

MUI does not have a built-in modal window concept, but you can simulate it by disabling input on the main window and running a sub-loop for the dialog window.

---

Previous: [Widgets Overview](06-widgets-overview.md)
Next: [Menus](08-menus.md)
