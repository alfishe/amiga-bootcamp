[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Compiler-Specific Code Generation Patterns

## Overview

Different Amiga compilers produce distinct code signatures. Recognising these helps quickly identify compiler origin, locate `main()`, and distinguish OS glue from application logic.

---

## SAS/C 6.x Patterns

### Function Prologue / Epilogue

```asm
; Non-leaf function with local vars:
LINK    A5, #-N          ; allocate N bytes of locals on stack
MOVEM.L D2-D7/A2-A3, -(SP)  ; save preserved registers
...
MOVEM.L (SP)+, D2-D7/A2-A3
UNLK    A5
RTS

; Leaf function (no locals, no preserved regs):
; — no LINK, pure computation, ends in RTS
```

### D0 Save Pattern

SAS/C saves D0 at the start of functions that need it later:

```asm
MOVE.L  D0, -(SP)       ; save return value from previous call
JSR     another_func
MOVE.L  (SP)+, D0       ; restore
```

### Register Argument Passing

SAS/C passes OS call args via `#pragma amicall` register placement. Inside application functions, SAS/C uses a **stack-based C ABI** (unlike OS calls):

```asm
; C function call in SAS/C: push args right-to-left
MOVE.L  arg3, -(SP)
MOVE.L  arg2, -(SP)
MOVE.L  arg1, -(SP)
JSR     _myfunction
ADDQ.L  #12, SP         ; clean args (caller cleanup)
```

### String Constants

SAS/C places string literals in the **data hunk**, referenced via absolute addresses requiring `HUNK_RELOC32`:

```asm
MOVE.L  #_str_hello, D1   ; absolute address → RELOC32 entry
MOVEA.L _DOSBase, A6
JSR     (-48,A6)           ; Write(stdout, "hello", ...)
```

---

## GCC (m68k-amigaos / bebbo) Patterns

### PC-Relative String Access

GCC uses PC-relative addressing by default, eliminating most HUNK_RELOC32 entries:

```asm
LEA     _str_hello(PC), A0   ; PC-relative — no reloc needed
```

### No Frame Pointer (Default)

```asm
; GCC -O2 leaf function:
MOVEM.L D2/A2, -(SP)    ; only save what's used
...
MOVEM.L (SP)+, D2/A2
RTS
; No LINK/UNLK — pure register allocation
```

### GCC Function Prologues

```asm
; Non-leaf with GCC -fno-omit-frame-pointer:
LINK    A6, #-N          ; note: GCC uses A6 as frame pointer here
                         ; (conflicts with OS library base usage — rare)
; More common with -O2:
SUBQ.L  #N, SP           ; allocate locals without frame pointer
```

### Integer Division / Modulo

GCC emits calls to `__divsi3`, `__modsi3` from `libgcc`:

```asm
JSR     ___divsi3        ; 32-bit signed divide (libgcc helper)
; operands in D0:D1, result in D0
```

SAS/C uses the 68k `DIVS.L` instruction directly (available on 020+) or `DIVS.W`.

---

## VBCC Patterns

VBCC generates very tight code with minimal function overhead:

```asm
; VBCC typical function (no frame pointer, minimal saves):
MOVEM.L D2-D4, -(SP)
...
MOVEM.L (SP)+, D2-D4
RTS
```

VBCC's OS call inline expansion looks identical to GCC's inline-asm stubs.

---

## Distinguishing Compiler Artefacts from Logic

| Pattern | Compiler | Meaning |
|---|---|---|
| `LINK A5, #-N` | SAS/C | Function with locals |
| `LINK A6, #-N` | GCC (rare) | Frame pointer mode |
| `JSR ___divsi3` | GCC | Software 32-bit division |
| `DIVS.L D1, D0` | SAS/C (020+) | Hardware divide |
| `MULS.L D1, D0` | SAS/C (020+) | Hardware multiply |
| `LEA str(PC), A0` | GCC | PC-relative string ref |
| `MOVE.L #_str, D1` | SAS/C | Absolute string ref (reloc'd) |
| `JSR _main` | Startup | C main() entry point |
| `MOVE.L 4.W, A6` | Startup | SysBase load |
| `JSR -552(A6)` | Any | exec.library OpenLibrary |

---

## Locating `main()` via Startup Skip

After identifying the startup stub (`MOVE.L 4.W, A6` → `JSR _OpenLibraries`):

1. Find the first `JSR` or `BSR` after library opens
2. That target is `__main` or directly `_main`
3. If `__main`: follow its internal `JSR _main` call
4. Label the target `main` in IDA

---

## References

- SAS/C 6.x manual — code generation chapter
- GCC for m68k: https://github.com/bebbo/amiga-gcc
- VBCC manual: http://www.compilers.de/vbcc.html
- *Amiga ROM Kernel Reference Manual: Libraries* — register conventions
