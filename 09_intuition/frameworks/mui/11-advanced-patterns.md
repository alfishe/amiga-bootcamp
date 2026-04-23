[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Advanced Patterns

## Drag and Drop

MUI supports drag and drop between listviews and custom objects. The drag source initiates the operation; the destination decides whether to accept it.

### Enabling Drag and Drop on Lists

```c
ListviewObject,
    MUIA_Listview_DragType, MUIV_Listview_DragType_Default,
    MUIA_Listview_List, ListObject,
        MUIA_List_DragSortable, TRUE,
        End,
    End,
```

`MUIA_List_DragSortable` allows the user to reorder list items by dragging.

### Custom Drag Query

For custom classes, implement `MUIM_DragQuery` to accept or reject drags:

```c
ULONG DragQuery(struct IClass *cl, Object *obj, struct MUIP_DragDrop *msg)
{
    if (msg->obj == obj)
    {
        /* Dragging onto ourselves - let superclass handle it */
        return DoSuperMethodA(cl, obj, msg);
    }
    else if (msg->obj == (Object *)muiUserData(obj))
    {
        /* Accept drags from our predefined source */
        return MUIV_DragQuery_Accept;
    }

    /* Reject everything else */
    return MUIV_DragQuery_Refuse;
}
```

Return values:

| Value | Meaning |
|-------|---------|
| `MUIV_DragQuery_Accept` | Accept the drag |
| `MUIV_DragQuery_Refuse` | Reject the drag |
| `MUIV_DragQuery_Ask` | Ask user (rarely used) |

### Handling the Drop

Implement `MUIM_DragDrop` to process the actual drop:

```c
ULONG DragDrop(struct IClass *cl, Object *obj, struct MUIP_DragDrop *msg)
{
    /* msg->obj is the source, obj is the destination */
    /* Perform the drop operation */
    return DoSuperMethodA(cl, obj, msg);
}
```

## Settings Persistence

MUI provides a mechanism to save and restore the state of widgets using `Dataspace` objects.

### Saving Settings

```c
APTR dataspace;

/* Create a dataspace to hold settings */
dataspace = MUI_NewObject(MUIC_Dataspace, TAG_DONE);

/* Ask each object to export its settings */
DoMethod(window, MUIM_Export, dataspace);

/* Save the dataspace to disk */
/* (Implementation depends on your storage format) */
```

### Loading Settings

```c
/* Load dataspace from disk, then: */
DoMethod(window, MUIM_Import, dataspace);

/* Update the UI */
MUI_DisposeObject(dataspace);
```

Many built-in MUI classes support `MUIM_Export` and `MUIM_Import` automatically. Custom classes need to implement these methods if they want to participate.

## Subtasks and Background Processing

For long-running operations, perform work in a separate task and update the UI periodically. The `Subtask.c` example demonstrates this with a fractal renderer.

### SubTask Structure

```c
struct SubTask
{
    struct Task    *st_Task;    /* Sub task pointer */
    struct MsgPort *st_Port;    /* Allocated by sub task */
    struct MsgPort *st_Reply;   /* Allocated by main task */
    APTR            st_Data;    /* Initial data */
    struct SubTaskMsg st_Message;
};

struct SubTaskMsg
{
    struct Message stm_Message;
    WORD           stm_Command;
    APTR           stm_Parameter;
    LONG           stm_Result;
};
```

### Communication Protocol

```c
#define STC_STARTUP  -2
#define STC_SHUTDOWN -1
#define STC_START     0
#define STC_STOP      1

LONG SendSubTaskMsg(struct SubTask *st, WORD command, APTR params)
{
    st->st_Message.stm_Message.mn_ReplyPort = st->st_Reply;
    st->st_Message.stm_Message.mn_Length    = sizeof(struct SubTaskMsg);
    st->st_Message.stm_Command              = command;
    st->st_Message.stm_Parameter            = params;
    st->st_Message.stm_Result               = 0;

    PutMsg(command == STC_STARTUP
               ? &((struct Process *)st->st_Task)->pr_MsgPort
               : st->st_Port,
           (struct Message *)&st->st_Message);

    WaitPort(st->st_Reply);
    GetMsg(st->st_Reply);

    return st->st_Message.stm_Result;
}
```

### Spawning a Subtask

```c
struct SubTask *SpawnSubTask(char *name, VOID (*func)(VOID), APTR data)
{
    struct SubTask *st;

    if (st = AllocVec(sizeof(struct SubTask), MEMF_PUBLIC | MEMF_CLEAR))
    {
        if (st->st_Reply = CreateMsgPort())
        {
            st->st_Data = data;

            if (st->st_Task = CreateNewProcTags(
                    NP_Entry, func,
                    NP_Name, name,
                    NP_Priority, 0,
                    TAG_DONE))
            {
                /* Send startup message with SubTask pointer */
                SendSubTaskMsg(st, STC_STARTUP, st);
                return st;
            }
        }
    }
    /* cleanup on error */
    return NULL;
}
```

### Updating the UI from the Subtask

The subtask should not directly call MUI methods. Instead, it signals the main task, which then updates the UI:

```c
/* In subtask: calculate a line, then signal main task */
Signal(mainTask, SIGF_SINGLE);

/* In main task input loop or notification handler: */
/* Check for update flag and redraw affected area */
```

Alternatively, use `MUIM_Application_PushMethod` to safely queue a method call from another task:

```c
/* Thread-safe: push a method onto the application's queue */
DoMethod(app, MUIM_Application_PushMethod, obj, 2, MUIM_Redraw, MADF_DRAWOBJECT);
```

## BOOPSI Gadget Integration

MUI can host native BOOPSI gadgets through the `Boopsi` class:

```c
Child, BoopsiObject,
    MUIA_Boopsi_ClassID, "gadgetclass",
    MUIA_Boopsi_MinWidth, 100,
    MUIA_Boopsi_MinHeight, 20,
    MUIA_Boopsi_Gadget, myGadget,
    TAG_DONE,
```

This is useful when you have existing BOOPSI gadgets that you want to embed in a MUI layout.

## Complex UI State Management

When multiple widgets depend on the same state, use a Dataspace or a central model object with notifications:

```c
/* Central model object (can be a simple Notify subclass) */
APTR model = MUI_NewObject(MUIC_Notify,
    MUIA_UserData, initialValue,
    TAG_DONE);

/* Widget A reflects model state */
DoMethod(model, MUIM_Notify, MUIA_UserData, MUIV_EveryTime,
    widgetA, 3, MUIM_Set, MUIA_Numeric_Value, MUIV_TriggerValue);

/* Widget B also reflects model state */
DoMethod(model, MUIM_Notify, MUIA_UserData, MUIV_EveryTime,
    widgetB, 3, MUIM_Set, MUIA_Numeric_Value, MUIV_TriggerValue);

/* Changing the model updates both widgets */
set(model, MUIA_UserData, newValue);
```

## Notification Chains for Wizard UIs

For multi-step UIs, chain notifications to show/hide pages:

```c
/* Show page 2 when Next is pressed */
DoMethod(nextButton, MUIM_Notify, MUIA_Pressed, FALSE,
    page1, 3, MUIM_Set, MUIA_ShowMe, FALSE);

DoMethod(nextButton, MUIM_Notify, MUIA_Pressed, FALSE,
    page2, 3, MUIM_Set, MUIA_ShowMe, TRUE);

/* Show page 1 when Back is pressed */
DoMethod(backButton, MUIM_Notify, MUIA_Pressed, FALSE,
    page2, 3, MUIM_Set, MUIA_ShowMe, FALSE);

DoMethod(backButton, MUIM_Notify, MUIA_Pressed, FALSE,
    page1, 3, MUIM_Set, MUIA_ShowMe, TRUE);
```

## Using MUI_MakeObject

For simple widgets that don't need attributes at creation time, `MUI_MakeObject` provides a compact syntax:

```c
/* Cycle gadget */
APTR cycle = MUI_MakeObject(MUIO_Cycle, NULL, choices);

/* Radio buttons */
APTR radio = MUI_MakeObject(MUIO_Radio, NULL, options);

/* Horizontal bar */
APTR hbar = MUI_MakeObject(MUIO_HBar, 4);

/* Vertical bar */
APTR vbar = MUI_MakeObject(MUIO_VBar, 4);

/* Menu strip from NewMenu */
APTR strip = MUI_MakeObject(MUIO_MenustripNM, newMenu, 0);
```

This reduces verbosity for simple cases.

---

Previous: [Events and Notifications](10-events-and-notifications.md)
Next: [Reference Snippets](12-reference-snippets.md)
