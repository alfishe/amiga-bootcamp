[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Menus

## Menu System Architecture

MUI's menu system consists of three class types:

| Class | Role |
|-------|------|
| `Menustrip` | Root container holding all menus |
| `Menu` | A single pull-down menu (e.g., "Project") |
| `Menuitem` | An individual item within a menu |

A Menustrip is attached to either a specific Window (via `MUIA_Window_Menustrip`) or to the Application (via `MUIA_Application_Menustrip`). When attached to the Application, all windows inherit the menu unless overridden.

## Using GadTools NewMenu

The easiest way to define menus is with the familiar GadTools `NewMenu` structure. MUI converts this into its own object tree automatically.

### Define the Menu Structure

```c
enum {
    MEN_PROJECT = 1,
    MEN_ABOUT,
    MEN_QUIT,
    MEN_EDIT,
    MEN_CUT,
    MEN_COPY,
    MEN_PASTE
};

static struct NewMenu MenuData[] = {
    { NM_TITLE, "Project" , 0, 0, 0, (APTR)MEN_PROJECT },
    { NM_ITEM , "About...", "?", 0, 0, (APTR)MEN_ABOUT   },
    { NM_ITEM , NM_BARLABEL, 0, 0, 0, (APTR)0            },
    { NM_ITEM , "Quit"    , "Q", 0, 0, (APTR)MEN_QUIT    },

    { NM_TITLE, "Edit"    , 0, 0, 0, (APTR)MEN_EDIT     },
    { NM_ITEM , "Cut"     , "X", 0, 0, (APTR)MEN_CUT      },
    { NM_ITEM , "Copy"    , "C", 0, 0, (APTR)MEN_COPY     },
    { NM_ITEM , "Paste"   , "V", 0, 0, (APTR)MEN_PASTE    },

    { NM_END, NULL, 0, 0, 0, (APTR)0 },
};
```

### Create and Attach the Menu

```c
app = ApplicationObject,
    ...
    SubWindow, win = WindowObject,
        MUIA_Window_Title    , "Menus",
        MUIA_Window_ID       , MAKE_ID('M','E','N','1'),
        MUIA_Window_Menustrip, strip = MUI_MakeObject(MUIO_MenustripNM, MenuData, 0),
        WindowContents, VGroup,
            ...
            End,
        End,
    End;
```

`MUI_MakeObject(MUIO_MenustripNM, MenuData, 0)` parses the `NewMenu` array and returns a Menustrip object.

## Handling Menu Selections

### Method 1: Return IDs in the Input Loop

Each menu item's `UserData` becomes its Return ID. In the main loop, check for it:

```c
while (running)
{
    switch (DoMethod(app, MUIM_Application_Input, &signals))
    {
        case MUIV_Application_ReturnID_Quit:
            running = FALSE;
            break;

        case MEN_ABOUT:
            /* show about box */
            break;

        case MEN_CUT:
            /* perform cut */
            break;
    }

    if (running && signals)
        Wait(signals);
}
```

### Method 2: Notifications

Bind menu items directly to actions using `MUIM_Notify`:

```c
APTR aboutItem;

/* Find the item using its userdata */
aboutItem = (APTR)DoMethod(strip, MUIM_FindUserData, MEN_ABOUT);

if (aboutItem)
{
    DoMethod(aboutItem, MUIM_Notify, MUIA_Menuitem_Trigger, MUIV_EveryTime,
        app, 2, MUIM_Application_ReturnID, MEN_ABOUT);
}
```

### Method 3: Hooks

For more complex actions, use `MUIM_CallHook`:

```c
SAVEDS ASM LONG AboutFunc(REG(a2) APTR obj, REG(a1) APTR msg)
{
    MUI_Request(app, win, 0, "About", "*OK",
        "MyApp\nVersion 1.0\nBy Author");
    return 0;
}

static struct Hook AboutHook = { {0,0}, (VOID *)AboutFunc, NULL, NULL };

/* In setup: */
DoMethod(aboutItem, MUIM_Notify, MUIA_Menuitem_Trigger, MUIV_EveryTime,
    app, 3, MUIM_CallHook, &AboutHook, MUIV_TriggerValue);
```

## Dynamic Menu Manipulation

### Enabling and Disabling Items

```c
/* Disable a menu item */
set(menuItem, MUIA_Menuitem_Enabled, FALSE);

/* Enable it again */
set(menuItem, MUIA_Menuitem_Enabled, TRUE);
```

### Checkmarks and Radio Groups

Use standard GadTools flags in the `NewMenu` structure:

```c
#define RB CHECKIT

static struct NewMenu MenuData[] = {
    { NM_TITLE, "Settings"                 , 0 ,0             ,0,(APTR)MEN_SETTINGS },
    { NM_ITEM , "Hardware"                , 0 ,NM_ITEMDISABLED,0,(APTR)MEN_HARDWARE },
    { NM_SUB  ,   "A1000"                  ,"1",RB|CHECKED,2|4|8 ,(APTR)MEN_A1000    },
    { NM_SUB  ,   "A2000"                  ,"2",RB         ,1|4|8 ,(APTR)MEN_A2000    },
    { NM_SUB  ,   "A3000"                  ,"3",RB         ,1|2|8 ,(APTR)MEN_A3000    },
    { NM_SUB  ,   "A4000"                  ,"4",RB         ,1|2|4 ,(APTR)MEN_A4000    },
    { NM_END  , NULL                       , 0 ,0             ,0,(APTR)0            },
};
```

`CHECKIT` makes the item checkable. `CHECKED` pre-checks it. The mutual exclude field (e.g., `2|4|8`) defines radio groups: items with overlapping bits cannot be checked simultaneously.

### Toggle Items

Use `MENUTOGGLE` for items that toggle on/off independently:

```c
#define TG CHECKIT|MENUTOGGLE

{ NM_SUB, "Option", "O", TG, 0, (APTR)MEN_OPTION },
```

## Creating Menus Programmatically

Instead of `NewMenu`, you can build the menu tree manually:

```c
MUIA_Window_Menustrip, MenustripObject,
    Child, MenuObject,
        MUIA_Menu_Title, "Project",
        Child, MenuitemObject,
            MUIA_Menuitem_Title, "About...",
            MUIA_Menuitem_Shortcut, "?",
            End,
        Child, MenuitemObject,
            MUIA_Menuitem_Title, NM_BARLABEL,
            End,
        Child, MenuitemObject,
            MUIA_Menuitem_Title, "Quit",
            MUIA_Menuitem_Shortcut, "Q",
            End,
        End,
    End,
```

This is more verbose but gives you direct access to every menu item object for notifications.

## Menu Best Practices

- Always provide keyboard shortcuts for common actions
- Use `NM_BARLABEL` to separate logical groups
- Keep the `NewMenu` userdata values unique across the entire menu
- Attach menus to the Application if all windows share the same menu
- Attach menus to individual Windows only when menus differ per window
- Use `MUIM_FindUserData` on the Menustrip to locate individual items for notifications

---

Previous: [Windows and Applications](07-windows-and-applications.md)
Next: [Custom Classes](09-custom-classes.md)
