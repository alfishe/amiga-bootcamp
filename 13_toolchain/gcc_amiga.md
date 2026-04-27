[← Home](../README.md) · [Toolchain](README.md)

# m68k-amigaos-gcc — Cross-Compiler

## Overview

`m68k-amigaos-gcc` is the GCC-based cross-compiler for AmigaOS, typically based on GCC 2.95 (legacy) or GCC 6.5 (bebbo's fork). It produces Amiga hunk-format executables and supports all 68k variants. By default, bebbo's toolchain uses [vasm](vasm_vlink.md) as the assembler and [vlink](vasm_vlink.md) as the linker — the compiler emits assembly, vasm assembles it, and vlink produces the final hunk executable.

---

## Installation (bebbo's toolchain)

```bash
# Docker-based (recommended):
docker pull bebbo/amiga-gcc
docker run -v $(pwd):/work bebbo/amiga-gcc m68k-amigaos-gcc -o hello hello.c

# Native build (Linux/macOS):
# NOTE: bebbo removed his repos from GitHub. Use Codeberg or his personal git:
git clone https://codeberg.org/bebbo/amiga-gcc.git
# Mirror: https://franke.ms/git/bebbo/amiga-gcc
cd amiga-gcc
make update
make all -j$(nproc)
# Installs to /opt/amiga/
```

---

## Usage

```bash
# Compile and link:
m68k-amigaos-gcc -noixemul -o hello hello.c

# Common flags:
#   -noixemul       — use libnix (no ixemul.library dependency)
#   -m68000          — target 68000 (default)
#   -m68020          — target 68020+
#   -m68040          — target 68040
#   -m68060          — target 68060
#   -m68881          — use 68881/68882 FPU
#   -Os              — optimize for size
#   -O2              — optimize for speed
#   -fomit-frame-pointer — free up A5
#   -fbaserel        — base-relative addressing (small data model)
#   -resident        — generate resident-capable code
#   -g               — include debug info (HUNK_DEBUG)
#   -s               — strip symbols
```

---

## Startup Code

| Startup | Description |
|---|---|
| `libnix` | Minimal C runtime, no shared library dependency |
| `ixemul` | Unix-like C runtime (requires ixemul.library) |
| `crt0.o` | Raw startup — no C runtime at all |

---

## Inline/Pragma System Calls

```c
/* Use inline headers to call library functions via registers: */
#include <inline/exec.h>
#include <inline/dos.h>

/* Or use proto headers (auto-select inline vs pragma): */
#include <proto/exec.h>
#include <proto/dos.h>
```

---

## Toolchain Integration — vasm & vlink

bebbo's GCC uses **[vasm](vasm_vlink.md)** and **[vlink](vasm_vlink.md)** as its default assembler and linker. The compiler emits assembly (`.s`), vasm assembles it to hunk-format object files, and vlink links the final executable. This is fully configurable — `-Wa,...` passes flags to the assembler, `-Wl,...` passes flags to the linker.

```bash
# Single command — GCC orchestrates assembler and linker internally:
m68k-amigaos-gcc -noixemul -m68020 -O2 -o myapp myapp.c
# Internal pipeline: gcc → .s → vasmm68k_mot → .o → vlink → executable

# Pass assembler-specific flags:
m68k-amigaos-gcc -Wa,-m68060,-devpac -o myapp myapp.c

# Pass linker-specific flags:
m68k-amigaos-gcc -Wl,-Map=myapp.map -o myapp myapp.c
```

---

## References

- [vasm & vlink](vasm_vlink.md) — assembler and linker used by this toolchain
- Codeberg: https://codeberg.org/bebbo/amiga-gcc
- Mirror: https://franke.ms/git/bebbo/amiga-gcc
- GCC 6.5 m68k cross-compiler documentation
