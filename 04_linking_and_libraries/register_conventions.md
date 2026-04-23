[← Home](../README.md) · [Linking & Libraries](README.md)

# M68k Register Calling Conventions on Amiga

## Overview

AmigaOS uses a **pure register-based calling convention** for all OS API calls. There is no stack-based C ABI for library functions. Every argument is passed in a specific CPU register defined by the `.fd` file for that library. This document covers the complete convention including integer, FPU, varargs, tag-based calls, small-data model, and inter-library patterns.

---

## The AmigaOS Register Convention

### Integer Registers

| Register | Role | Preserved? |
|---|---|---|
| **A6** | Library base pointer (always) | **No** — overwritten with target lib |
| **D0** | Return value (32-bit) | **No** — scratch |
| **D1** | 2nd return (64-bit pair) or argument | **No** — scratch |
| **A0** | Argument or scratch | **No** — scratch |
| **A1** | Argument or scratch | **No** — scratch |
| D2–D7 | Arguments (per .fd) | **Yes** — callee-preserved |
| A2–A3 | Arguments (per .fd) | **Yes** — callee-preserved |
| A4 | Small-data base pointer (VBCC/GCC) | **Yes** — callee-preserved |
| A5 | Frame pointer (SAS/C) or scratch | **Yes** — callee-preserved |
| A7 (SP) | Stack pointer | Maintained by convention |

### Key Rules

1. **A6 is always destroyed** — it holds the target library base before and after every OS call
2. **D0, D1, A0, A1** are volatile — the OS may destroy them in any library call
3. Callee-preserved means the OS function saves and restores these registers internally
4. Arguments go in the registers specified by the `.fd` file — never on the stack

### FPU Registers (68881/68882/68040/68060)

| Register | Role | Preserved? |
|---|---|---|
| **FP0** | Return value (floating-point) | **No** — scratch |
| **FP1** | Scratch | **No** — scratch |
| FP2–FP7 | Available for arguments | **Yes** — callee-preserved |

> **Note**: Very few AmigaOS functions use FPU registers. `mathieeedoubtrans.library` and `mathtrans.library` pass arguments via D0/D1 (as 32-bit or 64-bit integer representations of IEEE floats), not in FP registers. Only custom libraries designed for FPU-equipped systems use FP0–FP7 for parameter passing.

---

## Example: dos.library Write()

From `fd/dos_lib.fd`:
```
Write(file,buffer,length)(d1,d2,d3)
```

```asm
; Assembly — calling Write(fh, buf, 512):
    MOVEA.L  _DOSBase, A6       ; Library base → A6
    MOVE.L   fh,    D1          ; BPTR filehandle → D1
    MOVE.L   buf,   D2          ; Buffer address → D2
    MOVE.L   #512,  D3          ; Byte count → D3
    JSR      -48(A6)            ; Write() LVO = -48
    ; D0 = bytes written (-1 = error)
    ; D1, A0, A1, A6 are now UNDEFINED
    ; D2, D3 still hold their values (callee-preserved)
```

```c
/* C — compiler generates the above automatically */
LONG n = Write(fh, buf, 512);
```

---

## Register Preservation Map

```
After ANY OS library call:

  ┌─────────────────────────────┐
  │ DESTROYED (don't rely on):  │
  │   D0  D1  A0  A1  A6       │
  │   FP0  FP1                  │
  │   CCR (condition codes)     │
  └─────────────────────────────┘

  ┌─────────────────────────────┐
  │ PRESERVED (guaranteed):     │
  │   D2  D3  D4  D5  D6  D7   │
  │   A2  A3  A4  A5           │
  │   FP2  FP3  FP4  FP5       │
  │   FP6  FP7                 │
  │   SP (A7)                  │
  └─────────────────────────────┘
```

This matches the Motorola 68000 family software convention. AmigaOS does **not** follow the System V m68k ABI (which uses stack-based parameter passing).

---

## Inter-Library Calls

When one library function calls another library internally, it must save/restore A6:

```asm
; Inside dos.library, calling exec.library AllocMem:
    MOVEM.L  A6, -(SP)          ; Save current A6 (dos.library base)
    MOVEA.L  _SysBase, A6       ; Load exec.library base
    MOVE.L   #1024, D0          ; byteSize
    MOVE.L   #$10001, D1        ; MEMF_PUBLIC|MEMF_CLEAR
    JSR      -198(A6)           ; AllocMem()
    MOVEA.L  (SP)+, A6          ; Restore dos.library base
    ; D0 = allocated memory or NULL
```

> **Common bug**: Forgetting to save/restore A6 in hand-written assembly library code. The caller expects A6 to point to the library it called, but internally the library swapped A6 to call another library.

---

## Small Data Model (A4-Relative)

C compilers can use A4 as a **base register** for accessing global/static data, reducing code size:

### SAS/C Small Data

```c
/* SAS/C: compile with -b0 (small data model) */
/* Generates A4-relative addressing for globals */
```

```asm
; Without small data:
    MOVE.L  _myGlobal, D0       ; 6 bytes: absolute addressing

; With small data (A4-relative):
    MOVE.L  -$1234(A4), D0     ; 4 bytes: A4-relative displacement
```

### __saveds Keyword

The `__saveds` keyword tells the compiler to reload A4 on function entry — essential for library functions and interrupt handlers that may be called from any context:

```c
/* Library function: */
LONG __saveds MyFunc(LONG arg __asm("d0"))
{
    /* __saveds generates: */
    /* LEA  __LinkerDB, A4  ; reload small-data base */
    /* ...function code... */
    return arg * 2;
}
```

```asm
; What __saveds generates:
_MyFunc:
    LEA     __LinkerDB, A4      ; Restore small-data base register
    ; Now A4-relative data access works
    MOVE.L  D0, D1
    ADD.L   D1, D0
    RTS
```

**When you need `__saveds`:**
- Library functions (called via JMP table from any task)
- Interrupt handlers (`AddIntServer` callbacks)
- Hook functions (Intuition/BOOPSI hooks)
- Callback functions passed to other libraries

**When you DON'T need `__saveds`:**
- Regular functions called within the same program (A4 already set)
- Programs compiled with the large data model (absolute addressing)

### GCC Equivalent

```c
/* GCC: -msmall-code -mbaserel flags */
/* Uses A4 as the small-data base pointer */
/* __saveds equivalent: __attribute__((saveds)) */

LONG __attribute__((saveds)) MyFunc(LONG arg __asm("d0"))
{
    return arg * 2;
}
```

---

## Varargs and Tag-Based Calls

### The Problem

The register convention breaks down for variable-argument functions. You can't pass an unknown number of arguments in registers. AmigaOS solves this with **TagItem arrays**:

```c
/* Fixed-register call (standard): */
struct Window *OpenWindow(struct NewWindow *nw __asm("a0"));
/* → A0 = pointer to struct, A6 = IntuitionBase */

/* Tag-based call (varargs): */
struct Window *OpenWindowTagList(
    struct NewWindow *nw,      /* A0 */
    struct TagItem *tagList    /* A1 — pointer to tag array */
);
```

### TagItem Structure

```c
struct TagItem {
    ULONG ti_Tag;     /* tag identifier */
    ULONG ti_Data;    /* tag value */
};

/* Example tag list: */
struct TagItem tags[] = {
    { WA_Left,    100 },
    { WA_Top,     50  },
    { WA_Width,   640 },
    { WA_Height,  480 },
    { WA_Title,   (ULONG)"My Window" },
    { TAG_DONE,   0   }
};

struct Window *win = OpenWindowTagList(NULL, tags);
```

### Stack-Based Varargs Wrappers

For convenience, AmigaOS provides `...Tags()` wrappers that build the tag array on the stack:

```c
/* This is a MACRO or inline function, NOT an OS call: */
struct Window *OpenWindowTags(struct NewWindow *nw, ULONG tag1, ...)
{
    /* Tags are pushed onto the stack by the caller */
    /* The wrapper takes the address of tag1 and passes it as a TagItem* */
    return OpenWindowTagList(nw, (struct TagItem *)&tag1);
}

/* Usage: */
struct Window *win = OpenWindowTags(NULL,
    WA_Left, 100,
    WA_Top, 50,
    WA_Width, 640,
    WA_Height, 480,
    WA_Title, "My Window",
    TAG_DONE);
```

> **Important**: The `...Tags()` functions are **not** OS calls — they are C macros or inline stubs that build a tag array on the caller's stack and pass it to the real `...TagList()` function. They do NOT use the stack for parameter passing to the OS.

### Common Tag Patterns

| Real function (register) | Convenience wrapper (stack) |
|---|---|
| `OpenWindowTagList(nw, tags)` | `OpenWindowTags(nw, ...)` |
| `CreateNewProcTags(tags)` | Doesn't exist — use TagList directly |
| `AllocDosObjectTagList(type, tags)` | `AllocDosObject(type, ...)` |
| `SetAttrsA(obj, tags)` | `SetAttrs(obj, ...)` |

---

## C Compiler Differences

### SAS/C 6.x
- Uses A5 as frame pointer (`LINK A5; UNLK A5`)
- Uses A4 for small data model (opt-in with `-b0`)
- `#pragma amicall` for register specification
- `__saveds` for A4 reload in library/callback functions

### GCC (bebbo m68k-amigaos)
- No frame pointer by default (`-fomit-frame-pointer`)
- Uses A4 for small data (`-mbaserel`, `-msmall-code`)
- Inline assembly with `__asm("register")` constraints
- `__attribute__((saveds))` for A4 reload

### VBCC
- `__reg("d0")` storage class for explicit register placement
- No frame pointer — generates very compact code
- Uses A4 for small data model by default
- `__saveds` supported

---

## Detecting the Convention in Disassembly

### Identifying an OS API Call

```asm
; Pattern 1 — Standard library call:
    MOVEA.L  (_DOSBase).L, A6     ; Load library base
    [move args to registers]       ; Per .fd specification
    JSR      (-138,A6)            ; Call at LVO -138

; Pattern 2 — PC-relative base load (GCC):
    LEA      _DOSBase(PC), A0    ; PC-relative load of base address
    MOVEA.L  (A0), A6            ; Dereference
    JSR      (-30,A6)            ; Open()

; Pattern 3 — Small-data base load (SAS/C):
    MOVEA.L  -$42(A4), A6        ; Load base from A4-relative storage
    JSR      (-48,A6)            ; Write()
```

Cross-reference the LVO against the `.fd` file to identify the function. IDA's Amiga loader applies LVO names automatically when library definitions are present.

---

## References

- NDK39: `fd/*.fd` — register assignments per function
- NDK39: `utility/tagitem.h` — TagItem structure
- *Amiga ROM Kernel Reference Manual: Libraries* — register conventions appendix
- SAS/C 6.x Programmer's Guide — calling convention, small data, __saveds
- GCC m68k-amigaos (bebbo) — `libnix` inline headers
- VBCC documentation — register specification chapter
