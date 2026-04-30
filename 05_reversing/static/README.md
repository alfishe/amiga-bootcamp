[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Static Analysis & Binary Archaeology

## Contents

### Fundamentals
- [hunk_reconstruction.md](hunk_reconstruction.md) — Understanding the Amiga HUNK structure in disassemblers
- [code_vs_data_disambiguation.md](code_vs_data_disambiguation.md) — Distinguishing instructions from data blocks
- [m68k_codegen_patterns.md](m68k_codegen_patterns.md) — Common 68k assembly sequences and optimizations

### API & Data Analysis
- [library_jmp_table.md](library_jmp_table.md) — Reconstructing library jump tables and LVOS
- [api_call_identification.md](api_call_identification.md) — Identifying system calls in naked disassembly
- [string_xref_analysis.md](string_xref_analysis.md) — Using strings to anchor functional analysis
- [struct_recovery.md](struct_recovery.md) — Identifying AmigaOS structures in memory

### Language-Specific RE
- [asm68k_binaries.md](asm68k_binaries.md) — Hand-written 68k assembly (Demos, Bootblocks)
- [ansi_c_reversing.md](ansi_c_reversing.md) — Recovering C code logic
- [cpp_vtables_reversing.md](cpp_vtables_reversing.md) — C++ Objects and VTables
- [other_languages.md](other_languages.md) — AMOS, Blitz Basic, Amiga E, and more
