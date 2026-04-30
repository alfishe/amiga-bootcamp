[← Home](../../../README.md) · [Reverse Engineering](../../README.md) · [Static Analysis](../README.md) · [Compilers](README.md)

# Lattice C 3.x/4.x — Reverse Engineering Field Manual

## Overview

**Lattice C** (versions 3.x–4.x, 1985–1989) is the direct predecessor to SAS/C. When SAS Institute acquired the Lattice C product line in 1988, they rebranded version 5.0 as "SAS/C". Lattice C 3.x and 4.x binaries represent the first generation of commercial C compilers for AmigaOS. Their code generation is recognizably similar to SAS/C but with less aggressive optimization and some distinct early patterns.

Key constraints:
- **The transition point**: Lattice C 3.x → 4.x → SAS/C 5.x form a continuous evolution. Code from 3.x looks noticeably "early" — simpler register allocation, less peephole optimization, longer function prologues.
- **LINK A5 + D2-D5/A2-A3 save** — Lattice C 3.x typically saves fewer registers than SAS/C (D2-D5 + A2-A3, 6 registers total) but more than Aztec C (5 regs, data only).
- **Startup code evolution** — Lattice C 3.x's `lc.o` startup is simpler than SAS/C's `c.o` — may not handle Workbench launches correctly, may not support `argc`/`argv` parsing.
- **Hunk names**: `CODE`, `DATA`, `BSS` (same as SAS/C — established this convention)

```asm
; Lattice C 3.x function prologue (less aggressive than SAS/C):
_func:
    LINK    A5, #-$14
    MOVEM.L D2-D5/A2-A3, -(SP)    ; 4 data + 2 address = 6 registers
    ; Compare: SAS/C saves D2-D7/A2-A4 (9 registers)
    ; Compare: Aztec C saves D3-D7 only (5 registers, data only)
```

---

## Binary Identification — Lattice C vs SAS/C

| Criterion | Lattice C 3.x | Lattice C 4.x | SAS/C 5.x/6.x |
|---|---|---|---|
| **Register save** | D2-D5, A2-A3 (6 regs) | D2-D6, A2-A3 (7 regs) | D2-D7, A2-A4 (9 regs) |
| **D6/D7 usage** | Rarely used | Sometimes used | Frequently used |
| **Peephole optimization** | Minimal | Moderate | Aggressive |
| **MOVEQ for small values** | Inconsistent | Common | Always |
| **Stack frame** | LINK A5 always | LINK A5 always | LINK A5 always |
| **Library calls** | `JSR -$XXX(A6)` | `JSR -$XXX(A6)` | `JSR -$XXX(A6)` |
| **Startup** | `lc.o` (simpler) | `lc.o` (improved) | `c.o` (full-featured) |
| **Era** | 1985–1987 | 1987–1989 | 1988–1996 |

### Evolutionary Markers

The Lattice→SAS/C evolution is visible in the binary:

1. **Register save set grows** — 6→7→9 registers as the optimizer learned to use more registers effectively
2. **MOVEQ adoption** — Lattice 3.x uses `MOVE.L #0, D0`; Lattice 4.x uses `MOVEQ #0, D0`; SAS/C always uses MOVEQ
3. **Library call density** — Lattice 3.x loads A6 before every single library call; SAS/C may reuse A6 across calls
4. **Stack frame size** — Lattice 3.x often allocates oversized frames (locals * sizeof(LONG) rounded up to nice boundary)

---

## Historical Context

Lattice, Inc. was an early cross-platform compiler vendor. Their C compiler for the Amiga was the first commercially viable option, shipping in 1985. Commodore itself used Lattice C for some system development before adopting SAS/C.

Key timeline:
- **1985**: Lattice C 3.0 — first commercial Amiga C compiler
- **1986**: Lattice C 3.1 — improved optimizer, bug fixes
- **1987**: Lattice C 4.0 — major update, AmigaOS 1.2 support
- **1988**: SAS Institute acquires Lattice C product line
- **1989**: Rebranded as SAS/C 5.0

Any binary from 1985–1989 is likely Lattice C. After 1989, the brand transitioned to SAS/C, though Lattice C was still sold through existing channels for a time.

Software likely compiled with Lattice C:
- Commodore's early Amiga utilities (1985–1986)
- Early third-party tools like `DiskMon`, `CLImate`, `Memacs`
- Amiga 1000 launch-era software
- Early versions of `ARP` (AmigaDOS Replacement Project) components
- Early `WShell` / `ZShell` versions

---

## Same C Function — Lattice C Output

```asm
; CountWords() — Lattice C 4.x:
; (Notably simpler than SAS/C — less aggressive optimizer)

_CountWords:
    LINK    A5, #-$08
    MOVEM.L D2-D4/A2, -(SP)       ; 4 regs saved (D2-D4 + A2)
    ; Note: A2 saved even though it's not used — Lattice C saves a fixed set
    
    MOVEQ   #0, D2                 ; D2 = count
    MOVEQ   #0, D3                 ; D3 = in_word
    
    MOVEA.L $08(A5), A0            ; A0 = str
    
    BRA     .loop_test              ; Lattice C uses BRA (long), not BRA.S

.loop_body:
    MOVE.L  #' ', D0               ; MOVE.L for char constant (should be MOVEQ!)
    CMP.B   (A0), D0
    BEQ     .not_word               ; BEQ (long), not BEQ.S
    
    MOVE.L  #'\t', D0
    CMP.B   (A0), D0
    BEQ     .not_word
    
    MOVE.L  #'\n', D0
    CMP.B   (A0), D0
    BEQ     .not_word
    
    TST.B   D3
    BNE     .next_char
    
    ADDQ.L  #1, D2
    MOVEQ   #1, D3
    BRA     .next_char

.not_word:
    MOVEQ   #0, D3

.next_char:
    ADDQ.L  #1, A0

.loop_test:
    TST.B   (A0)
    BNE     .loop_body

    MOVE.L  D2, D0
    MOVEM.L (SP)+, D2-D4/A2
    UNLK    A5
    RTS
```

**Lattice C observations**:
1. **`MOVE.L #' ', D0`** instead of `MOVEQ #' ', D0` — Lattice C doesn't always use MOVEQ for constants that fit in 8 bits. This wastes 2 bytes and 4 cycles per constant load.
2. **`BRA`/`BEQ`/`BNE`** (long, 4-byte) instead of `BRA.S`/`BEQ.S`/`BNE.S` (short, 2-byte) — Lattice C's branch target distance calculation is conservative.
3. **A2 saved but unused** — Lattice C saves a fixed register set rather than analyzing which registers are actually needed.

---

## Differences from SAS/C — Summary

```
Lattice C 3.x/4.x → SAS/C 5.x/6.x improvements visible in disassembly:
  ✓ MOVEQ substituted for MOVE.L #small_const
  ✓ BRA.S/BEQ.S/BNE.S used where target is within 8-bit range
  ✓ Dead register saves eliminated (per-function save analysis)
  ✓ Common subexpression elimination (CSE) more aggressive
  ✓ Loop induction variables kept in registers, not on stack
  ✓ Struct copy inlined as MOVE.L (A0)+, (A1)+ for small structs
  ✓ Tail-call optimization in some cases (rare but present in SAS/C 6.x)
```

---

## References

- [compiler_fingerprints.md](../../compiler_fingerprints.md) — Quick identification
- *Lattice C 3.x/4.x Manual* (archive.org)
- See also: [sasc.md](sasc.md) — SAS/C (direct successor)
- See also: [aztec_c.md](aztec_c.md) — contemporary competitor
