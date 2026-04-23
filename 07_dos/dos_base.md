[← Home](../README.md) · [AmigaDOS](README.md)

# DosLibrary — Structure and Global State

## Overview

`dos.library` is opened by nearly every Amiga program. The library base `DOSBase` is a `struct DosLibrary` that extends `struct Library` with process-level state, the root node, and handler management.

---

## struct DosLibrary

```c
/* dos/dosextens.h — NDK39 */
struct DosLibrary {
    struct Library  dl_lib;           /* standard Library header */
    struct RootNode *dl_Root;         /* pointer to the system root node */
    APTR            dl_GV;            /* BCPL global vector */
    LONG            dl_A2;            /* BCPL scratch */
    LONG            dl_A5;            /* BCPL scratch */
    LONG            dl_A6;            /* BCPL scratch */
    struct ErrorString *dl_Errors;    /* error string table */
    struct timerequest *dl_TimeReq;   /* timer.device request */
    struct Library  *dl_UtilityBase;  /* cached UtilityBase */
    struct Library  *dl_IntuitionBase;/* cached IntuitionBase */
};
```

---

## struct RootNode

```c
struct RootNode {
    BPTR   rn_TaskArray;   /* BPTR to CLI task array */
    BPTR   rn_ConsoleSegment; /* console handler segment */
    struct DateStamp rn_Time; /* current system time */
    LONG   rn_RestartSeg;  /* restart segment */
    BPTR   rn_Info;        /* BPTR to DosInfo */
    BPTR   rn_FileHandlerSegment;
    struct MinList rn_CliList; /* list of CLI processes */
    /* ... OS 3.x additions ... */
    ULONG  rn_BootFlags;
    APTR   rn_BootProc;
};
```

---

## Opening dos.library

```c
struct DosLibrary *DOSBase;
DOSBase = (struct DosLibrary *)OpenLibrary("dos.library", 40);
if (!DOSBase) { /* OS 3.1 or later required */ }
```

---

## BCPL Heritage

AmigaDOS was originally written in BCPL. Artifacts remain:
- **BPTR** — pointers right-shifted by 2 (`real = bptr << 2`)
- `dl_GV` — BCPL global vector (used internally by filesystem handlers)
- File handles and locks are BPTRs, not real pointers

```c
/* Convert BPTR to C pointer: */
#define BADDR(bptr) ((APTR)((ULONG)(bptr) << 2))
```

---

## References

- NDK39: `dos/dosextens.h`, `dos/dos.h`
- ADCD 2.1: dos.library autodocs
