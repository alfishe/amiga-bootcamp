[← Home](../README.md) · [Intuition](README.md)

# Requesters — EasyRequest, AutoRequest, ASL File Requester

## Overview

Requesters are modal dialog boxes. Intuition provides `EasyRequest` for simple dialogs; `asl.library` provides file/font/screen-mode requesters.

---

## EasyRequest (OS 2.0+)

```c
struct EasyStruct es = {
    sizeof(struct EasyStruct),
    0,
    "Warning",                    /* title */
    "Delete file '%s'?",          /* body (printf format) */
    "Yes|No|Cancel"               /* button labels (| separated) */
};

LONG result = EasyRequest(win, &es, NULL, filename);
/* Returns: 1=Yes, 0=Cancel, 2=No (rightmost non-zero, leftmost=0) */
/* For Yes|No: 1=Yes, 0=No */
```

---

## ASL File Requester

```c
struct Library *AslBase = OpenLibrary("asl.library", 39);
struct FileRequester *fr = AllocAslRequestTags(ASL_FileRequest,
    ASLFR_TitleText,    "Open File",
    ASLFR_InitialDrawer, "SYS:",
    ASLFR_InitialPattern, "#?.txt",
    ASLFR_DoPatterns,   TRUE,
    TAG_DONE);

if (AslRequest(fr, NULL)) {
    Printf("Selected: %s%s\n", fr->fr_Drawer, fr->fr_File);
}
FreeAslRequest(fr);
CloseLibrary(AslBase);
```

---

## ASL Font Requester

```c
struct FontRequester *fo = AllocAslRequestTags(ASL_FontRequest,
    ASLFO_TitleText,    "Select Font",
    ASLFO_InitialName,  "topaz.font",
    ASLFO_InitialSize,  8,
    ASLFO_DoStyle,      TRUE,
    TAG_DONE);

if (AslRequest(fo, NULL)) {
    Printf("Font: %s %ld\n", fo->fo_Attr.ta_Name, fo->fo_Attr.ta_YSize);
}
FreeAslRequest(fo);
```

---

## References

- NDK39: `intuition/intuition.h`, `libraries/asl.h`
- ADCD 2.1: `EasyRequest`, `AslRequest`
