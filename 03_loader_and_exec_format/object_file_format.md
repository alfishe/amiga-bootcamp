[← Home](../README.md) · [Loader & HUNK Format](README.md)

# Object File Format (HUNK_UNIT)

## Overview

Compiler output (`.o` files) uses `HUNK_UNIT` format — a variation of the HUNK executable format for **relocatable, unlinked code**. Multiple object files are combined by the linker to produce a final executable.

---

## Object File vs Executable

| Feature | Object file | Executable |
|---|---|---|
| Magic word | `HUNK_UNIT` ($3E7) | `HUNK_HEADER` ($3F3) |
| Unit name | Yes (HUNK_NAME) | No |
| External refs | `HUNK_EXT` (imports+exports) | None (resolved by linker) |
| Relocation | `HUNK_RELOC32` (partial) | `HUNK_RELOC32` (complete) |
| BSS | `HUNK_BSS` | `HUNK_BSS` |
| Loaded directly | No | Yes |

---

## Object File Structure

```
HUNK_UNIT ($000003E7)     — identifies this as an object file
HUNK_NAME ($000003E8)     — optional: source/module name
  <num_longs>
  <name string>

--- For each code/data/bss section: ---

HUNK_CODE / HUNK_DATA / HUNK_BSS
  <data>

HUNK_RELOC32              — intra-object relocations (if any)

HUNK_EXT                  — external symbol definitions + references
  EXT_DEF  _myfunc  = offset X    (export)
  EXT_REF32  _printf  [offsets]   (import)

HUNK_SYMBOL               — optional local symbols

HUNK_END

--- Repeat for additional sections ---
```

---

## Multi-Section Object Files

A single `.o` file can contain multiple code/data sections. Each section is a separate hunk terminated by `HUNK_END`:

```
HUNK_UNIT
HUNK_NAME  "mymodule.c"
HUNK_CODE              ; section 0: main code
  [code...]
HUNK_EXT               ; exports/imports for section 0
HUNK_END
HUNK_CODE              ; section 1: __initdata (constructor table)
  [init code...]
HUNK_END
HUNK_DATA              ; section 2: initialized data
  [data...]
HUNK_RELOC32           ; internal relocs for section 2
HUNK_END
HUNK_BSS               ; section 3: uninitialized data
HUNK_END
```

---

## Compiler Section Naming Convention

Different compilers use different conventions for code/data section organization:

### SAS/C 6.x

| Section | Type | Contents |
|---|---|---|
| `.text` | HUNK_CODE | Compiled functions |
| `.data` | HUNK_DATA | Initialized globals |
| `.bss` | HUNK_BSS | Uninitialized globals |
| `__CSEG` | HUNK_CODE | (alternate) code |
| `__DSEG` | HUNK_DATA | (alternate) data |

SAS/C 6.x uses HUNK_NAME to embed section names (matching HUNK_NAME format).

### GCC (m68k-amigaos)

GCC emits more sections:
```
.text           — code
.data           — initialized data
.bss            — BSS
.rodata         — read-only data (string literals, const)
.ctors          — C++ constructor table
.dtors          — C++ destructor table
```

VBCC follows a similar scheme to GCC.

---

## Library Archives (.lib)

A `.lib` file is an **archive of object files**, using `HUNK_LIB` ($3FA) and `HUNK_INDEX` ($3FB):

```
HUNK_LIB ($000003FA)
  <total_size>        size of all following library data in longs
  [HUNK_UNIT blocks for each member ...]

HUNK_INDEX ($000003FB)
  <size_in_longs>     size of index data
  [index entries...]
```

The index maps symbol names to their containing `HUNK_UNIT` within the library, allowing the linker to extract only the needed object files.

Libraries shipped with SAS/C, GCC, and VBCC use this format.

---

## Linker Operation (Overview)

The linker (`slink`, `blink`, `ld`) processes object files:

1. **Collect all HUNK_EXT exports** from every `.o` into a global symbol table
2. **Resolve HUNK_EXT imports** — for each `EXT_REF32`, find the defining object
3. **Pull in library members** — if an imported symbol lives in a `.lib`, add that object file
4. **Merge sections** — combine all `.text` hunks into one code hunk, all `.data` into one data hunk, etc.
5. **Emit HUNK_RELOC32** — for each resolved external reference, emit a relocation entry
6. **Write HUNK_HEADER** — calculate final hunk sizes and write executable header

---

## Inspecting Object Files

### hexdump

```bash
xxd myfile.o | head -40   # look for $000003E7 (HUNK_UNIT) at start
```

### hunkinfo (community tool)

```bash
hunkinfo myfile.o   # lists all hunks, sizes, symbols, externals
```

### IDA Pro

IDA can load `.o` files directly using the Amiga HUNK loader plugin — useful for reversing library object files without full executable context.

---

## References

- NDK39: `dos/doshunks.h`
- SAS/C 6.x Programmer's Guide — object file chapter
- VBCC documentation — object file format
- vlink linker manual (covers HUNK_LIB/HUNK_INDEX): http://sun.hasenbraten.de/vlink/
- GCC m68k-amigaos port documentation
