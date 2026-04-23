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

## Assembler-Only Code

Some core library routines and demos are pure assembly. Identifying features:
- No compiler prologue pattern
- `MOVEM.L` register lists tend to be maximally specified
- Copper/blitter setup code appears directly
- May use `SECTION` macros instead of implicit hunk ordering

---

## Quick Fingerprint Checklist

```
□ Does function prologue use LINK A5?  → SAS/C
□ Does function prologue use LINK A6?  → GCC with -fno-omit-frame-pointer
□ No LINK at all, just MOVEM.L?        → GCC/VBCC (check other patterns)
□ PC-relative globals (LEA x(PC))?     → GCC -fpic or VBCC
□ Absolute globals + HUNK_RELOC32?     → SAS/C or GCC without -fpic
□ HUNK_SYMBOL has __main, __exit?      → GCC/libnix
□ HUNK_SYMBOL has _c_start, _main?     → SAS/C
```

---

## References

- SAS/C 6.x Programmer's Guide — code generation appendix
- GCC m68k-amigaos port (bebbo): https://github.com/bebbo/amiga-gcc
- VBCC manual: http://www.ibaug.de/vbcc/doc/vbcc.html
- Aztec C 68k manual (archive.org)
