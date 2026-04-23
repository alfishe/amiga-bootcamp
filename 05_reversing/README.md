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
| [compiler_fingerprints.md](compiler_fingerprints.md) | Compiler identification by code patterns |
| [library_reconstruction.md](library_reconstruction.md) | Reconstructing unknown library JMP tables |
| [patching_techniques.md](patching_techniques.md) | Surgical binary patching methods |
| [case_studies/](case_studies/) | Real-world RE walkthroughs |
| [case_studies/ramdrive_device.md](case_studies/ramdrive_device.md) | ramdrive.device RE walkthrough |

## Core Principles

1. **Know the ABI first** — All library calls are `JSR LVO(A6)`. Before reversing any function, identify which library A6 holds using the `lib_Node.ln_Name` string at `base+$00`.
2. **Use .fd files** — The NDK39 `.fd` files give you every function name and parameter mapping for free.
3. **Relocations are your friend** — HUNK_RELOC32 entries tell you exactly which longwords are inter-hunk references, making it easy to distinguish code from data.
4. **Compiler signatures reduce work** — SAS/C vs GCC produces distinct prologues. Identifying the compiler narrows the pattern space dramatically.

## Tool Setup

| Tool | Purpose |
|---|---|
| IDA Pro 7.x | Primary disassembler and decompiler (Hex-Rays) |
| IDA Amiga plugin | HUNK loader, HUNK_SYMBOL import |
| `hunkinfo` | Quick hunk/symbol/reloc dump |
| Ghidra + AmigaOS plugin | Free alternative to IDA |
| wack / MonAm | On-device debugger |

## References

- NDK39: `fd/`, `include/`
- ADCD 2.1: complete library autodocs
- *Amiga ROM Kernel Reference Manual: Libraries* and *Devices*
