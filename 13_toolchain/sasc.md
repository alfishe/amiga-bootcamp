[← Home](../README.md) · [Toolchain](README.md)

# SAS/C 6.x — Compiler Reference

## Overview

SAS/C (originally Lattice C) was the dominant commercial C compiler for AmigaOS. Version 6.58 is the final release. It produces optimised 68k code with full AmigaOS integration, including pragma-based system calls and SAS-specific debug formats.

---

## Key Features

| Feature | Description |
|---|---|
| Register args | Automatic register parameter passing |
| Pragmas | `#pragma libcall` for direct library LVO calls |
| Small data | A4-relative addressing for globals |
| Profiling | Built-in `sprof` profiler |
| Debug format | SAS stabs (`=APS` tag in HUNK_DEBUG) |
| Optimizer | Global optimizer (`lc -O`) with peephole |

---

## Pragma Format

```c
/* dos_pragmas.h — generated from FD files: */
#pragma libcall DOSBase Open 1e 2102
/*                       ^^   ^^ ^^^^
                         name LVO reg-encoding
   reg-encoding: 2=D2, 1=D1, 0=result in D0, 2 args */

#pragma libcall DOSBase Close 24 101
#pragma libcall DOSBase Read 2a 32103
```

Register encoding: digits map to registers (1=D0, 2=D1, ... 9=A0, A=A1, etc.)

---

## Compilation

```
lc -v -O -b0 -j73 hello.c     ; compile
blink hello.o TO hello LIB lib:sc.lib lib:amiga.lib  ; link
```

| Flag | Meaning |
|---|---|
| `-v` | Verbose |
| `-O` | Optimise |
| `-b0` | Small data model (A4-relative) |
| `-b1` | Large data model |
| `-j73` | Generate 68020/68881 code |
| `-d0` | No debug info |
| `-d2` | Full debug info |

---

## References

- SAS/C 6.x User Manual
- NDK39 pragma files: `NDK_3.9/Include/pragmas/`
