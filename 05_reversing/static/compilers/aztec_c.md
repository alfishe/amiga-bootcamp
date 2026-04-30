[← Home](../../../README.md) · [Reverse Engineering](../../README.md) · [Static Analysis](../README.md) · [Compilers](README.md)

# Manx Aztec C — Reverse Engineering Field Manual

## Overview

**Manx Aztec C** (versions 3.x–5.x, 1985–1992) was the first widely used C compiler for the Amiga, predating Lattice C's market dominance. It targets early AmigaOS (1.1–1.3) and produces code with a distinctive **`LINK A5, #-N` + `MOVEM.L D3-D7, -(SP)`** prologue — saving only 5 data registers (D3–D7) instead of SAS/C's 9 registers. This narrower save set is the single most reliable Aztec C fingerprint.

Key constraints:
- **5-register data save (D3–D7 only)** — Aztec C preserves fewer registers than any other Amiga C compiler. D2 is considered scratch by Aztec, while SAS/C, GCC, and VBCC all preserve D2.
- **A5 frame pointer** — standard `LINK A5, #-N` convention, like SAS/C.
- **Absolute string addressing** — like SAS/C, strings are in DATA with `HUNK_RELOC32` relocation.
- **Pre-MakeLibrary era** — Aztec C libraries use a different initialization pattern than later RTF_AUTOINIT libraries.
- **Early AmigaOS focus** — code may assume OS 1.1/1.2 behavior that changed in 2.0+.

```asm
; Aztec C function prologue (THE signature):
_func:
    LINK    A5, #-$14               ; allocate frame
    MOVEM.L D3-D7, -(SP)           ; save D3-D7 ONLY (5 regs!)
    ; Note: D2 is NOT saved (unlike SAS/C, GCC, VBCC)
    ; Note: A2-A4 are not saved (unlike SAS/C)
```

---

## Binary Identification

| Criterion | Aztec C | SAS/C |
|---|---|---|
| **Register save** | `D3-D7` (5 regs) | `D2-D7/A2-A4` (9 regs) |
| **D2 preservation** | NOT preserved — call-clobbered | Preserved — callee-saved |
| **A2-A4 preservation** | NOT preserved by default | Always preserved |
| **Frame pointer** | A5 (`LINK A5`) | A5 (`LINK A5`) |
| **String addressing** | Absolute + relocation | Absolute + relocation |
| **Startup module** | `aztec.o` | `c.o` |
| **Hunk names** | `CODE`, `DATA`, `BSS` | `CODE`, `DATA`, `BSS` |
| **Era** | 1985–1992 (OS 1.1–1.3) | 1988–1996 (OS 1.2–3.1) |

### Detecting D2 as Scratch Register

The most distinctive Aztec C behavior: **D2 is call-clobbered**. After a function call, Aztec C must reload D2 if it was using it. SAS/C, GCC, and VBCC all preserve D2 across calls.

```asm
; Aztec C: D2 is NOT preserved across calls
    MOVE.L  #value, D2             ; D2 = important value
    BSR     _some_func             ; D2 may be destroyed!
    MOVEQ   #0, D2                 ; reload D2 (Aztec C knows D2 is scratch)
    ; SAS/C would NOT need this reload — D2 is callee-saved there
```

---

## Historical Context

Manx Software Systems produced Aztec C for multiple platforms (CP/M, DOS, Macintosh, Amiga, Atari ST). The Amiga version was one of the earliest C compilers available — released in 1985 alongside the Amiga 1000 launch. Its 5-register save convention (D3-D7 only) reflects the era's emphasis on minimizing prologue/epilogue overhead on the 7.14 MHz 68000.

Aztec C was superceded by Lattice C (which became SAS/C) in the late 1980s, though Manx continued to release versions into the early 1990s. Most Aztec C binaries date from 1985–1989 — the Amiga's formative years.

Software known to use Aztec C:
- Early Amiga utilities (1985–1987 era)
- Some Commodore-developed tools
- ABasiC (the Amiga BASIC compiler)
- Early versions of certain games ported from other platforms

---

## Same C Function — Aztec C Output

```asm
; CountWords() — Manx Aztec C 5.x:
; (Note: smaller register save set, but structurally similar to SAS/C)

_CountWords:
    LINK    A5, #-$08
    MOVEM.L D3-D4, -(SP)           ; ONLY D3-D4 (not D2-D3!)
    
    MOVEQ   #0, D3                  ; D3 = count
    MOVEQ   #0, D4                  ; D4 = in_word
    
    MOVEA.L $08(A5), A0             ; str
    
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
    
    TST.B   D4
    BNE.S   .next_char
    ADDQ.L  #1, D3
    MOVEQ   #1, D4
    BRA.S   .next_char

.not_word:
    MOVEQ   #0, D4

.next_char:
    ADDQ.L  #1, A0

.loop_test:
    TST.B   (A0)
    BNE.S   .loop_body

    MOVE.L  D3, D0
    MOVEM.L (SP)+, D3-D4
    UNLK    A5
    RTS
```

**Aztec C observations**: The function body is nearly identical to SAS/C, but notice D2 is **not used** — Aztec C skips D2 and starts local register allocation at D3. If you see functions that never touch D2, it's likely Aztec C (or early Lattice C).

---
## References

- [compiler_fingerprints.md](../../compiler_fingerprints.md) — Quick identification
- Aztec C 68k Manual (archive.org)
- See also: [sasc.md](sasc.md), [lattice_c.md](lattice_c.md) — compare with other compilers
