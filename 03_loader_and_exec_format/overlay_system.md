[← Home](../README.md) · [Loader & HUNK Format](README.md)

# HUNK_OVERLAY — Overlay System

## Overview

The **overlay system** allows programs larger than available RAM to run by dividing code into **segments loaded on demand**. Only one overlay section is present in memory at any time; others are swapped in from disk when needed.

This predates virtual memory and was commonly used in A500-era applications with limited Fast RAM.

---

## When Overlays Are Used

- Application code exceeds available RAM
- Rarely-used code paths (setup, error handling) should not occupy memory permanently
- The game/app has a fixed resident core and multiple interchangeable level/module overlays

---

## HUNK_OVERLAY Structure

```
HUNK_HEADER
  (normal header for resident hunks)

[Normal hunks: code, data, BSS]

HUNK_OVERLAY ($000003F5)
  <size_in_longs>         total size of overlay table data
  <overlay_tree...>       tree of overlay nodes

HUNK_BREAK ($000003F6)    marks end of overlay tree
```

### Overlay Tree Format

The overlay tree describes groups of overlays and their dependencies:

```
<num_overlay_nodes>
For each node:
  <num_hunks>             number of hunks in this overlay
  <hunk_sizes...>         size of each hunk in longwords
  <hunk_memory_types...>  memory requirements
```

The resident (non-overlay) hunks are hunk 0 through N. The overlay hunks are numbered starting at N+1.

---

## Runtime Overlay Support — overlaylibrary

AmigaOS provides `dos.library` support for overlays via `InternalLoadSeg` with an overlay table. The application calls `ObtainSemaphore()` + `OverlayLoad()` to swap overlays.

In practice, the overlay system is complex and rarely documented precisely. Most real Amiga applications avoid overlays in favour of:
- Dynamic library loading (`OpenLibrary`)
- Splitting functionality into separate executables run via `Execute`
- AmigaOS shared library mechanism

---

## Practical Alternative: Dynamic Linking

Modern Amiga development (and OS 3.1+ best practices) uses `OpenLibrary()` instead of overlays:

```c
struct MyLib *MyBase = (struct MyLib *)OpenLibrary("mycode.library", 0);
if (MyBase) {
    MyBase->myFunction(arg1, arg2);
    CloseLibrary((struct Library *)MyBase);
}
```

This is functionally equivalent to overlay loading but uses the OS resource tracking system and allows multiple users.

---

## References

- *Amiga ROM Kernel Reference Manual: Libraries* — AmigaDOS overlay section
- NDK39: `dos/doshunks.h` — HUNK_OVERLAY, HUNK_BREAK
- Paul Tuma's Amiga HUNK format notes (community)
