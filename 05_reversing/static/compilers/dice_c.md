[← Home](../../../README.md) · [Reverse Engineering](../../README.md) · [Static Analysis](../README.md) · [Compilers](README.md)

# DICE C — Reverse Engineering Field Manual

## Overview

**DICE C** (by Matt Dillon, 1992–1995) was a fast, lean C compiler for AmigaOS known for its incredible compilation speed — often 10–50× faster than SAS/C. It was the compiler of choice for rapid development cycles and produced tight, no-frills code. Its key RE characteristics: **no frame pointer** (like GCC/VBCC), **PC-relative string addressing** (like GCC), and **minimal register saves** (per-function, like VBCC). DICE C binaries look most similar to VBCC output but with some distinctive patterns.

Key constraints:
- **No frame pointer** — DICE C omits the frame pointer by default. Functions use SP-relative addressing.
- **PC-relative strings** — Like GCC and VBCC, DICE uses `LEA string(PC), A0`.
- **Extremely fast compilation** — DICE's speed came from a simpler optimizer; the binary output is clean but not as aggressively optimized as SAS/C -O2 or GCC -O2.
- **Custom startup** — `_mainCRTStartup` (not `_start`) is the typical entry point name.
- **Hunk names**: `CODE`, `DATA`, `BSS` (Amiga standard)

```asm
; DICE C function — no frame pointer, PC-relative, per-function save:
_func:
    MOVEM.L D2-D4/A2-A3, -(SP)    ; save only what's used
    ; ... function body, SP-relative access ...
    MOVEM.L (SP)+, D2-D4/A2-A3
    RTS
```

---

## Binary Identification

| Criterion | DICE C | SAS/C | GCC | VBCC |
|---|---|---|---|---|
| **Frame pointer** | None | A5 always | A6 or none | None |
| **String addressing** | PC-relative | Absolute + reloc | PC-relative | PC-relative |
| **Register save** | Per-function | Fixed 9 regs | Per-function | Per-function |
| **Startup entry** | `_mainCRTStartup` | `_start` | `_start` | `_start` |
| **Hunk names** | `CODE`, `DATA`, `BSS` | `CODE`, `DATA`, `BSS` | `.text`, `.data`, `.bss` | `CODE`, `DATA`, `BSS` |
| **Optimizer** | Moderate | Aggressive | Aggressive | Aggressive (peephole) |
| **Compile speed** | Very fast | Moderate | Slow | Fast |

### Key Distinguishing Patterns

1. **`_mainCRTStartup` entry point** — unique to DICE C. No other Amiga compiler uses this name for the startup entry.
2. **`ADDQ.L #4, SP` argument cleanup** — DICE C often uses `ADDQ` to pop arguments after function calls, where SAS/C would use `LEA`.
3. **Conservative optimization** — DICE C may not perform CSE or loop-invariant code motion as aggressively as SAS/C or GCC.

---

## Library Call Patterns

```asm
; DICE C library call:
    MOVEA.L (_SysBase).L, A6
    JSR     -$C6(A6)              ; AllocMem
    ; DICE C may not cache A6 — reloads from global for each call block
```

DICE C is notable for using **`MOVEA.L (_LibBase).L, A6`** (absolute long with relocation) rather than `MOVEA.L _LibBase, A6` (absolute with reloc). The `().L` suffix is a DICE C assembler convention that appears in the disassembly.

---

## Historical Context

**Matt Dillon** (later known for DragonFly BSD, the HAMMER filesystem, and the D compiler) wrote DICE C as a side project while developing Amiga software. Its claim to fame was compiling the entire DICE C compiler itself in **under 10 seconds** on a stock Amiga 3000 — a feat SAS/C needed minutes for.

DICE C was particularly popular in the Amiga demoscene and shareware community, where fast edit-compile-test cycles mattered more than squeezing every last cycle out of the generated code. It also shipped with a suite of development tools including a linker, librarian, and debugger.

DICE C's development effectively ended when Matt Dillon moved to FreeBSD development in the mid-1990s. The final version was released as freeware.

Software known or likely to use DICE C:
- **DICE C itself** (self-hosting — compiled with DICE C)
- Various Amiga shareware utilities (1992–1995 era)
- Some demoscene tools and intros
- Early Amiga networking utilities

---

## Same C Function — DICE C Output

```asm
; CountWords() — DICE C:
; (No frame pointer, PC-relative strings, per-function save)

_CountWords:
    MOVEM.L D2-D3, -(SP)          ; save D2-D3 only
    
    MOVEQ   #0, D2                 ; D2 = count
    MOVEQ   #0, D3                 ; D3 = in_word
    
    MOVEA.L $0C(SP), A0            ; A0 = str (SP+12, after saved regs + ret addr)
    
    BRA.S   .loop_test

.loop_body:
    MOVEQ   #' ', D0
    CMP.B   (A0), D0
    BEQ.S   .not_word
    MOVEQ   #'\t', D0
    CMP.B   (A0), D0
    BEQ.S   .not_word
    MOVEQ   #'\n', D0
    CMP.B   (A0), D0
    BEQ.S   .not_word
    
    TST.B   D3
    BNE.S   .next_char
    ADDQ.L  #1, D2
    MOVEQ   #1, D3
    BRA.S   .next_char

.not_word:
    MOVEQ   #0, D3

.next_char:
    ADDQ.L  #1, A0

.loop_test:
    TST.B   (A0)
    BNE.S   .loop_body

    MOVE.L  D2, D0
    MOVEM.L (SP)+, D2-D3
    RTS
```

**DICE C observations**: For this simple function, DICE C's output is nearly identical to GCC and VBCC. The distinction emerges in:
- **Startup code naming** (`_mainCRTStartup` vs `_start`)
- **Argument cleanup patterns** (`ADDQ.L #4, SP` after calls)
- **Less aggressive CSE** in more complex functions

---
## References

- [compiler_fingerprints.md](../../compiler_fingerprints.md) — Quick identification
- DICE C distribution (Aminet: `dev/c/dice`)
- Matt Dillon's DICE C documentation (archive.org)
- See also: [sasc.md](sasc.md), [gcc.md](gcc.md), [vbcc.md](vbcc.md) — compare with other compilers
