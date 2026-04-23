[← Home](../README.md) · [Intuition](README.md)

# Requesters

## What Is a Requester?

A requester is a **modal dialog** — a focused interaction that temporarily blocks user access to its parent window until the user responds. Amiga requesters come in several flavors:

| Type | API | Use Case |
|---|---|---|
| **EasyRequest** | `EasyRequest()` / `EasyRequestArgs()` | Simple message dialogs (alerts, confirmations) |
| **AutoRequest** | `AutoRequest()` | Legacy OS 1.x two-button dialog |
| **ASL File** | `asl.library` — `ASL_FileRequest` | File open/save dialogs |
| **ASL Font** | `asl.library` — `ASL_FontRequest` | Font picker |
| **ASL ScreenMode** | `asl.library` — `ASL_ScreenModeRequest` | Display mode picker |
| **Custom** | `Request()` / BOOPSI | Application-defined forms |

---

## EasyRequest (OS 2.0+)

The standard way to show message dialogs — supports printf-style formatting and arbitrary button layouts:

### Basic Usage

```c
struct EasyStruct es = {
    sizeof(struct EasyStruct),
    0,                               /* Flags (reserved) */
    "Warning",                       /* Window title */
    "Delete file '%s'?\n"
    "This action cannot be undone.",  /* Body text (printf format) */
    "Delete|Cancel"                  /* Button labels (| separated) */
};

LONG result = EasyRequest(win, &es, NULL, filename);
```

### Return Value Logic

The return value mapping is **not intuitive** — it follows a specific pattern:

| Buttons | Click | Return Value |
|---|---|---|
| `"OK"` | OK | `1` |
| `"Yes\|No"` | Yes | `1` |
| `"Yes\|No"` | No | `0` |
| `"Save\|Don't Save\|Cancel"` | Save | `1` |
| `"Save\|Don't Save\|Cancel"` | Don't Save | `2` |
| `"Save\|Don't Save\|Cancel"` | Cancel | `0` |

**Rule**: The **rightmost button always returns 0** (typically "Cancel"). All other buttons return 1, 2, 3... from left to right.

### Printf-Style Formatting

The body text supports `%s`, `%ld`, `%lx`, etc. Additional arguments are passed after the `IDCMP_Ptr` parameter:

```c
struct EasyStruct es = {
    sizeof(struct EasyStruct), 0,
    "Disk Error",
    "Error %ld occurred while\n"
    "reading '%s' from %s:",
    "Retry|Abort"
};

/* Pass format arguments as varargs */
LONG result = EasyRequest(win, &es, NULL,
    errorCode,   /* %ld */
    fileName,    /* %s  */
    deviceName   /* %s  */
);
```

### Non-Blocking Variant

```c
/* For situations where you can't block (e.g., input handler): */
struct Window *reqWin = BuildEasyRequest(win, &es, IDCMP_DISKINSERTED, args);

/* Poll for response (returns -1 while still open): */
LONG response;
while ((response = SysReqHandler(reqWin, NULL, FALSE)) == -1)
{
    /* Do other work or Wait() */
    Wait(1L << reqWin->UserPort->mp_SigBit);
}
FreeSysRequest(reqWin);
```

---

## ASL File Requester

The standard file open/save dialog provided by `asl.library`:

### Opening a File

```c
#include <libraries/asl.h>
#include <proto/asl.h>

struct Library *AslBase = OpenLibrary("asl.library", 39);

struct FileRequester *fr = AllocAslRequestTags(ASL_FileRequest,
    ASLFR_TitleText,      "Open File",
    ASLFR_InitialDrawer,  "SYS:Docs",
    ASLFR_InitialFile,    "",
    ASLFR_InitialPattern, "#?.(txt|doc|guide)",
    ASLFR_DoPatterns,     TRUE,     /* Show pattern gadget */
    ASLFR_DoMultiSelect,  FALSE,    /* Single file selection */
    ASLFR_RejectIcons,    TRUE,     /* Hide .info files */
    TAG_DONE);

if (AslRequest(fr, NULL))
{
    /* User clicked "OK" */
    char fullPath[512];
    strcpy(fullPath, fr->fr_Drawer);
    AddPart(fullPath, fr->fr_File, sizeof(fullPath));
    Printf("Selected: %s\n", fullPath);
}
else
{
    /* User clicked "Cancel" */
}

FreeAslRequest(fr);
CloseLibrary(AslBase);
```

### Save Dialog

```c
struct FileRequester *fr = AllocAslRequestTags(ASL_FileRequest,
    ASLFR_TitleText,     "Save As...",
    ASLFR_InitialDrawer, currentDrawer,
    ASLFR_InitialFile,   currentFile,
    ASLFR_DoSaveMode,    TRUE,      /* "Save" button instead of "Open" */
    ASLFR_DoPatterns,    TRUE,
    TAG_DONE);
```

### Multi-Select

```c
struct FileRequester *fr = AllocAslRequestTags(ASL_FileRequest,
    ASLFR_TitleText,     "Select Files",
    ASLFR_DoMultiSelect, TRUE,
    TAG_DONE);

if (AslRequest(fr, NULL))
{
    if (fr->fr_NumArgs > 0)
    {
        /* Multi-select: iterate the WBArg array */
        for (LONG i = 0; i < fr->fr_NumArgs; i++)
        {
            Printf("File: %s\n", fr->fr_ArgList[i].wa_Name);
        }
    }
    else
    {
        /* Single file selected (even in multi-select mode) */
        Printf("File: %s%s\n", fr->fr_Drawer, fr->fr_File);
    }
}
```

### Common ASL File Tags

| Tag | Type | Description |
|---|---|---|
| `ASLFR_TitleText` | `STRPTR` | Requester window title |
| `ASLFR_InitialDrawer` | `STRPTR` | Starting directory |
| `ASLFR_InitialFile` | `STRPTR` | Pre-selected filename |
| `ASLFR_InitialPattern` | `STRPTR` | AmigaOS pattern filter (e.g., `#?.txt`) |
| `ASLFR_DoPatterns` | `BOOL` | Show pattern matching gadget |
| `ASLFR_DoSaveMode` | `BOOL` | Show "Save" button instead of "Open" |
| `ASLFR_DoMultiSelect` | `BOOL` | Allow multiple file selection |
| `ASLFR_RejectIcons` | `BOOL` | Hide `.info` icon files |
| `ASLFR_DrawersOnly` | `BOOL` | Only show directories (folder picker) |
| `ASLFR_InitialLeftEdge/TopEdge` | `WORD` | Requester position |
| `ASLFR_InitialWidth/Height` | `WORD` | Requester size |
| `ASLFR_Window` | `struct Window *` | Parent window (for positioning) |
| `ASLFR_Screen` | `struct Screen *` | Screen to open on |
| `ASLFR_FilterFunc` | `struct Hook *` | Custom filtering function |

---

## ASL Font Requester

```c
struct FontRequester *fo = AllocAslRequestTags(ASL_FontRequest,
    ASLFO_TitleText,     "Select Font",
    ASLFO_InitialName,   "topaz.font",
    ASLFO_InitialSize,   8,
    ASLFO_DoFrontPen,    TRUE,     /* Show color picker */
    ASLFO_DoStyle,       TRUE,     /* Show Bold/Italic/Underline */
    ASLFO_DoDrawMode,    TRUE,     /* Show JAM1/JAM2 selector */
    ASLFO_MinHeight,     6,        /* Minimum font size */
    ASLFO_MaxHeight,     72,       /* Maximum font size */
    TAG_DONE);

if (AslRequest(fo, NULL))
{
    Printf("Font: %s %ld\n", fo->fo_Attr.ta_Name, fo->fo_Attr.ta_YSize);
    Printf("Style: %ld, FrontPen: %ld\n", fo->fo_Attr.ta_Style, fo->fo_FrontPen);

    /* Open the selected font */
    struct TextFont *font = OpenDiskFont(&fo->fo_Attr);
    if (font)
    {
        SetFont(win->RPort, font);
        /* ... */
        CloseFont(font);
    }
}
FreeAslRequest(fo);
```

---

## ASL ScreenMode Requester

For applications that let users choose their display mode:

```c
struct ScreenModeRequester *smr = AllocAslRequestTags(ASL_ScreenModeRequest,
    ASLSM_TitleText,       "Select Screen Mode",
    ASLSM_InitialDisplayID, HIRES_KEY,
    ASLSM_InitialDisplayDepth, 4,
    ASLSM_DoWidth,         TRUE,     /* Allow width selection */
    ASLSM_DoHeight,        TRUE,     /* Allow height selection */
    ASLSM_DoDepth,         TRUE,     /* Allow depth selection */
    ASLSM_DoOverscanType,  TRUE,     /* Allow overscan selection */
    ASLSM_MinWidth,        320,
    ASLSM_MinHeight,       200,
    ASLSM_MinDepth,        1,
    ASLSM_MaxDepth,        8,
    TAG_DONE);

if (AslRequest(smr, NULL))
{
    Printf("Mode: 0x%08lx, %ldx%ldx%ld\n",
        smr->sm_DisplayID,
        smr->sm_DisplayWidth,
        smr->sm_DisplayHeight,
        smr->sm_DisplayDepth);

    /* Open screen with selected mode */
    struct Screen *scr = OpenScreenTags(NULL,
        SA_DisplayID, smr->sm_DisplayID,
        SA_Width,     smr->sm_DisplayWidth,
        SA_Height,    smr->sm_DisplayHeight,
        SA_Depth,     smr->sm_DisplayDepth,
        SA_Overscan,  smr->sm_OverscanType,
        SA_AutoScroll, TRUE,
        TAG_DONE);
}
FreeAslRequest(smr);
```

---

## Custom Window Requesters

For application-specific forms, use `Request()` with a custom layout:

```c
/* Create a requester with gadgets */
struct Requester req;
InitRequester(&req);

req.LeftEdge   = 20;
req.TopEdge    = 20;
req.Width      = 300;
req.Height     = 100;
req.ReqGadget  = myGadgetList;    /* Your gadgets */
req.ReqText    = myIntuiText;     /* Labels */
req.BackFill   = 0;               /* Background pen */
req.Flags      = 0;
req.ReqBorder  = myBorder;        /* Border decoration */

/* Activate the requester (blocks the parent window) */
if (Request(&req, win))
{
    /* Requester is active — handle IDCMP_GADGETUP events */
    /* When done: */
    EndRequest(&req, win);
}
```

> Most modern applications use `EasyRequest()` for simple dialogs or build custom windows instead of `Request()`. The `Request()` API is mainly relevant for legacy code.

---

## Remembering Requester State

ASL requesters remember their last position and selections if you reuse the same requester structure:

```c
/* Allocate once at program start */
struct FileRequester *fr = AllocAslRequestTags(ASL_FileRequest,
    ASLFR_TitleText, "Open", TAG_DONE);

/* First use — shows default directory */
AslRequest(fr, NULL);

/* Second use — automatically shows the directory from last use */
AslRequest(fr, NULL);

/* Free at program exit */
FreeAslRequest(fr);
```

You can override this with explicit tags on each call:

```c
AslRequest(fr, (struct TagItem *)(APTR[]){
    { ASLFR_InitialDrawer, (ULONG)"RAM:" },
    { TAG_DONE, 0 }
});
```

---

## Pitfalls

### 1. EasyRequest Return Value Confusion

The rightmost button always returns 0, not the button count. For `"Yes|No"`, "No" returns 0 — which many developers mistake for FALSE when it's actually the "No" response.

### 2. ASL Without a Window Reference

If you don't pass `ASLFR_Window`, the requester opens at a default position, potentially on a different screen or off-screen.

### 3. Not Checking AslRequest Return

`AslRequest()` returns FALSE if the user cancels. Always check — accessing `fr->fr_File` after cancellation returns the previous (stale) selection.

### 4. Forgetting FreeAslRequest

ASL requesters allocate internal memory for file lists and paths. Failing to call `FreeAslRequest()` leaks memory.

### 5. Blocking While Requester Is Open

EasyRequest and AslRequest are **synchronous** — your event loop is stopped while the requester is open. If you need to handle background events, use the non-blocking `BuildEasyRequest()`/`SysReqHandler()` pattern.

---

## Best Practices

1. **Use `EasyRequest()`** for all message dialogs — not `AutoRequest()` (OS 1.x legacy)
2. **Place "Cancel" as the rightmost button** — it always returns 0, matching the Amiga convention
3. **Pass the parent window** to requesters — for proper screen placement and depth arrangement
4. **Reuse ASL requesters** — users expect the dialog to remember their last directory
5. **Use `ASLFR_DoPatterns, TRUE`** — power users rely on pattern matching
6. **Use `ASLFR_RejectIcons, TRUE`** — `.info` files clutter the file list
7. **Use `BuildEasyRequest()`** when you need to handle events during a dialog
8. **Always check return values** — a canceled requester should not proceed with the operation

---

## References

- NDK 3.9: `intuition/intuition.h`, `libraries/asl.h`
- ADCD 2.1: `EasyRequest()`, `AllocAslRequest()`, `AslRequest()`, `FreeAslRequest()`
- AmigaOS Reference Manual (RKRM): Libraries, Chapter 9 — Requesters
- See also: [Windows](windows.md), [Gadgets](gadgets.md), [IDCMP](idcmp.md)
