[← Home](../README.md) · [Libraries](README.md)

# icon.library — Workbench Icons (.info Files)

## Overview

Every Workbench-visible file has a companion `.info` file containing its icon imagery, tooltypes, and default tool. `icon.library` provides reading/writing these structures.

---

## struct DiskObject

```c
/* workbench/workbench.h — NDK39 */
struct DiskObject {
    UWORD           do_Magic;      /* $E310 = WB_DISKMAGIC */
    UWORD           do_Version;    /* WB_DISKVERSION */
    struct Gadget   do_Gadget;     /* the icon gadget */
    UBYTE           do_Type;       /* WBDISK, WBTOOL, WBPROJECT, etc. */
    char           *do_DefaultTool; /* default tool path */
    char          **do_ToolTypes;   /* NULL-terminated string array */
    LONG            do_CurrentX;   /* icon X position */
    LONG            do_CurrentY;   /* icon Y position */
    BPTR            do_DrawerData;  /* drawer window position (BPTR) */
    char           *do_ToolWindow;  /* tool window spec */
    LONG            do_StackSize;   /* stack size for tool */
};
```

---

## Icon Types

| Constant | Value | Description |
|---|---|---|
| `WBDISK` | 1 | Disk/volume icon |
| `WBDRAWER` | 2 | Drawer (directory) |
| `WBTOOL` | 3 | Executable tool |
| `WBPROJECT` | 4 | Project (document) |
| `WBGARBAGE` | 5 | Trashcan |
| `WBDEVICE` | 6 | Device |
| `WBKICK` | 7 | Kickstart disk |
| `WBAPPICON` | 8 | AppIcon (OS 2.0+) |

---

## ToolTypes

ToolTypes are key=value strings stored in `do_ToolTypes`:

```c
struct DiskObject *dobj = GetDiskObject("myapp");
if (dobj) {
    char *val = FindToolType(dobj->do_ToolTypes, "PUBSCREEN");
    if (val) Printf("Screen: %s\n", val);
    if (MatchToolValue(FindToolType(dobj->do_ToolTypes, "FLAGS"), "DEBUG"))
        Printf("Debug mode\n");
    FreeDiskObject(dobj);
}
```

---

## References

- NDK39: `workbench/workbench.h`, `workbench/icon.h`
