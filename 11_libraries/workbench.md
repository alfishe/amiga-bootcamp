[← Home](../README.md) · [Libraries](README.md)

# workbench.library — Workbench Integration

## Overview

`workbench.library` provides APIs for interacting with the Workbench desktop: AppWindows, AppIcons, AppMenuItems, and startup message handling.

---

## WBStartup Message

When launched from Workbench, a program receives a `WBStartup` message instead of CLI arguments:

```c
struct WBStartup {
    struct Message sm_Message;
    struct MsgPort *sm_Process;   /* process that sent us */
    BPTR   sm_Segment;            /* our loaded segment */
    LONG   sm_NumArgs;            /* number of arguments */
    char  *sm_ToolWindow;         /* tool window spec */
    struct WBArg *sm_ArgList;     /* argument array */
};

struct WBArg {
    BPTR   wa_Lock;    /* directory lock */
    BYTE  *wa_Name;    /* filename */
};
```

### Handling WBStartup

```c
struct WBStartup *wbmsg = NULL;
if (!argc) {  /* launched from Workbench */
    WaitPort(&((struct Process *)FindTask(NULL))->pr_MsgPort);
    wbmsg = (struct WBStartup *)GetMsg(
        &((struct Process *)FindTask(NULL))->pr_MsgPort);
    /* Process wbmsg->sm_ArgList for file arguments */
}
/* ... do work ... */
if (wbmsg) {
    Forbid();
    ReplyMsg((struct Message *)wbmsg);
}
```

---

## AppWindow / AppIcon / AppMenuItem

```c
/* Register a window to receive file drops: */
struct AppWindow *appwin = AddAppWindow(1, 0, win, port, NULL);
/* When user drags files to the window, receive AppMessage on port */

struct AppMessage {
    struct Message am_Message;
    UWORD  am_Type;        /* AMTYPE_APPWINDOW, etc. */
    ULONG  am_UserData;
    ULONG  am_ID;
    LONG   am_NumArgs;     /* number of files dropped */
    struct WBArg *am_ArgList; /* array of file references */
    /* ... */
};

RemoveAppWindow(appwin);
```

---

## References

- NDK39: `workbench/workbench.h`, `workbench/startup.h`
