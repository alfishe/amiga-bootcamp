[← Home](../README.md) · [Reverse Engineering](README.md)

# Compiler Fingerprints — Identifying the Toolchain

## Overview

Knowing which compiler produced an Amiga binary dramatically reduces reverse engineering effort. Each compiler has distinctive code generation patterns at the function prologue, epilogue, calling sequence, and global variable access levels.

---

## SAS/C 6.x Fingerprints

### Function Prologue
```asm
; Classic SAS/C stack frame with A5 as frame pointer:
LINK    A5, #-N              ; allocate N bytes on stack
MOVEM.L D2-D7/A2-A4, -(SP)  ; save callee-saved registers
```

Alternatively (small functions):
```asm
LINK    A5, #0               ; minimal frame (no locals)
MOVE.L  D2, -(SP)            ; save only used regs
```

### Function Epilogue
```asm
MOVEM.L (SP)+, D2-D7/A2-A4  ; restore registers (reverse order)
UNLK    A5                   ; deallocate stack frame
RTS                          ; return
```

### Global Variable Access
```asm
; SAS/C: absolute addressing (with HUNK_RELOC32):
MOVE.L  $0000BEEF, D0        ; absolute address — gets relocated
MOVEA.L _DOSBase, A6         ; load from global via absolute ref
```

### Library Calls
```asm
MOVEA.L _DOSBase, A6         ; always load from named global
JSR     -48(A6)              ; Write LVO
```

### Identifying Strings
Look for:
- `"dos.library"` string in DATA hunk — opened by startup
- `"SAS/C"` or `"SAS C"` in the ID string of any custom library written with SAS/C
- The startup `_ReturnCode` variable name in HUNK_SYMBOL

---

## GCC (m68k-amigaos / bebbo) Fingerprints

### Function Prologue
```asm
; GCC: no frame pointer (default -fomit-frame-pointer)
MOVEM.L D2/D3/A2, -(SP)     ; save only actually-used regs
; (no LINK instruction)
```

Or with frame pointer (`-fno-omit-frame-pointer`):
```asm
LINK    A6, #-N              ; GCC uses A6 as frame pointer (not A5!)
MOVEM.L D2/A2, -(SP)
```

> [!NOTE]
> GCC uses **A6** as frame pointer when frame pointers are enabled. SAS/C uses **A5**. This is the primary disambiguation between the two.

### Function Epilogue
```asm
MOVEM.L (SP)+, D2/D3/A2     ; restore
RTS
; (no UNLK — GCC prefers to adjust SP directly)
```

### Global Variable Access (PC-relative)
```asm
; GCC -fpic: PC-relative access to globals:
LEA     _SysBase(PC), A0    ; PC-relative address of global
MOVEA.L (A0), A6            ; dereference to get library base

; Alternative (without PIC):
MOVEA.L (_DOSBase).L, A6    ; absolute with reloc (similar to SAS/C)
```

### Library Calls
```asm
; GCC inline stubs emit 16-bit short JSR:
JSR     -198(A6)            ; same visual result as SAS/C
```

But the surrounding code differs:
```asm
; GCC: tighter register use, less stack traffic
MOVEA.L (_SysBase).L, A6
MOVE.L  #$400, D0           ; byteSize
MOVE.L  #2, D1              ; MEMF_CHIP
JSR     -198(A6)            ; AllocMem
```

### Identifying Strings
- `"libnix"` or `"clib2"` version strings in DATA hunk
- GCC version string in `.comment` section (if present): `"GCC 6.5.0b ..."`
- `__main`, `__exit`, `__parse_args` as function names from HUNK_SYMBOL

---

## VBCC Fingerprints

VBCC is the most common modern AmigaOS compiler and produces very clean, standards-compliant code.

### Function Prologue
```asm
; VBCC: highly similar to GCC, no LINK by default
MOVEM.L D2-D5/A2-A3, -(SP)  ; exact set of used regs
```

### Distinguishing VBCC from GCC

| Pattern | GCC | VBCC |
|---|---|---|
| `__saveds` keyword | Yes (some stubs) | Yes |
| Tail calls via JMP | Rare | Common |
| Stack checking | Optional (`-stack-check`) | Optional |
| `move.l #imm, An` | `movea.l #imm, An` | Same |
| BRA to epilogue | Sometimes | Common |
| register int a0 | Supported | Supported |

VBCC often generates more BRA→epilogue patterns where GCC inlines the epilogue code.

### Identifying Strings
- `"vbcc"` in any metadata strings
- VBCC version string: `"vbcc (c) in 1995-2020 by Volker Barthelmann"`

---

## Aztec C / Manx C

Rare but present in 1.x/2.x era software. Distinctive:

```asm
; Aztec C: uses A4 as small-data register (AmigaOS __far model)
MOVEA.L _DOSBase, A6         ; absolute refs
MOVE.L  A4, -(SP)            ; A4 preserved (small-data base)
```

Aztec C often uses a different calling convention for internal functions — examine carefully before assuming standard lib-call convention.

---

## StormC / StormC++

Native IDE with C++ support. C-level code mimics SAS/C:

```asm
; StormC C function (SAS/C compatible):
LINK    A5, #-$10
MOVEM.L D2-D7/A2-A4, -(SP)
```

**Distinguishing features:**
- HUNK_DEBUG contains project metadata/source paths
- C++ methods use custom mangling: `__ct__6Window` (constructor), `__dt__` (destructor)
- C++ Vtable layout starts directly at first method (no `offset_to_top`)
- May contain `PPC_CODE` hunks for WarpOS binaries

---

## Lattice C 3.x/4.x

The predecessor to SAS/C (1985-1989 era).

```asm
; Lattice C 3.x/4.x:
LINK    A5, #-$14
MOVEM.L D2-D5/A2-A3, -(SP)    ; Saves fewer regs than SAS/C
```

**Distinguishing features:**
- Saves only 6-7 registers instead of SAS/C's 9.
- Uses `MOVE.L #small_val, D0` instead of `MOVEQ`.
- Uses long branches (`BRA`, `BEQ`) instead of short branches (`BRA.S`).

---

## DICE C

Lean, fast compiler by Matt Dillon.

```asm
; DICE C:
MOVEM.L D2-D4/A2-A3, -(SP)    ; Per-function save, no frame pointer
```

**Distinguishing features:**
- Extremely similar to VBCC/GCC (no frame pointer).
- Entry point is uniquely named `_mainCRTStartup`.
- Often uses `ADDQ.L #4, SP` to clean up stack arguments.
- Uses `MOVEA.L (_LibBase).L, A6` for library calls.

---

## Hand-Written Assembly (Assembler-Only Code)

Unlike compiler-generated code with predictable prologues and calling sequences, hand-written 68000 assembly (common in demos, games, and bootblocks) is unconstrained. 

**Distinguishing features:**
- **No `LINK` or `SUBQ.L #N,SP`** in the entire binary.
- **Custom Hardware Base Pointers:** Authors often dedicate a register (typically `A4` or `A5`) to `$DFF000` (custom chip base) for the entire program: `LEA $DFF000, A4`.
- **Ad-hoc Calling Conventions:** Parameters passed in arbitrary registers. `A6` might be used as a data pointer rather than the library base.
- **Maximally Specified Saves:** `MOVEM.L D0-D7/A0-A6, -(SP)` used aggressively for interrupt handlers or per-routine saves, rather than the compiler's minimal necessary set.
- **Self-Modifying Code (SMC):** `MOVE.W #imm, (next_insn+2, PC)` to patch instructions at runtime.
- **Hardware Register Banging:** Direct immediate access to `$DFFxxx` (custom chips), `$BFExxx` (CIAA), and `$BFDxxx` (CIAB). 
- **PC-Relative Data Tables:** `LEA table(PC), An` used for copper lists, sprite data, and audio samples mixed within the `CODE` hunk.

> [!TIP]
> For a deep dive into reversing hand-written Amiga assembly, see the **[Hand-Written Assembly Field Manual](static/asm68k_binaries.md)**.

### Assembler Toolchain Fingerprints

Because macro assemblers translate mnemonics 1:1, they lack the rigid calling conventions of C compilers. However, the choice of assembler (and the era it belongs to) can leave subtle forensic clues in the binary:

| Assembler | Era / Usage | Binary Fingerprints & Output Characteristics |
|---|---|---|
| **ASM-One** (and ASM-Pro) | 1990s Demoscene Standard | **Literal Translation:** Early versions did not automatically optimize `MOVE.L #0, Dn` to `MOVEQ`.<br>**Section Merging:** Often outputs a single giant `CODE` hunk containing data, copper lists, and BSS because coders frequently omitted `SECTION` directives.<br>**Symbols:** `HUNK_SYMBOL` tables lack the `_` prefix typical of C linkers.<br>**Relocation Ordering:** Unlike external linkers that group `HUNK_RELOC32` arrays strictly by target hunk, ASM-One's single-pass compilation often emits a single massive relocation block at the end of the file in sequential generation order. |
| **Seka / K-Seka** | 1980s Early Demoscene | **The Literal Extreme:** Absolutely zero optimization. What you write is what you get.<br>**Compact output:** Often used for bootblocks and 4K intros; does not generate standard Amiga hunks natively unless explicitly coded to do so. |
| **Devpac (HiSoft)** | 1980s-90s "Pro" Standard | **Disciplined Hunks:** Devpac encouraged proper `SECTION CODE,CODE` and `SECTION DATA,DATA` usage, resulting in cleanly separated binary hunks.<br>**Optimization:** Featured early peephole optimization (short branches, `MOVEQ`).<br>**Debug Hunks:** Devpac injects proprietary debug structures. Look for `HUNK_DEBUG` ($03F1) blocks containing the `"HCLN"` (HiSoft Compressed Line Numbers) or `"LINE"` ASCII signatures, and unique Devpac-only hunk types like `HUNK_DEXT` ($03F7) and `HUNK_DREL32` ($03F8). |
| **PhxAss** | Late 90s Performance | **Aggressive Optimization:** Automatically shrinks `MOVE.L` to `MOVEQ`, and `LEA/JMP` to PC-relative `BSR/BRA` where possible.<br>**Object Linking:** Often output object files linked via `Blink`. `Blink` leaves its own structural fingerprints, strictly ordering `HUNK_RELOC32` offsets in ascending order per target hunk, and cleanly terminating relocation arrays. |
| **Barfly** | 1990s High-Speed | Extremely fast. Output binaries are functionally similar to PhxAss, often utilizing external linkers and producing highly optimized instruction sequences. |
| **vasm** | Modern Cross-Assembler | Can emulate the syntax and output style of Devpac (`-m68000 -Fhunkexe -phxass`) or ASM-One, making its footprint identical to the legacy assembler it is configured to mimic. |

---

## Quick Fingerprint Checklist

```
□ Does function prologue use LINK A5?  → SAS/C, StormC (C mode), or Lattice C
  ↳ Saves D2-D5/A2-A3?                 → Lattice C
  ↳ Has __ct__/__dt__ or project paths?→ StormC
  ↳ Saves D2-D7/A2-A4, absolute refs?  → SAS/C
□ Does function prologue use LINK A6?  → GCC with -fno-omit-frame-pointer
□ No LINK at all, just MOVEM.L?        → GCC, VBCC, or DICE C
  ↳ Entry point is _mainCRTStartup?    → DICE C
□ PC-relative globals (LEA x(PC))?     → GCC -fpic, VBCC, or DICE C
□ Absolute globals + HUNK_RELOC32?     → SAS/C, StormC, Lattice, or GCC without -fpic
□ HUNK_SYMBOL has __main, __exit?      → GCC/libnix
□ HUNK_SYMBOL has _c_start, _main?     → SAS/C
```

---

## References

- SAS/C 6.x Programmer's Guide — code generation appendix
- GCC m68k-amigaos port (bebbo): https://github.com/bebbo/amiga-gcc
- VBCC manual: http://www.ibaug.de/vbcc/doc/vbcc.html
- Aztec C 68k manual (archive.org)
- **Amiga ROM Kernel Reference Manual (RKRM): Includes and Autodocs** — Definitive source for standard Commodore Hunk IDs (`HUNK_CODE`, `HUNK_RELOC32`, `HUNK_DEBUG`).
- **AmigaDOS Executable Format Documentation** — Details the loader's behavior of skipping unrecognized hunk blocks, which allowed for proprietary debugger extensions.
- **HiSoft Devpac Amiga Assembler Manual** — Primary source for understanding `"HCLN"` (HiSoft Compressed Line Numbers) and its proprietary `HUNK_DEXT` / `HUNK_DREL32` structures.
- **Amiga Development Wiki (Wikidot)** — Excellent community repository documenting the exact bit-layout of the reverse-engineered `HCLN` compression scheme.
- **English Amiga Board (EAB) / Aminet Archives** — Primary historical source for the demoscene evolution of ASM-One, Seka, and PhxAss, including their specific linking behaviors and macro habits.
- **[Per-Compiler RE Field Manuals](static/compilers/README.md)** — In-depth binary analysis for each compiler
  - [SAS/C](static/compilers/sasc.md) · [GCC](static/compilers/gcc.md) · [VBCC](static/compilers/vbcc.md) · [StormC](static/compilers/stormc.md) · [Aztec C](static/compilers/aztec_c.md) · [Lattice C](static/compilers/lattice_c.md) · [DICE C](static/compilers/dice_c.md)
- [code_vs_data_disambiguation.md](static/code_vs_data_disambiguation.md) — distinguishing code bytes from data/variables
