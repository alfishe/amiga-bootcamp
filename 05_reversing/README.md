[← Home](../README.md)

# Reverse Engineering AmigaOS Binaries

## Overview

This section provides a systematic methodology for reverse engineering AmigaOS executables and shared libraries using IDA Pro (or Ghidra with the Amiga plugin), with focus on:

- Reconstructing the library JMP table
- Identifying compiler-specific code patterns
- Understanding the exec/dos calling convention at the assembly level
- Tracing library patches (SetFunction)
- Case studies from real Amiga software

## Contents

| File | Topic |
|---|---|
| [methodology.md](methodology.md) | Step-by-step RE workflow for Amiga HUNK binaries |
| [ida_setup.md](ida_setup.md) | IDA Pro configuration for 68k/Amiga analysis |
| [ghidra_setup.md](ghidra_setup.md) | Ghidra configuration for 68k/Amiga analysis & decompilation |
| [compiler_fingerprints.md](compiler_fingerprints.md) | Compiler identification by code patterns |
| [library_reconstruction.md](library_reconstruction.md) | Reconstructing unknown library JMP tables |
| [static/code_vs_data_disambiguation.md](static/code_vs_data_disambiguation.md) | Distinguishing code bytes from data — IDA/Ghidra workflows |
| [patching_techniques.md](patching_techniques.md) | Surgical binary patching methods |
| [unpacking_and_decrunching.md](unpacking_and_decrunching.md) | Executable unpacking, decruncher architecture, and manual extraction |
| [custom_loaders_and_drm.md](custom_loaders_and_drm.md) | Bypassing DOS, Trackloaders, and physical DRM tricks |
| [anti_debugging.md](anti_debugging.md) | The Cracker vs. Developer arms race: Trace vector abuse, NMI defeat, CIA timers |
| [whdload_architecture.md](whdload_architecture.md) | WHDLoad internals, slaves, resload_DiskLoad, and runtime memory patching |
| [case_studies/](case_studies/) | Real-world RE walkthroughs |
| [case_studies/ramdrive_device.md](case_studies/ramdrive_device.md) | ramdrive.device RE walkthrough |

### Game Reverse Engineering

| File | Topic |
|---|---|
| [games/game_reversing.md](games/game_reversing.md) | Game RE: disassembly, modification, asset extraction, save game analysis |

### Per-Compiler Reverse Engineering — Binary Field Manuals

| File | Topic |
|---|---|
| [static/compilers/README.md](static/compilers/README.md) | Compiler identification flowchart and comparison matrix |
| [static/compilers/sasc.md](static/compilers/sasc.md) | **SAS/C 5.x/6.x** — LINK A5 + 9-reg save, absolute strings, `_LibBase` globals |
| [static/compilers/gcc.md](static/compilers/gcc.md) | **GCC 2.95.x** — `.text` hunk, A6 frame pointer, PC-relative strings, `__CTOR_LIST__` |
| [static/compilers/vbcc.md](static/compilers/vbcc.md) | **VBCC** — No frame pointer, per-function saves, `__reg()`, `__MERGED` hunks |
| [static/compilers/stormc.md](static/compilers/stormc.md) | **StormC / StormC++** — SAS/C-compatible C, unique C++ ABI, PPC support |
| [static/compilers/aztec_c.md](static/compilers/aztec_c.md) | **Manx Aztec C** — D3-D7 save only (5 regs), D2 scratch, pre-1990 era |
| [static/compilers/lattice_c.md](static/compilers/lattice_c.md) | **Lattice C 3.x/4.x** — SAS/C predecessor, simpler optimizer, 6-reg save |
| [static/compilers/dice_c.md](static/compilers/dice_c.md) | **DICE C** — No frame pointer, `_mainCRTStartup`, fast compile speed |

### Language-Specific Reverse Engineering

| File | Topic |
|---|---|
| [static/asm68k_binaries.md](static/asm68k_binaries.md) | Hand-written assembly reverse engineering — demos, games, bootblocks |
| [static/ansi_c_reversing.md](static/ansi_c_reversing.md) | ANSI C reverse engineering — struct recovery, control flow, library anchoring |
| [static/cpp_vtables_reversing.md](static/cpp_vtables_reversing.md) | C++ OOP reverse engineering — vtables, inheritance, RTTI, name mangling |
| [static/other_languages.md](static/other_languages.md) | Non-C languages — AMOS, Blitz Basic, Amiga E, Modula-2, FORTH, ARexx |

## Core Principles

1. **Know the ABI first** — All library calls are `JSR LVO(A6)`. Before reversing any function, identify which library A6 holds using the `lib_Node.ln_Name` string at `base+$00`.
2. **Use .fd files** — The NDK39 `.fd` files give you every function name and parameter mapping for free.
3. **Relocations are your friend** — HUNK_RELOC32 entries tell you exactly which longwords are inter-hunk references, making it easy to distinguish code from data.
4. **Compiler signatures reduce work** — SAS/C vs GCC produces distinct prologues. Identifying the compiler narrows the pattern space dramatically.

## Tool Setup

| Tool | Purpose |
|---|---|
| IDA Pro 7.x | Primary static disassembler (no native M68k decompilation) |
| IDA Amiga plugin | HUNK loader, HUNK_SYMBOL import |
| Ghidra + ghidra-amiga | Powerful disassembler and C-pseudocode decompiler for M68k |
| `hunkinfo` | Quick hunk/symbol/reloc dump |
| wack / MonAm | On-device debugger |

## References

- NDK39: `fd/`, `include/`
- ADCD 2.1: complete library autodocs
- *Amiga ROM Kernel Reference Manual: Libraries* and *Devices*
