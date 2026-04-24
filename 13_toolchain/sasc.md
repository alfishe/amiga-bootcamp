[← Home](../README.md) · [Toolchain](README.md)

# SAS/C 6.x — Compiler Reference

## Overview

SAS/C (originally Lattice C) was the dominant commercial C compiler for AmigaOS from the mid-1980s through the mid-1990s. Version **6.58** is the final release. It produces highly optimised 68k code with deep AmigaOS integration, including pragma-based system calls, SAS-specific debug formats, and a built-in profiler.

Most existing Amiga source code and documentation assumes SAS/C conventions. Understanding its idioms is essential for working with legacy codebases.

---

## Key Features

| Feature | Description |
|---|---|
| **Register args** | Automatic register parameter passing for small functions |
| **Pragmas** | `#pragma libcall` for direct library LVO calls — no stub library needed |
| **Small data model** | A4-relative addressing for global variables (faster, smaller code) |
| **Large data model** | Absolute addressing for globals (no 64 KB limit) |
| **Profiler** | Built-in `sprof` function-level profiler |
| **Debug format** | SAS stabs (`=APS` tag in `HUNK_DEBUG`) |
| **Global optimizer** | `lc -O` with peephole, dead code elimination, CSE |
| **Code generation** | 68000 through 68060 + 68881/68882 FPU |
| **Integrated linker** | `blink` — faster than generic linkers, understands Amiga hunks |

---

## Pragma Format

Pragmas tell the compiler how to call AmigaOS library functions directly via JSR through the library base, with arguments in specific registers:

```c
/* dos_pragmas.h — generated from FD files: */
#pragma libcall DOSBase Open 1e 2102
/*                            ^^  ^^^^
                              LVO  register encoding

   LVO $1E = -30 (decimal) = offset in jump table
   Register encoding: read RIGHT to LEFT:
     2 = D2 (not used here)
     0 = D0 (return value)
     1 = D1 (first arg)
     2 = D2 (second arg)
   Last digit = number of arguments */

#pragma libcall DOSBase Close 24 101
/* LVO -$24 (-36), 1 arg in D1, returns in D0 */

#pragma libcall DOSBase Read 2a 32103
/* LVO -$2A (-42), 3 args: D1=fh, D2=buffer, D3=length */
```

### Register Encoding

| Digit | Register | Digit | Register |
|---|---|---|---|
| 0 | D0 | 8 | (unused) |
| 1 | D1 | 9 | A0 |
| 2 | D2 | A | A1 |
| 3 | D3 | B | A2 |
| 4 | D4 | C | A3 |
| 5 | D5 | D | A4 |
| 6 | D6 | E | A5 |
| 7 | D7 | F | (unused) |

The rightmost digit is always the result register, next digit is number of args, then args are listed left-to-right.

---

## Compilation Workflow

```
Source (.c) → lc (compile) → Object (.o) → blink (link) → Executable
```

```bash
# Compile a single file:
lc -v -O -b0 main.c

# Link:
blink main.o util.o TO myapp LIB lib:sc.lib lib:amiga.lib

# Compile + link in one step:
lc -v -O -b0 -j73 main.c util.c LINK TO myapp
```

### Compiler Flags

| Flag | Meaning |
|---|---|
| `-v` | Verbose output |
| `-O` | Enable global optimiser |
| `-b0` | Small data model (A4-relative, max 64 KB globals) |
| `-b1` | Large data model (absolute addressing) |
| `-j30` | Generate 68030 code |
| `-j40` | Generate 68040 code |
| `-j73` | Generate 68020 + 68881 FPU code |
| `-d0` | No debug info |
| `-d2` | Full debug info (SAS stabs) |
| `-r` | Generate resident/reentrant code |
| `-L` | Disable auto-open of amiga.lib |
| `-w` | Suppress warnings |
| `-E` | Preprocess only |

### Linker Flags (blink)

| Flag | Meaning |
|---|---|
| `TO name` | Output file name |
| `LIB libs` | Link libraries |
| `DEBUG` | Include debug hunks |
| `STRIPDEBUG` | Remove debug hunks |
| `SMALLCODE` | PC-relative addressing |
| `SMALLDATA` | A4-relative data |
| `MAP file` | Generate link map |
| `NODEBUG` | Omit all debug info |

---

## SAS/C-Specific Idioms

```c
/* Register parameters: */
ULONG __asm MyFunc(register __d0 ULONG arg1,
                   register __a0 APTR arg2);

/* Interrupt-safe function: */
void __interrupt __saveds MyInterrupt(void);

/* Resident code: */
LONG __saveds __asm LibOpen(register __a6 struct Library *base);

/* __saveds: saves/restores A4 (small data base) on entry/exit */
/* __interrupt: preserves all registers */
/* __asm: use register calling convention */
```

### Differences from GCC

| Feature | SAS/C | GCC (m68k-amigaos) |
|---|---|---|
| Register args | `register __d0 ULONG x` | `ULONG x __asm("d0")` |
| Small data base | A4 (automatic with `-b0`) | `-fbaserel` (A4) |
| Library pragmas | `#pragma libcall` | Inline asm stubs in `<inline/lib.h>` |
| Startup | `cres.o` (resident) / `c.o` (standard) | `libnix` or `ixemul` |
| String constants | Pooled by default | `-fmerge-constants` |

---

## References

- SAS/C 6.x User Manual and Reference Manual
- NDK39 pragma files: `NDK_3.9/Include/pragmas/`
- See also: [pragmas.md](pragmas.md) — pragma/inline mechanism in depth
- See also: [gcc_amiga.md](gcc_amiga.md) — GCC cross-compiler (modern alternative)
