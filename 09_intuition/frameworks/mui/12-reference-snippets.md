[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Reference Snippets

Quick copy-paste templates for common MUI patterns.

## Table of Contents

- [Minimal Application Skeleton](#minimal-application-skeleton)
- [Window with Close Handler](#window-with-close-handler)
- [Vertical Layout with Text and Button](#vertical-layout-with-text-and-button)
- [Horizontal Button Row](#horizontal-button-row)
- [Listview with Strings](#listview-with-strings)
- [Slider with Value Display](#slider-with-value-display)
- [Cycle Gadget](#cycle-gadget)
- [Radio Buttons](#radio-buttons)
- [Notification Patterns](#notification-patterns)
- [Custom Class Boilerplate](#custom-class-boilerplate)
- [Menu Definition Template](#menu-definition-template)
- [Hook Function Template](#hook-function-template)
- [AppWindow Drag and Drop](#appwindow-drag-and-drop)
- [Input Loop Variants](#input-loop-variants)

## Minimal Application Skeleton

```c
#include <libraries/mui.h>
#include <clib/muimaster_protos.h>
#include <clib/exec_protos.h>
#include <clib/intuition_protos.h>
#include <pragmas/muimaster_pragmas.h>
#include <pragmas/exec_pragmas.h>
#include <pragmas/intuition_pragmas.h>
#include <stdio.h>
#include <stdlib.h>

struct Library *MUIMasterBase;
extern struct Library *SysBase;

int main(int argc, char *argv[])
{
    APTR app, window;

    if (!(MUIMasterBase = OpenLibrary(MUIMASTER_NAME, MUIMASTER_VMIN)))
        return 20;

    app = ApplicationObject,
        MUIA_Application_Title      , "App",
        MUIA_Application_Version    , "$VER: App 1.0",
        MUIA_Application_Copyright  , "Author",
        MUIA_Application_Author     , "Author",
        MUIA_Application_Description, "Description",
        MUIA_Application_Base       , "APP",

        SubWindow, window = WindowObject,
            MUIA_Window_Title, "Window",
            MUIA_Window_ID   , MAKE_ID('W','I','N','1'),
            WindowContents, VGroup,
                Child, TextObject,
                    MUIA_Text_Contents, "Hello MUI",
                    End,
                End,
            End,
        End;

    if (!app)
    {
        CloseLibrary(MUIMasterBase);
        return 20;
    }

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
    CloseLibrary(MUIMasterBase);
    return 0;
}
```

## Window with Close Handler

```c
DoMethod(window, MUIM_Notify, MUIA_Window_CloseRequest, TRUE,
    app, 2, MUIM_Application_ReturnID, MUIV_Application_ReturnID_Quit);
```

## Vertical Layout with Text and Button

```c
WindowContents, VGroup,
    Child, TextObject,
        TextFrame,
        MUIA_Background, MUII_TextBack,
        MUIA_Text_Contents, "\33cTitle",
        End,
    Child, StringObject,
        StringFrame,
        MUIA_String_Contents, "",
        End,
    Child, HGroup,
        Child, HSpace(0),
        Child, SimpleButton("OK"),
        Child, SimpleButton("Cancel"),
        Child, HSpace(0),
        End,
    End,
```

## Horizontal Button Row

```c
Child, HGroup,
    MUIA_Group_SameSize, TRUE,
    Child, SimpleButton("New"),
    Child, SimpleButton("Open"),
    Child, SimpleButton("Save"),
    Child, SimpleButton("Quit"),
    End,
```

## Listview with Strings

```c
APTR lv;

Child, lv = ListviewObject,
    MUIA_Listview_Input, TRUE,
    MUIA_Listview_List, ListObject,
        ReadListFrame,
        MUIA_List_ConstructHook, MUIV_List_ConstructHook_String,
        MUIA_List_DestructHook,  MUIV_List_DestructHook_String,
        End,
    End,

/* Insert items */
DoMethod(lv, MUIM_List_InsertSingle, "First", MUIV_List_Insert_Bottom);
DoMethod(lv, MUIM_List_InsertSingle, "Second", MUIV_List_Insert_Bottom);

/* Clear */
DoMethod(lv, MUIM_List_Clear);
```

## Slider with Value Display

```c
APTR slider, valueText;

Child, HGroup,
    Child, slider = SliderObject,
        MUIA_Numeric_Min, 0,
        MUIA_Numeric_Max, 100,
        MUIA_Numeric_Value, 50,
        MUIA_Slider_Horiz, TRUE,
        End,
    Child, valueText = TextObject,
        MUIA_Text_Contents, "50",
        End,
    End,

/* Sync slider to text */
DoMethod(slider, MUIM_Notify, MUIA_Numeric_Value, MUIV_EveryTime,
    valueText, 3, MUIM_Set, MUIA_Text_Contents, MUIV_TriggerValue);
```

## Cycle Gadget

```c
static char *choices[] = { "Low", "Medium", "High", NULL };

Child, CycleObject,
    MUIA_Cycle_Entries, choices,
    End,
```

## Radio Buttons

```c
static char *options[] = { "Option 1", "Option 2", "Option 3", NULL };

Child, RadioObject,
    MUIA_Radio_Entries, options,
    End,
```

## Notification Patterns

### Button Click -> Quit

```c
DoMethod(button, MUIM_Notify, MUIA_Pressed, FALSE,
    app, 2, MUIM_Application_ReturnID, MUIV_Application_ReturnID_Quit);
```

### Button Click -> Custom Return ID

```c
#define ID_SAVE 1

DoMethod(button, MUIM_Notify, MUIA_Pressed, FALSE,
    app, 2, MUIM_Application_ReturnID, ID_SAVE);
```

### Checkbox Enables/Disables Widget

```c
DoMethod(checkbox, MUIM_Notify, MUIA_Selected, TRUE,
    widget, 3, MUIM_Set, MUIA_Disabled, FALSE);

DoMethod(checkbox, MUIM_Notify, MUIA_Selected, FALSE,
    widget, 3, MUIM_Set, MUIA_Disabled, TRUE);
```

### String -> Window Title Sync

```c
DoMethod(string, MUIM_Notify, MUIA_String_Contents, MUIV_EveryTime,
    window, 3, MUIM_Set, MUIA_Window_Title, MUIV_TriggerValue);
```

## Custom Class Boilerplate

```c
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
    /* custom rendering here */
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

/* In main() */
struct MUI_CustomClass *mcc;
mcc = MUI_CreateCustomClass(NULL, MUIC_Area, NULL,
                            sizeof(struct MyData), MyDispatcher);
if (!mcc) /* handle error */;

APTR obj = NewObject(mcc->mcc_Class, NULL, TAG_DONE);

/* Cleanup */
MUI_DeleteCustomClass(mcc);
```

## Menu Definition Template

```c
enum { MEN_PROJECT=1, MEN_ABOUT, MEN_QUIT, MEN_EDIT, MEN_CUT, MEN_COPY, MEN_PASTE };

static struct NewMenu MenuData[] = {
    { NM_TITLE, "Project" , 0, 0, 0, (APTR)MEN_PROJECT },
    { NM_ITEM , "About...", "?", 0, 0, (APTR)MEN_ABOUT   },
    { NM_ITEM , NM_BARLABEL, 0, 0, 0, (APTR)0            },
    { NM_ITEM , "Quit"    , "Q", 0, 0, (APTR)MEN_QUIT    },
    { NM_TITLE, "Edit"    , 0, 0, 0, (APTR)MEN_EDIT     },
    { NM_ITEM , "Cut"     , "X", 0, 0, (APTR)MEN_CUT      },
    { NM_ITEM , "Copy"    , "C", 0, 0, (APTR)MEN_COPY     },
    { NM_ITEM , "Paste"   , "V", 0, 0, (APTR)MEN_PASTE    },
    { NM_END  , NULL      , 0, 0, 0, (APTR)0             },
};

/* Attach to window */
MUIA_Window_Menustrip, MUI_MakeObject(MUIO_MenustripNM, MenuData, 0),

/* Handle in loop */
case MEN_ABOUT: /* show about */ break;
case MEN_QUIT:  running = FALSE; break;
```

## Hook Function Template

```c
SAVEDS ASM LONG MyHookFunc(REG(a2) APTR obj, REG(a1) APTR param)
{
    /* obj = object that triggered the hook */
    /* param = argument from notification */
    return 0;
}

static struct Hook MyHook = {
    { NULL, NULL }, (VOID *)MyHookFunc, NULL, NULL
};

/* Usage in notification */
DoMethod(button, MUIM_Notify, MUIA_Pressed, FALSE,
    app, 3, MUIM_CallHook, &MyHook, MUIV_TriggerValue);
```

## AppWindow Drag and Drop

```c
/* Enable AppWindow */
WindowObject,
    MUIA_Window_Title    , "Drop Zone",
    MUIA_Window_ID       , MAKE_ID('D','R','O','P'),
    MUIA_Window_AppWindow, TRUE,
    ...
    End,

/* Hook to handle dropped icons */
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
        DoMethod(obj, MUIM_List_InsertSingle, buf, MUIV_List_Insert_Bottom);
    }
    return 0;
}

static const struct Hook AppMsgHook = {
    { NULL, NULL }, (VOID *)AppMsgFunc, NULL, NULL
};

/* Connect notification */
DoMethod(listview, MUIM_Notify, MUIA_AppMessage, MUIV_EveryTime,
    listview, 3, MUIM_CallHook, &AppMsgHook, MUIV_TriggerValue);
```

## Input Loop Variants

### Modern (Recommended)

```c
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
```

### Legacy with Return IDs

```c
ULONG signals;
BOOL running = TRUE;
while (running)
{
    switch (DoMethod(app, MUIM_Application_Input, &signals))
    {
        case MUIV_Application_ReturnID_Quit:
            running = FALSE;
            break;
        case ID_SAVE:
            /* handle save */
            break;
    }
    if (running && signals)
        Wait(signals);
}
```

### Legacy with Hooks (No Return IDs)

```c
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
/* All actions handled via MUIM_CallHook notifications */
```

---

Previous: [Advanced Patterns](11-advanced-patterns.md)
Back to [MUI Bootcamp](README.md)
