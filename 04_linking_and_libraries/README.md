[← Home](../README.md)

# Linking & Library Integration

## Overview

This section documents how AmigaOS shared libraries work at the binary level — how compilers produce library call stubs, how the linker wires them up, and how to reconstruct this mechanism during reverse engineering.

## Contents

| File | Topic |
|---|---|
| [library_structure.md](library_structure.md) | Library memory layout, JMP table encoding, MakeLibrary construction, complete library creation example |
| [shared_libraries_runtime.md](shared_libraries_runtime.md) | OpenLibrary resolution path, ramlib disk loader, version negotiation, expunge mechanics |
| [register_conventions.md](register_conventions.md) | Register ABI: integer, FPU, varargs/TagItem, small-data model, __saveds, inter-library calls |
| [fd_files.md](fd_files.md) | Function Definition files — the library ABI source of truth, LVO calculation |
| [lvo_table.md](lvo_table.md) | JMP table layout, complete exec.library LVO table, IDA reconstruction script |
| [compiler_stubs.md](compiler_stubs.md) | How SAS/C, GCC, VBCC call libraries — compiler signature identification |
| [inline_stubs.md](inline_stubs.md) | Compiler inline stubs: pragma (SAS/C), inline asm (GCC), __reg (VBCC), stub generation tools |
| [link_libraries.md](link_libraries.md) | Static linking: amiga.lib, sc.lib, libnix, auto.lib, WBStartup glue, stack cookie |
| [startup_code.md](startup_code.md) | c.o / gcrt0.S: entry contract, CLI vs WB detection, argument parsing, WBStartup message |
| [setfunction.md](setfunction.md) | Runtime function patching: canonical pattern, chaining, removal, RE detection heuristics |

## The Library ABI Model

Every AmigaOS shared library exposes its functions through a **negative-offset JMP table** relative to the library base pointer:

```
Library base:  LIB+0    → Library node (struct Library)
               LIB-6    → JMP _Open        (mandatory)
               LIB-12   → JMP _Close       (mandatory)
               LIB-18   → JMP _Expunge     (mandatory)
               LIB-24   → JMP _Reserved    (mandatory)
               LIB-30   → JMP _func1       (first user function)
               LIB-36   → JMP _func2
               ...
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
