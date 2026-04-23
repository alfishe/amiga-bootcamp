[← Home](../README.md) · [Exec Kernel](README.md)

# Library System — OpenLibrary Lifecycle

## Overview

The AmigaOS library system provides **versioned, shared code** via a standardised interface. Libraries are identified by name, opened with a version check, and reference-counted for safe unloading.

---

## Library Node

Every library is an `NT_LIBRARY` node on `SysBase->LibList`:

```c
struct Library {
    struct Node  lib_Node;       /* ln_Name = "dos.library" */
    UBYTE        lib_Flags;      /* LIBF_SUMUSED | LIBF_DELEXP */
    UBYTE        lib_Pad;
    UWORD        lib_NegSize;    /* size of JMP table in bytes */
    UWORD        lib_PosSize;    /* size of library base struct */
    UWORD        lib_Version;    /* major version */
    UWORD        lib_Revision;   /* minor revision */
    APTR         lib_IdString;   /* "dos.library 40.1 (16.7.93)" */
    ULONG        lib_Sum;        /* JMP table checksum */
    UWORD        lib_OpenCnt;    /* reference count */
};
```

---

## OpenLibrary / CloseLibrary

```c
/* Open — get a reference: */
struct DosLibrary *DOSBase =
    (struct DosLibrary *)OpenLibrary("dos.library", 40);

/* Use the library ... */

/* Close — release reference: */
CloseLibrary((struct Library *)DOSBase);
```

Internally:
1. `exec` scans `LibList` for `ln_Name == "dos.library"`
2. If not found, searches resident list and `LIBS:` path
3. If found on disk: `LoadSeg` + call `InitLib`
4. Check `lib_Version >= requested_version`
5. Call library's `Open()` vector → `lib_OpenCnt++`
6. Return library base

---

## Library Flags

| Flag | Value | Meaning |
|---|---|---|
| `LIBF_SUMUSED` | 0x01 | Checksum is maintained |
| `LIBF_CHANGED` | 0x02 | Checksum needs recalculation |
| `LIBF_DELEXP` | 0x04 | Expunge deferred (opened while expunge pending) |

---

## Version Numbering Convention

`lib_Version.lib_Revision`:
- `40.1` = OS 3.1 release
- `40.x` = OS 3.1 (various revisions)
- `44.x` = OS 3.2

Increment rules:
- `lib_Revision` — minor bugfix, compatible
- `lib_Version` — API change or major update (requestors check this)

---

## Finding a Library Without Opening

```c
/* Read-only peek — no open count increment */
Forbid();
struct Library *lib = FindName(&SysBase->LibList, "graphics.library");
Permit();
if (lib) printf("Found v%d\n", lib->lib_Version);
```

> [!CAUTION]
> Using `FindName` without `Forbid()` is a race condition — the library could be expunged between finding it and using it.

---

## References

- NDK39: `exec/libraries.h`
- ADCD 2.1: `OpenLibrary`, `CloseLibrary`, `FindName`
- `04_linking_and_libraries/shared_libraries_runtime.md` — expunge lifecycle
