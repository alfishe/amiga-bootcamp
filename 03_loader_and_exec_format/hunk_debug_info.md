[← Home](../README.md) · [Loader & HUNK Format](README.md)

# HUNK Debug Information

## Overview

Two optional hunk types carry debug information in AmigaOS executables:

- **HUNK_SYMBOL** ($3F0) — a simple name→offset symbol table
- **HUNK_DEBUG** ($3F1) — arbitrary debug data (most commonly stabs records)

Both are ignored by the loader and only used by debuggers.

---

## HUNK_SYMBOL

The simplest debug hunk. Contains a list of (name, offset) pairs for the current hunk:

```
HUNK_SYMBOL ($000003F0)

[Repeat:]
  <name_len>      Length of name in longwords (0 terminates)
  <name...>       Symbol name padded to longword boundary
  <value>         Symbol value (offset within current hunk)

<0>               Terminator: name_len = 0
HUNK_END
```

### Example

Two symbols in a code hunk:
```
$000003F0           HUNK_SYMBOL
$00000001           name = 1 long (4 chars)
"_foo"              symbol name
$00000000           at offset 0
$00000002           name = 2 longs (8 chars)
"_bar\0\0\0\0"
$00000040           at offset $40
$00000000           terminator
```

### Use in Debuggers

MonAm, wack, and IDA Pro all parse `HUNK_SYMBOL` to provide named labels in the disassembly. IDA's Amiga loader maps these directly to function/data names.

---

## HUNK_DEBUG

`HUNK_DEBUG` carries arbitrary debug data. The most common format used by AmigaOS compilers is **stabs** records (as produced by SAS/C 6.x and GCC).

```
HUNK_DEBUG ($000003F1)

<size_in_longs>     Total size of the debug data in longwords
<data...>           Compiler-specific debug data
HUNK_END
```

### SAS/C Stabs Format

SAS/C 6.x emits stabs-format debug info. The first longword in the debug data is a tag identifying the format:

```
$3D415053   Tag = "=APS" — SAS/C stabs
```

Following the tag: standard BSD/UNIX stabs records:
```c
struct stab_entry {
    ULONG  n_strx;   /* offset into string table */
    UBYTE  n_type;   /* stab type code */
    UBYTE  n_other;
    UWORD  n_desc;   /* line number or misc */
    ULONG  n_value;  /* symbol value */
};
```

**Common stab type codes:**
| Code | Name | Meaning |
|---|---|---|
| $24 | `N_FUN` | Function start |
| $44 | `N_SLINE` | Source line number |
| $64 | `N_SO` | Source file name |
| $84 | `N_LSYM` | Local symbol / type |
| $A0 | `N_GSYM` | Global symbol |
| $C0 | `N_RSYM` | Register variable |

### GCC Stabs Format

GCC (`m68k-amigaos-gcc`) emits similar stabs, usually with tag `$3D474343` ("=GCC") or no tag at all.

### Line Number Information

Stabs records with `N_SLINE` provide source-to-address mapping, enabling source-level debugging in tools like wack:

```
N_SLINE: n_desc = source_line_number
         n_value = offset in current code hunk
```

---

## Reading Debug Info in IDA Pro

IDA Pro's Amiga HUNK loader (standard IDA plugin) parses:
- `HUNK_SYMBOL` → applies as function/data names automatically
- `HUNK_DEBUG` → partially parsed; stab `N_FUN` entries become function names

To see IDA's parsed symbols after loading:
- `View → Open Subviews → Names` — all named locations including HUNK_SYMBOL entries
- `View → Open Subviews → Segments` — hunk-to-segment mapping

---

## Stripping Debug Info

To produce a smaller executable without debug info:

**SAS/C:**
```
slink lib/c.o + myobj.o TO myexe NODBG
```

**GCC:**
```
m68k-amigaos-strip --strip-debug myexe
```

This removes HUNK_SYMBOL and HUNK_DEBUG records, reducing file size.

---

## Worked Hex Example (HUNK_SYMBOL)

Binary fragment from a real executable:
```
Offset  Hex Bytes           Decoded
$1A00:  00 00 03 F0         HUNK_SYMBOL
$1A04:  00 00 00 01         name_len = 1 (4 chars)
$1A08:  5F 6D 61 69         "_mai"
$1A0C:  6E 00 00 00         "n\0\0\0"
$1A10:  00 00 00 00         value = 0 (entry at start of code hunk)
$1A14:  00 00 00 02         name_len = 2 (8 chars)
$1A18:  5F 70 72 6F         "_pro"
$1A1C:  63 65 73 73         "cess"
$1A20:  00 00 00 78         value = $78
$1A24:  00 00 00 00         terminator
$1A28:  00 00 03 F2         HUNK_END
```

---

## References

- NDK39: `dos/doshunks.h` — HUNK_SYMBOL, HUNK_DEBUG constants
- SAS/C 6.x Programmer's Guide — debug output format
- GCC internals — stabs format documentation
- IDA Pro Amiga loader source (community) — stabs parsing
