[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Events and Notifications

## The MUI Event Model

MUI replaces traditional callback registration with a declarative notification system. Instead of writing:

```c
/* Traditional GUI toolkit */
button_set_callback(myButton, on_click, myHandler);
```

You write:

```c
/* MUI */
DoMethod(myButton, MUIM_Notify, MUIA_Pressed, FALSE,
    targetObj, 3, MUIM_CallHook, &myHook, MUIV_TriggerValue);
```

This establishes a relationship: when the source attribute changes to a specific value, invoke a method on the target object.

## MUIM_Notify

The notification method signature:

```c
DoMethod(sourceObj, MUIM_Notify,
    sourceAttribute, triggerValue,
    targetObj, numArgs, targetMethod, ...);
```

| Parameter | Description |
|-----------|-------------|
| `sourceObj` | Object to monitor |
| `sourceAttribute` | Attribute to watch (e.g., `MUIA_Pressed`) |
| `triggerValue` | Value that triggers the notification |
| `targetObj` | Object to invoke the method on |
| `numArgs` | Number of arguments passed to the target method |
| `targetMethod` | Method to invoke (e.g., `MUIM_Application_ReturnID`) |
| `...` | Additional arguments |

### Common Trigger Values

| Value | Meaning |
|-------|---------|
| `MUIV_EveryTime` | Trigger on any change, not just a specific value |
| `TRUE` / `FALSE` | Trigger only when boolean attribute becomes true/false |
| Specific value | Trigger only when attribute equals this exact value |

### Simple Example: Close Window

```c
DoMethod(window, MUIM_Notify, MUIA_Window_CloseRequest, TRUE,
    app, 2, MUIM_Application_ReturnID, MUIV_Application_ReturnID_Quit);
```

When the window's close request flag becomes `TRUE` (user clicks the close gadget), the Application receives a ReturnID of `Quit`.

### Button Press

```c
DoMethod(button, MUIM_Notify, MUIA_Pressed, FALSE,
    app, 2, MUIM_Application_ReturnID, ID_SAVE);
```

`MUIA_Pressed` becomes `FALSE` when the user releases the mouse button over the gadget. This is the standard way to detect button clicks.

### Slider Value Change

```c
DoMethod(slider, MUIM_Notify, MUIA_Numeric_Value, MUIV_EveryTime,
    textObj, 3, MUIM_Set, MUIA_Text_Contents, MUIV_TriggerValue);
```

Every time the slider value changes, update a text object. `MUIV_TriggerValue` passes the new slider value as the argument.

## Input Loops

MUI provides two methods for running the application's main loop.

### Modern Loop: MUIM_Application_NewInput

This is the preferred method. It is faster because it integrates signal waiting.

```c
ULONG sigs = 0;

while (DoMethod(app, MUIM_Application_NewInput, &sigs)
       != MUIV_Application_ReturnID_Quit)
{
    if (sigs)
    {
        sigs = Wait(sigs | SIGBREAKF_CTRL_C);
        if (sigs & SIGBREAKF_CTRL_C)
            break;
    }
}
```

How it works:

1. `DoMethod(app, MUIM_Application_NewInput, &sigs)` processes pending input
2. It returns a ReturnID if one was triggered, or 0
3. It fills `sigs` with the signal mask the application should wait on
4. Your code calls `Wait()` with those signals
5. The loop repeats

This is significantly more efficient than the legacy loop because MUI tells you exactly which signals to wait for.

### Legacy Loop: MUIM_Application_Input

Older examples use this method. It is simpler but less efficient.

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

        case ID_ABOUT:
            /* handle about */
            break;

        case ID_SAVE:
            /* handle save */
            break;
    }

    if (running && signals)
        Wait(signals);
}
```

The difference: `MUIM_Application_Input` handles waiting internally but returns a generic signal mask. `MUIM_Application_NewInput` gives you finer control.

## Return IDs

Return IDs are how notifications communicate with the input loop. MUI defines a standard quit ID:

| Constant | Value | Meaning |
|----------|-------|---------|
| `MUIV_Application_ReturnID_Quit` | -1 | Application should terminate |

You can define your own IDs:

```c
#define ID_ABOUT  1
#define ID_SAVE   2
#define ID_OPEN   3
```

Return IDs are triggered by notifications:

```c
DoMethod(button, MUIM_Notify, MUIA_Pressed, FALSE,
    app, 2, MUIM_Application_ReturnID, ID_SAVE);
```

## Hooks

For complex actions that cannot be expressed as a simple method call, use hooks. A hook is a standard AmigaOS callback structure.

### Hook Structure

```c
struct Hook
{
    struct MinNode h_MinNode;
    ULONG          (*h_Entry)();  /* function pointer */
    ULONG          (*h_SubEntry)();
    APTR           h_Data;        /* user data */
};
```

### Defining a Hook

```c
SAVEDS ASM LONG MyHookFunc(REG(a2) APTR obj, REG(a1) APTR param)
{
    /* obj is the object that triggered the hook */
    /* param is the argument passed from the notification */
    return 0;
}

static struct Hook MyHook = {
    { NULL, NULL }, (VOID *)MyHookFunc, NULL, NULL
};
```

### Invoking a Hook via Notification

```c
DoMethod(button, MUIM_Notify, MUIA_Pressed, FALSE,
    app, 3, MUIM_CallHook, &MyHook, MUIV_TriggerValue);
```

### Hook Register Conventions

The MUI examples use register arguments for hook functions:

| Register | Parameter |
|----------|-----------|
| `a0` | struct Hook * |
| `a2` | Object * (source object) |
| `a1` | Msg / parameter |

Different compilers handle register keywords differently, so the examples use conditional macros:

```c
#ifdef _DCC
#define REG(x) __ ## x
#define ASM
#define SAVEDS __geta4
#else
#define REG(x) register __ ## x
#if defined __MAXON__ || defined __GNUC__
#define ASM
#define SAVEDS
#else
#define ASM    __asm
#define SAVEDS __saveds
#endif
#endif
```

## Notification Chains

Notifications can be chained. One notification can trigger an attribute change that causes another notification:

```c
/* When checkbox is checked, enable the button */
DoMethod(checkbox, MUIM_Notify, MUIA_Selected, TRUE,
    button, 3, MUIM_Set, MUIA_Disabled, FALSE);

/* When checkbox is unchecked, disable the button */
DoMethod(checkbox, MUIM_Notify, MUIA_Selected, FALSE,
    button, 3, MUIM_Set, MUIA_Disabled, TRUE);
```

## Common Notification Patterns

### Synchronize Two Widgets

```c
/* Slider and numeric button show the same value */
DoMethod(slider, MUIM_Notify, MUIA_Numeric_Value, MUIV_EveryTime,
    numButton, 3, MUIM_Set, MUIA_Numeric_Value, MUIV_TriggerValue);

DoMethod(numButton, MUIM_Notify, MUIA_Numeric_Value, MUIV_EveryTime,
    slider, 3, MUIM_Set, MUIA_Numeric_Value, MUIV_TriggerValue);
```

### Update Window Title

```c
DoMethod(string, MUIM_Notify, MUIA_String_Contents, MUIV_EveryTime,
    window, 3, MUIM_Set, MUIA_Window_Title, MUIV_TriggerValue);
```

### Enable Widget Based on Selection

```c
DoMethod(listview, MUIM_Notify, MUIA_List_Active, MUIV_EveryTime,
    app, 2, MUIM_CallHook, &UpdateButtonHook);
```

---

Previous: [Custom Classes](09-custom-classes.md)
Next: [Advanced Patterns](11-advanced-patterns.md)
