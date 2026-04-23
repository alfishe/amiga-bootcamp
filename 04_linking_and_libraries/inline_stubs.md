[← Home](../README.md) · [Linking & Libraries](README.md)

# Compiler Inline Stubs

## Overview

AmigaOS library functions are not called via the C standard ABI. Every call goes through a **negative-offset JMP table** relative to a library base pointer held in an address register (conventionally A6). Compiler vendors each solve this differently:

- **SAS/C** — `#pragma` headers and `inline/` headers
- **GCC (m68k-amigaos)** — inline-assembly `__attribute__((regparm))` stubs
- **VBCC** — `__reg()` storage class and module pragmas

All approaches ultimately compile to the same machine code:

```asm
MOVEA.L  _DOSBase, A6
JSR      -LVO(A6)          ; e.g. JSR -138(A6) for dos.library Output()
```

---

## SAS/C: Pragma-Based Stubs

### Pragma Syntax

SAS/C uses `#pragma` directives to declare register assignments:

```c
#pragma amicall(DOSBase, 0x008A, Open(D1, D2))
```

- `DOSBase` — global holding the library base (placed in A6 automatically)
- `0x008A` — LVO offset (hex)
- `Open(D1, D2)` — function name and register allocation for arguments

### Include Structure (NDK39)

```
NDK39/
  include/
    pragmas/
      dos_pragmas.h      ← #pragma amicall directives for dos.library
      exec_pragmas.h     ← exec.library pragmas
      graphics_pragmas.h
      ...
    inline/
      dos.h              ← Alternative: inline-macro stubs (SAS/C 6.x)
```

Usage:
```c
#include <clib/dos_protos.h>    /* ANSI prototypes */
#include <pragmas/dos_pragmas.h> /* register pragmas */

extern struct DosLibrary *DOSBase;

BPTR fh = Open("foo", MODE_OLDFILE);   /* expands to JSR -30(A6) */
```

### Pragma-Generated Code

```asm
; Open("foo", MODE_OLDFILE)
MOVE.L   #MODE_OLDFILE, D2
MOVE.L   #_str_foo, D1
MOVEA.L  _DOSBase, A6
JSR      -30(A6)
; Return value in D0
```

No stack frame involved — pure register passing.

---

## GCC (m68k-amigaos): Inline Assembly Stubs

### Modern Approach (GCC 6.x+ / bebbo cross-compiler)

The NDK provides `<proto/dos.h>` which pulls in compiler-specific stubs. Under bebbo GCC:

```c
/* auto-generated stub in clib2 / libnix */
static inline BPTR __attribute__((always_inline))
Open(CONST_STRPTR name, LONG accessMode)
{
    register BPTR __ret __asm("d0");
    register struct DosLibrary *const __DOSBase __asm("a6") = DOSBase;
    register CONST_STRPTR __name __asm("d1") = name;
    register LONG __accessMode __asm("d2") = accessMode;
    __asm volatile ("jsr %%a6@(-30:W)"
        : "=r"(__ret)
        : "r"(__DOSBase), "r"(__name), "r"(__accessMode)
        : "d1", "a0", "a1", "fp0", "fp1", "cc", "memory");
    return __ret;
}
```

Key points:
- `__asm("a6")` forces the library base into A6
- `__asm("d1")`, `__asm("d2")` — per-function register assignments from `.fd` file
- `"jsr %%a6@(-30:W)"` — 16-bit signed displacement form (most efficient)
- Clobbers declared explicitly to prevent register allocation conflicts

### Older GCC (< 6.x): `__OLDSTYLE__` macros

```c
#define Open(name, mode)  \
    ({ BPTR _r; \
       __asm volatile ("movea.l %2,a6; jsr -30(a6)" : "=d"(_r) : \
                       "d"(name), "d"(mode), "m"(DOSBase) : "a6"); \
       _r; })
```

Less elegant — explicitly moves DOSBase to A6 inside the macro.

---

## VBCC: `__reg()` Storage Class

VBCC uses a compiler extension to place variables in specific registers:

```c
/* vbcc style */
BPTR __reg("d0") Open(__reg("d1") CONST_STRPTR name,
                      __reg("d2") LONG mode);
#pragma amicall(DOSBase, 0x1E, Open(d1,d2))
```

VBCC automatically inserts `MOVEA.L DOSBase,A6` and `JSR -30(A6)`.

Module pragma file (`dos.fd`-derived):
```
##base DOSBase
##bias 30
Open(name,accessMode)(d1,d2)
##bias 36
Close(file)(d1)
...
```

---

## Generated Machine Code (All Compilers)

For `Write(fh, buf, len)` at LVO −48 (`$30`):

```asm
MOVEA.L  _DOSBase, A6       ; load library base into A6
MOVE.L   fh_var,  D1        ; BPTR filehandle → D1
MOVE.L   buf_ptr, D2        ; buffer address  → D2
MOVE.L   len_val, D3        ; byte count      → D3
JSR      -48(A6)            ; call Write()
; D0 = bytes actually written, or -1 on error
```

---

## Register Allocation Convention

All AmigaOS library functions follow this invariant:

| Register | Role |
|---|---|
| A6 | Library base (always) |
| D0 | Return value (32-bit) |
| D0+D1 | 64-bit return (rare: `DivideU`) |
| D1–D7, A0–A3 | Arguments (per `.fd` file) |
| A4, A5 | Scratch in OS (do not rely on preservation) |
| D2–D7, A2–A3 | **Preserved** by OS calls (callee-saved) |

A compiler stub must:
1. Load arguments into exact registers from the `.fd` specification
2. Load the library base into A6
3. Execute `JSR -LVO(A6)`
4. Collect the return value from D0

---

## Stub Generation Tools

| Tool | Input | Output |
|---|---|---|
| `fd2pragma` (SAS) | `.fd` file | `#pragma amicall` header |
| `fd2inline` | `.fd` file | GCC inline-asm header |
| `fd2sfd` | `.fd` file | SFD (Amiga DevKit) format |
| `cvinclude.pl` | `.fd` + `.sfd` | VBCC pragma headers |

NDK39 ships pre-generated `pragmas/` and `inline/` directories — you only need to run these tools when writing a new library.

---

## References

- NDK39: `include/pragmas/`, `include/inline/`, `fd/`
- SAS/C 6.x Programmer's Reference Manual — chapter on pragmas
- GCC for Amiga (bebbo): `m68k-amigaos-gcc` repo, `libnix` stubs
- VBCC manual: http://www.compilers.de/vbcc.html — register specification chapter
- vlink documentation: http://sun.hasenbraten.de/vlink/
