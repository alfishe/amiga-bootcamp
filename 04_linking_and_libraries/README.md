[← Home](../README.md)

# Linking & Library Integration

## Overview

This section documents how AmigaOS shared libraries work at the binary level — how compilers produce library call stubs, how the linker wires them up, and how to reconstruct this mechanism during reverse engineering.

## Contents

| File | Topic |
|---|---|
| [library_structure.md](library_structure.md) | Library node, LVO table, OpenLibrary mechanics |
| [fd_files.md](fd_files.md) | Function Definition files — the library ABI source |
| [lvo_table.md](lvo_table.md) | JMP table layout and reconstruction |
| [compiler_stubs.md](compiler_stubs.md) | How SAS/C, GCC, VBCC call libraries |
| [setfunction.md](setfunction.md) | Runtime function patching with SetFunction |
| [startup_code.md](startup_code.md) | c.o / gcrt0.S — startup and exit sequences |

## The Library ABI Model

Every AmigaOS shared library exposes its functions through a **negative-offset JMP table** relative to the library base pointer:

```
Library base:  LIB+0    → Library node (struct Library)
               LIB-6    → JMP _funcN   (last function)
               LIB-12   → JMP _funcN-1
               ...
               LIB-6    → JMP _func1   (first user function)
```

A C call like `OpenLibrary("graphics.library", 0)` compiles to:
```asm
MOVE.L  4.W, A6          ; A6 = SysBase (exec)
JSR     -552(A6)          ; LVO for OpenLibrary = -552
```

The negative offset (`-552`) is the **Library Vector Offset (LVO)** — a fixed ABI value defined in the library's `.fd` file and `proto/` include.

## References

- NDK39: `fd/` directory, `proto/` includes, `inline/` inline stubs
- ADCD 2.1: Library writing guide, ROM Kernel Manual
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node0000.html
