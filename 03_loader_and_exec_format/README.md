[← Home](../README.md)

# Executable Loader & HUNK Format

## Overview

This section covers the complete lifecycle of an AmigaOS executable:

1. **HUNK file format** — the binary container for all AmigaOS executables, libraries, and object files
2. **Loader pipeline** — how `dos.library` loads and relocates an executable into memory
3. **Object files** — how compilers produce relocatable object files for the linker
4. **Overlays** — how programs larger than available memory use the overlay system

## Contents

| File | Topic |
|---|---|
| [hunk_format.md](hunk_format.md) | Complete HUNK binary specification — all 22 hunk type codes with wire format, memory flags, advisory bits |
| [hunk_ext_deep_dive.md](hunk_ext_deep_dive.md) | HUNK_EXT: exports (EXT_DEF), imports (EXT_REF32), commons, linker resolution |
| [hunk_relocation.md](hunk_relocation.md) | Relocation mechanics: visual before/after, patching algorithm, RELOC32/SHORT/DREL32, PC-relative impact |
| [hunk_debug_info.md](hunk_debug_info.md) | HUNK_SYMBOL and HUNK_DEBUG: stabs format (SAS/C, GCC), debugger consumption, stripping |
| [exe_load_pipeline.md](exe_load_pipeline.md) | LoadSeg → AllocMem → relocation → segment chain → CreateProc → entry point |
| [object_file_format.md](object_file_format.md) | Compiler object files (HUNK_UNIT), multi-section layout, HUNK_LIB archives, linker operation |
| [overlay_system.md](overlay_system.md) | HUNK_OVERLAY: tree architecture, runtime overlay manager, worked binary example, modern alternatives |
| [**exe_crunchers.md**](exe_crunchers.md) | **Executable packers: PowerPacker/Imploder/Shrinkler, decrunch stubs, compression algorithms, detection** |

## Why HUNK?

HUNK is the native AmigaOS executable format, used from AmigaOS 1.0 through 3.x. It predates ELF/COFF and has these key properties:

- **Segmented**: separate code, data, and BSS hunks with independent memory allocation
- **Relocatable**: all absolute references are patched at load time (no ASLR; base address changes each run)
- **Typed memory**: each hunk can request `CHIP` or `FAST` memory independently
- **Symbol-complete**: optional HUNK_SYMBOL and HUNK_DEBUG hunks carry debugging information

## Key Concepts

| Term | Meaning |
|---|---|
| **Hunk** | One contiguous block in the binary (code, data, BSS, etc.) |
| **Segment** | A loaded hunk at runtime — a `BPTR`-linked list |
| **Segment list** | Chain of loaded hunks returned by `LoadSeg()` |
| **BPTR** | Amiga byte pointer — 32-bit value right-shifted by 2 (`ptr >> 2`) |
| **Relocation** | Patching absolute addresses based on actual load address |
| **LVO** | Library Vector Offset — negative offset from library base |

## References

- ADCD 2.1: `Includes_and_Autodocs_3._guide/` — dos.library LoadSeg autodoc
- NDK39: `dos/dos.h` — BPTR, segment handling macros
- *Amiga ROM Kernel Reference Manual: Libraries* — AmigaDOS chapter
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node0150.html
