[← Home](../README.md) · [Linking & Libraries](README.md)

# M68k Register Calling Conventions on Amiga

## Overview

AmigaOS uses a **pure register-based calling convention** for all OS API calls. There is no stack-based C ABI for library functions. Every argument is passed in a specific CPU register defined by the `.fd` file for that library.

---

## The AmigaOS Register Convention

All OS library calls follow this scheme:

| Register | Role |
|---|---|
| **A6** | Library base pointer (always) |
| **D0** | Return value (32-bit integer or BOOL) |
| **D0+D1** | 64-bit return (rare; e.g., `DivideU`) |
| D1–D7, A0–A3 | Arguments — exact registers per `.fd` |
| D2–D7, A2–A3 | **Callee-preserved** (OS will not trash these) |
| D0, D1, A0, A1 | **Scratch** (may be destroyed by any OS call) |
| A4 | Global data pointer (VBCC; not used by OS) |
| A5 | Frame pointer (some compilers; not used by OS) |
| A6 | Library base — **always trashed to point to lib** |
| A7 | Stack pointer |

### Key rules:
- **A6 is always destroyed** — it holds the target library base after every OS call
- **D0, D1, A0, A1** are volatile — save them if needed across OS calls
- **FP0, FP1** are scratch if the FPU is present

---

## Example: `dos.library Write()`

From `fd/dos_lib.fd`:
```
Write(file,buffer,length)(d1,d2,d3)
```

```c
/* C call: */
LONG n = Write(fh, buf, 512);

/* Compiles to: */
MOVEA.L  _DOSBase, A6
MOVE.L   fh,    D1
MOVE.L   buf,   D2
MOVE.L   #512,  D3
JSR      -48(A6)
; D0 = bytes written (−1 = error)
```

---

## Preserved vs. Scratch Register Summary

```
Scratch (caller must save if needed):
    D0  D1  A0  A1  A6  FP0  FP1

Preserved (callee saves/restores):
    D2  D3  D4  D5  D6  D7
    A2  A3  A4  A5
    FP2  FP3  FP4  FP5  FP6  FP7
```

This matches the Motorola 68000 family software convention, but AmigaOS does **not** use A5 as a frame pointer (unlike the standard System V m68k ABI).

---

## Inter-Library Calls

When one library function calls another library internally, it must:

```asm
; save A6 (current lib base), load new lib base
MOVEM.L  A6, -(SP)
MOVEA.L  _GfxBase, A6
JSR      -102(A6)          ; graphics.library BltClear()
MOVEM.L  (SP)+, A6
```

Failure to save/restore A6 is a common bug in hand-written assembly library code.

---

## C Compiler Differences

### SAS/C 6.x
- Generates standard `MOVEA.L libbase,A6; JSR -lvo(A6)` via `#pragma amicall`
- Uses A5 as a frame pointer in non-leaf functions
- Stack frame: `LINK A5,#-N` on entry, `UNLK A5` on exit

### GCC (bebbo m68k-amigaos)
- Generates inline-asm stubs with explicit register constraints
- No frame pointer by default (`-fomit-frame-pointer`)
- D2–D7/A2–A3 saved on stack per function (ABI-compatible)

### VBCC
- Uses `__reg()` storage class for explicit register placement
- No frame pointer — tighter code than SAS/C for register-intensive functions

---

## Detecting the Calling Convention in IDA Pro

Pattern to identify an OS API call in disassembly:
```asm
MOVEA.L  (_DOSBase).L, A6     ; load library base
JSR      (-138,A6)            ; call at LVO −138
```

Cross-reference the LVO against the `.fd` file to identify the function. IDA's Amiga loader applies LVO names automatically when library definitions are present.

---

## References

- NDK39: `fd/*.fd` — register assignments per function
- *Amiga ROM Kernel Reference Manual: Libraries* — register conventions appendix
- SAS/C 6.x Programmer's Guide — calling convention chapter
- GCC m68k-amigaos (bebbo) — `libnix` inline headers
