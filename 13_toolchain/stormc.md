[← Home](../README.md) · [Toolchain](README.md)

# StormC — Native IDE and Compiler Suite

## Overview

**StormC** was a native Amiga integrated development environment (IDE) developed by **Haage & Partner**. Unlike SAS/C (command-line focused) or GCC (cross-compilation), StormC provided a modern GUI-based IDE running directly on the Amiga with project management, integrated editor, debugger, and compiler — similar to what Borland C++ and Visual Studio offered on PC.

---

## Version History

| Version | Year | Key Features |
|---|---|---|
| StormC 1.0 | 1996 | Initial release, C compiler, basic IDE |
| StormC 2.0 | 1997 | C++ support, improved optimiser |
| StormC 3.0 | 1998 | Full C++ with exceptions, STL, PowerPC support |
| StormC 4.0 | 1999 | Final version, OS 3.5 integration |

---

## Key Features

| Feature | Description |
|---|---|
| **Native IDE** | GUI editor + project manager running on AmigaOS itself |
| **C and C++** | Full C89/C90, C++ with exceptions and RTTI |
| **PowerPC** | StormC 3+ could target PPC (for CyberStorm PPC, BlizzardPPC) |
| **68k code gen** | 68000 through 68060 target support |
| **Debugger** | Integrated source-level debugger with breakpoints and watch |
| **Linker** | StormLink — Amiga hunk format output |
| **Profiler** | Built-in function-level profiler |
| **AmigaOS integration** | Full NDK headers, pragma support, Amiga library call stubs |
| **MUI support** | Built-in MUI class creation wizards (later versions) |

---

## Project Structure

StormC used `.storm` project files (proprietary format) containing:
- Source file list and compilation order
- Compiler flags per file or project-wide
- Include paths and library search paths
- Debug/Release build configurations
- Target CPU selection

---

## Compilation

```
; From the IDE:
; Project → Build (or press Ctrl+B)

; Command-line compiler also available:
stormc -O2 -m68020 -o myapp main.c util.c

; Typical flags:
;   -m68000      Target 68000
;   -m68020      Target 68020+
;   -m68040      Target 68040
;   -m68060      Target 68060
;   -O0 to -O3   Optimisation level
;   -g           Debug info
;   -c           Compile only (no link)
;   -I<path>     Include path
;   -L<path>     Library path
;   -l<lib>      Link library
```

---

## StormC vs. Other Amiga Compilers

| Feature | SAS/C 6.58 | GCC (bebbo) | StormC 4.0 |
|---|---|---|---|
| **C++ support** | No (C only) | Yes (GCC 6.5) | Yes (with exceptions) |
| **IDE** | No (CLI + editor) | No (CLI + any editor) | **Yes (native GUI)** |
| **Debugger** | External (CodeProbe) | GDB remote | **Integrated** |
| **Cross-compile** | No (native only) | **Yes (Linux/macOS host)** | No (native only) |
| **Optimiser quality** | Excellent | Good | Good |
| **PowerPC** | No | No | Yes (v3+) |
| **Availability** | Abandonware | Free / open source | Abandonware |
| **Legacy code compat** | High (dominant compiler) | Moderate (GCC differences) | Moderate |
| **Pragma support** | Native `#pragma libcall` | Inline asm stubs | Pragma compatible |

---

## Limitations and Legacy

- **Proprietary project format**: `.storm` files can't be converted to Makefiles easily
- **No cross-compilation**: Must run on a real Amiga or emulator
- **C++ ABI**: StormC's C++ name mangling and vtable layout differ from GCC — libraries compiled with StormC can't be linked with GCC C++ code
- **Abandoned**: Haage & Partner ceased operations; no source release
- **PowerPC path abandoned**: The WarpOS/PowerUP split made PPC support fragmented

Despite these issues, StormC was the most productive **native** Amiga development environment, and many late-era Amiga applications (1996–2000) were developed with it.

---

## References

- Haage & Partner: historical website (archived)
- Aminet: `dev/c/StormC` — various StormC patches and updates
- See also: [sasc.md](sasc.md) — SAS/C (dominant legacy compiler)
- See also: [gcc_amiga.md](gcc_amiga.md) — GCC cross-compiler (modern standard)
