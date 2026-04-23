[← Home](../README.md) · [Loader & HUNK Format](README.md)

# HUNK_EXT — Exports and Imports

## Overview

`HUNK_EXT` ($000003EF) is the external symbol record used in **object files** (HUNK_UNIT format). It carries both **exported symbols** (definitions visible to the linker) and **imported symbols** (references to symbols defined in other object files or libraries).

`HUNK_EXT` does **not** appear in final executables — the linker resolves all externals during the link step and emits `HUNK_RELOC32` instead.

---

## Record Format

```
HUNK_EXT ($000003EF)

[Repeat until terminator:]
  <type_and_namelen>    Longword: bits[31:24] = EXT type, bits[23:0] = name length in longs
  <name...>             Symbol name, padded to longword boundary
  [type-specific data]

<0x00000000>            Terminator (name length = 0)
HUNK_END
```

---

## EXT Type Codes

| Value | Name | Direction | Description |
|---|---|---|---|
| 0 | `EXT_SYMB` | export | Absolute symbol (no relocation) |
| 1 | `EXT_DEF` | export | Defined symbol at offset in current hunk |
| 2 | `EXT_ABS` | export | Absolute value symbol |
| 3 | `EXT_RES` | export | Resident library symbol |
| 129 | `EXT_REF32` | import | 32-bit reference (absolute) |
| 130 | `EXT_COMMON` | import/def | Common BSS block |
| 131 | `EXT_REF16` | import | 16-bit reference |
| 132 | `EXT_REF8` | import | 8-bit reference |
| 133 | `EXT_DEXT32` | import | 32-bit data-relative reference |
| 134 | `EXT_DEXT16` | import | 16-bit data-relative reference |
| 135 | `EXT_DEXT8` | import | 8-bit data-relative reference |

---

## Export Records

### EXT_DEF — Defined Symbol

The most common export — a function or data label at a fixed offset within the current hunk:

```
bits[31:24] = 0x01        EXT_DEF
bits[23:0]  = name_longs  name length in longwords
<name...>                 symbol name (padded)
<offset>                  offset within current hunk (longword)
```

Example: exporting `_init` at offset 0x10 in the code hunk:
```
$01000005   ; EXT_DEF, name = 5 longs (20 chars)
"_ini"
"t   "
"    "      ; (padded to 5 longs)
$00000010   ; offset $10
```

### EXT_ABS — Absolute Symbol

Symbol has an absolute value (not relative to any hunk):
```
bits[31:24] = 0x02
<name...>
<absolute_value>
```

---

## Import Records

### EXT_REF32 — 32-bit Reference

Used when the current object references an external symbol. The linker patches these after symbol resolution.

```
bits[31:24] = 0x81        EXT_REF32
bits[23:0]  = name_longs
<name...>                 symbol name being referenced
<num_refs>                number of reference sites in current hunk
<ref_offset_0>            byte offset within current hunk
<ref_offset_1>
...
```

Example: `_start` calls `_DOSBase` (external):
```
$81000004   ; EXT_REF32, name = 4 longs
"_DOS"
"Base"
$00000003   ; 3 reference sites
$0000001C   ; offset $1C
$00000034   ; offset $34
$00000048   ; offset $48
```

### EXT_COMMON — Common Block (BSS)

Uninitialized data shared across multiple object files (like C `extern int x;`). The linker allocates one block, all references point to it:

```
bits[31:24] = 0x82        EXT_COMMON
<name...>
<size>                    size in bytes (the common block size)
<num_refs>                reference sites
<offsets...>
```

---

## Worked Binary Example

Object file exporting `_foo` (at offset 0) and importing `_puts`:

```
Offset  Hex                         Meaning
$00:    00 00 03 E7                 HUNK_UNIT
$04:    00 00 00 01                 name length = 1 long
$08:    "foo\0"                     unit name = "foo"
$0C:    00 00 03 E9                 HUNK_CODE
$10:    00 00 00 08                 8 longwords = 32 bytes of code
$14:    [32 bytes of code...]
$34:    00 00 03 EF                 HUNK_EXT
$38:    01 00 00 01                 EXT_DEF, name = 1 long
$3C:    "_foo"                      symbol name "_foo"
$40:    00 00 00 00                 at offset 0 in code hunk
$44:    81 00 00 01                 EXT_REF32, name = 1 long
$48:    "_put"  (truncated)
$4C:    "s\0\0\0"
$50:    00 00 00 01                 1 reference
$54:    00 00 00 08                 at offset $08 in code
$58:    00 00 00 00                 HUNK_EXT terminator
$5C:    00 00 03 F2                 HUNK_END
```

---

## Linker Resolution

When the linker processes multiple object files:

1. Build a **global symbol table** from all `EXT_DEF` records
2. For each `EXT_REF32`, find the defining object and record the target hunk + offset
3. Emit `HUNK_RELOC32` in the output executable to patch the reference sites at load time
4. `EXT_COMMON` blocks are allocated once; all references redirected to that allocation

---

## References

- NDK39: `dos/doshunks.h` — EXT_ type constants
- vlink documentation: http://sun.hasenbraten.de/vlink/release/vlink.pdf
- ADE (Amiga Developer Environment) linker source code
- SAS/C 6.x reference manual — object file format appendix
