[← Home](../README.md) · [Loader & HUNK Format](README.md)

# HUNK Relocation Mechanics

## Overview

Relocation is the process of **patching absolute addresses** in a loaded executable to reflect its actual memory location. Since AmigaOS allocates memory dynamically, a program cannot know its load address at compile time — all inter-hunk references must be fixed up at runtime.

---

## Why Relocation Is Necessary

An Amiga executable contains references like:
```asm
LEA  DataTable(PC), A0   ; PC-relative — no relocation needed
MOVE.L #DataTable, A0    ; Absolute — MUST be relocated
```

The linker places `DataTable` at some hunk-relative offset (e.g., offset 0 in the data hunk). The absolute address is only known at load time. The relocation table tells the loader which longwords in the code contain these absolute values.

---

## HUNK_RELOC32 Format

```
HUNK_RELOC32 ($000003EC)

[Repeat until terminator:]
  <num_offsets>       Number of longword addresses to patch for this target hunk
  <target_hunk>       Index of the hunk whose base address is added
  <offset_0>          Byte offset within the current hunk to patch
  <offset_1>
  ...

<0>                   num_offsets = 0 terminates the reloc list
HUNK_END ($000003F2)
```

### Patching Algorithm

For each entry in HUNK_RELOC32 of hunk `H`:
```
foreach (target_hunk, offsets[]):
    base = segment_base_address[target_hunk]
    foreach offset in offsets:
        *(ULONG *)(H_base + offset) += base
```

The value at `H_base + offset` already contains the **hunk-relative** address written by the linker. Adding the actual base produces the final absolute address.

### Example

Code hunk references data hunk at two sites:
```
Before load (raw file values):
  code[0x18] = $00000000   ; linker placed "data offset 0" here
  code[0x2C] = $00000010   ; linker placed "data offset 0x10" here

HUNK_RELOC32:
  num_offsets = 2
  target_hunk = 1           ; data hunk
  offsets = [0x18, 0x2C]

After load (data hunk loaded at $20000):
  code[0x18] = $00000000 + $20000 = $00020000
  code[0x2C] = $00000010 + $20000 = $00020010
```

---

## HUNK_RELOC16 and HUNK_RELOC8

Same format as HUNK_RELOC32 but patch **16-bit** or **8-bit** values:
- `HUNK_RELOC16` ($3ED): patches UWORD at offset
- `HUNK_RELOC8` ($3EE): patches UBYTE at offset

These are rare in practice — the 68000 requires even-aligned word accesses and only supports 16-bit displacement in most addressing modes.

---

## HUNK_DREL32 — Short Relocation (32-bit)

`HUNK_DREL32` ($3F7) is an alternative relocation format used by some linkers (e.g., BLink) for smaller reloc tables:

```
HUNK_DREL32

[Repeat:]
  <num_offsets>  (WORD, not LONGWORD)
  <target_hunk>  (WORD)
  <offset_0>     (WORD)
  ...

<0>              terminator
```

By using 16-bit values, this format is more compact for programs with many relocations and small hunk sizes (<64 KB). AmigaOS `InternalLoadSeg` supports both formats.

---

## PC-Relative References (No Relocation Needed)

The 68020+ supports **PC-relative addressing** with 32-bit displacements:
```asm
LEA  symbol(PC), A0    ; PC-relative load effective address
MOVE.L  data(PC), D0   ; PC-relative data read
```

PC-relative references do not require relocation — the offset is relative to the instruction, so it is valid regardless of where the code is loaded. **GCC for 68k** generates PC-relative code by default (`-fpic`), significantly reducing the size of relocation tables.

SAS/C generates absolute references by default and relies heavily on `HUNK_RELOC32`.

---

## Relocation at Runtime — Segment Chain

The loader tracks loaded segments as a **BPTR chain** (singly-linked list). The segment list head is returned by `LoadSeg()`:

```
Segment 0 (code):
  BPTR → Segment 1
  [code data]

Segment 1 (data):
  BPTR → 0 (NULL)
  [data]
```

Each segment begins with a 4-byte BPTR to the next segment. Hunk index `n` corresponds to segment `n` in this chain.

---

## Viewing Relocations with Tools

### IDA Pro
After loading a HUNK file with the Amiga plugin, IDA resolves relocations automatically. The fixup table is visible in `View → Open Subviews → Fixups`.

### hexdump + manual

Locate HUNK_RELOC32 ($3EC) in raw hex:
```bash
xxd mybinary | grep "0003 ec"
```

Then read num_offsets and target_hunk longwords that follow.

### hunkinfo (custom tool)

```bash
hunkinfo mybinary    # shows all hunks, sizes, reloc counts
```

---

## References

- NDK39: `dos/doshunks.h`
- *Amiga ROM Kernel Reference Manual: Libraries* — AmigaDOS chapter, `InternalLoadSeg`
- vlink linker documentation — relocation section
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node01E0.html
