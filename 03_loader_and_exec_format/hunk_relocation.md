[← Home](../README.md) · [Loader & HUNK Format](README.md)

# HUNK Relocation Mechanics

## Overview

Relocation is the process of **patching absolute addresses** in a loaded executable to reflect its actual memory location. Since AmigaOS allocates memory dynamically via `AllocMem()`, a program cannot know its load address at compile time — all inter-hunk references must be fixed up at runtime by the loader.

---

## Why Relocation Is Necessary

Consider a program with a code hunk and a data hunk:

```c
/* Source code: */
const char message[] = "Hello";    /* in data hunk */
void foo(void) {
    puts(message);  /* code references data hunk — absolute address needed */
}
```

The linker places `message` at offset 0 in the data hunk. But the absolute address of `message` depends on where `AllocMem` places the data hunk at runtime — this is unknown at link time.

```asm
; What the linker writes (before loading):
foo:
    PEA     $00000000      ; ← linker writes offset 0 (within data hunk)
    JSR     _puts
    ADDQ.L  #4, SP

; After loading (data hunk loaded at $00040000):
foo:
    PEA     $00040000      ; ← loader patches: 0 + $40000 = $40000
    JSR     _puts
    ADDQ.L  #4, SP
```

The relocation table tells the loader **which bytes** to patch and **what base address** to add.

---

## Visual: Before and After Relocation

```
BEFORE (raw file):                    AFTER (loaded at runtime):
                                      Code hunk loaded at $00020000
                                      Data hunk loaded at $00040000

Code Hunk:                            Code Hunk:
offset $00: MOVEQ #0, D0             offset $00: MOVEQ #0, D0
offset $04: LEA $00000000, A0  ←─┐   offset $04: LEA $00040000, A0  ✓ patched
offset $0A: BSR $00000020       │    offset $0A: BSR $00000020
offset $0E: MOVE.L $00000010, D1 ←┤   offset $0E: MOVE.L $00040010, D1 ✓ patched
                                 │
HUNK_RELOC32:                    │
  target_hunk = 1 (data)         │
  offsets = [$06, $10]  ─────────┘    Relocation adds $00040000 at these offsets
```

---

## HUNK_RELOC32 Format ($3EC)

The most common relocation type:

```
HUNK_RELOC32 ($000003EC)

[Repeat until terminator:]
  <num_offsets>       Number of longword addresses to patch for this target hunk
  <target_hunk>       Index of the hunk whose base address is added
  <offset_0>          Byte offset within the CURRENT hunk to patch
  <offset_1>
  ...

<0>                   num_offsets = 0 terminates the reloc list
```

### Patching Algorithm

```c
/* For each entry group in HUNK_RELOC32 of hunk H: */
for (group = 0; group < num_groups; group++)
{
    ULONG count       = Read32();  /* how many patch sites */
    if (count == 0) break;          /* terminator */
    ULONG target_hunk = Read32();  /* which hunk's base to add */
    ULONG target_base = segment_base_address[target_hunk];

    for (ULONG i = 0; i < count; i++)
    {
        ULONG offset = Read32();   /* byte offset within current hunk */
        ULONG *patch = (ULONG *)(hunk_H_base + offset);
        *patch += target_base;     /* add actual load address */
    }
}
```

The value at the patch site already contains the **hunk-relative offset** written by the linker. Adding the target hunk's actual base address produces the final absolute address.

### Worked Example — Two Hunks

```
File layout:
  Hunk 0 (CODE): 128 bytes, references data at offsets $18 and $2C
  Hunk 1 (DATA): 64 bytes

Loaded at runtime:
  Hunk 0 → $00020000 (code)
  Hunk 1 → $00030000 (data)

HUNK_RELOC32 for Hunk 0:
  $00000002           ; 2 offsets to patch
  $00000001           ; target = hunk 1 (data)
  $00000018           ; patch at code+$18
  $0000002C           ; patch at code+$2C
  $00000000           ; terminator

Before patch:
  code[$18] = $00000000  (data offset 0)
  code[$2C] = $00000010  (data offset $10)

After patch:
  code[$18] = $00000000 + $00030000 = $00030000  ✓
  code[$2C] = $00000010 + $00030000 = $00030010  ✓
```

### Self-Referencing (Intra-Hunk) Relocation

Code can also reference its own hunk:

```
HUNK_RELOC32 for Hunk 0:
  $00000001           ; 1 offset
  $00000000           ; target = hunk 0 (self!)
  $00000044           ; patch at code+$44
  $00000000           ; terminator

This happens when code contains an absolute reference to a label
within the same hunk (e.g., a jump table with absolute addresses).
```

---

## HUNK_RELOC32SHORT ($3FC) — Compact Variant

Uses 16-bit values instead of 32-bit for offsets:

```
HUNK_RELOC32SHORT ($000003FC)

[Repeat:]
  <num_offsets>  (UWORD — 16-bit!)
  <target_hunk>  (UWORD)
  <offset_0>     (UWORD)
  ...

<0>              UWORD terminator
[padding to longword boundary if needed]
```

Saves space when all patch offsets fit in 16 bits (hunk size < 64 KB). The **semantics are identical** to HUNK_RELOC32 — only the field sizes differ.

Modern linkers (vlink, vasm) prefer this format for small programs.

---

## HUNK_RELOC16 ($3ED) and HUNK_RELOC8 ($3EE)

Same format as HUNK_RELOC32 but patch **16-bit** or **8-bit** values respectively:

| Type | Patches | Use Case |
|---|---|---|
| HUNK_RELOC32 | ULONG (4 bytes) | Standard — absolute 32-bit addresses |
| HUNK_RELOC16 | UWORD (2 bytes) | 16-bit displacement mode (rare) |
| HUNK_RELOC8 | UBYTE (1 byte) | 8-bit short-branch offset (extremely rare) |

HUNK_RELOC16 and HUNK_RELOC8 are almost never seen in practice — the 68000 doesn't commonly use 16-bit absolute addresses, and linkers generate PC-relative code for short displacements instead.

---

## HUNK_DREL32 ($3F7) — Base-Relative Compact Relocation

An alternative relocation format used by some linkers (BLink):

```
HUNK_DREL32 ($000003F7)

[Repeat:]
  <num_offsets>  (UWORD)
  <target_hunk>  (UWORD)
  <offset_0>     (UWORD)
  ...

<0>              UWORD terminator
```

Semantically identical to HUNK_RELOC32 but uses 16-bit fields. More compact for programs with many relocations and small hunk sizes (< 64 KB). Supported by `InternalLoadSeg`.

---

## HUNK_RELRELOC32 ($3FD) — PC-Relative Relocation

Patches a **32-bit displacement** rather than an absolute address:

```c
/* Patch algorithm for PC-relative: */
*patch = target_base - (current_hunk_base + offset);
/* The patched value is a signed offset from the patch site to the target */
```

Used by GCC with `-fPIC` for position-independent code. Rare in standard AmigaOS programs.

---

## PC-Relative References (No Relocation Needed)

The 68020+ supports **32-bit PC-relative addressing**, and even the 68000 supports 16-bit PC-relative:

```asm
; 68000 — 16-bit PC-relative (within ±32 KB):
LEA     myData(PC), A0      ; PC-relative — no reloc needed
BSR     myFunction           ; PC-relative branch — no reloc

; 68020+ — 32-bit PC-relative:
MOVE.L  myData(PC), D0       ; PC-relative with 32-bit displacement
```

PC-relative references are **relocation-free** — the offset is relative to the instruction pointer, so it remains valid regardless of where the code loads.

| Compiler | Default Mode | Relocation Impact |
|---|---|---|
| SAS/C | Absolute addressing | Heavy relocation (many HUNK_RELOC32 entries) |
| GCC | PC-relative (`-fpic`) | Minimal relocation — smaller executables |
| VBCC | PC-relative (with small code model) | Similar to GCC |

> **Practical impact**: A program with 500 internal function calls generates 500 HUNK_RELOC32 entries with absolute addressing (SAS/C), but nearly zero with PC-relative code (GCC). This affects both file size and load time.

---

## Relocation and the Segment Chain

The loader tracks loaded segments as a **BPTR chain** (singly-linked list). The segment list head is returned by `LoadSeg()`:

```
Segment 0 (code):
  byte -4:   allocation size (for FreeMem)
  byte  0:   BPTR → Segment 1
  byte  4:   [code data starts here]

Segment 1 (data):
  byte -4:   allocation size
  byte  0:   BPTR → 0 (NULL = end of chain)
  byte  4:   [data starts here]
```

Each segment begins with a 4-byte BPTR to the next segment. Hunk index `n` in the relocation table corresponds to segment `n` in this chain. The base address used for relocation is `segment_address + 4` (skip the BPTR link).

---

## Relocation Error Scenarios

| Error | Cause | Symptom |
|---|---|---|
| Offset beyond hunk size | Corrupt HUNK_RELOC32 | Random memory corruption; Guru |
| Invalid target hunk index | Corrupt reloc table | Crash during load |
| Relocation to freed memory | Hunk couldn't be allocated | Dangling pointer — crash at use time |
| Missing relocation entry | Linker bug | Pointer has wrong value; subtle crash |
| Unaligned offset | Not longword-aligned | Bus error on 68000 (address error) |

---

## Viewing Relocations with Tools

### IDA Pro
After loading a HUNK file with the Amiga plugin, IDA resolves relocations automatically. The fixup table is visible in `View → Open Subviews → Fixups`.

### hexdump + manual

```bash
# Find HUNK_RELOC32 in raw hex:
xxd mybinary | grep "0003 ec"
# Then read num_offsets, target_hunk, and offset longwords
```

### Python scanner

```python
import struct

def dump_relocs(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    off = 0
    while off < len(data) - 4:
        tag = struct.unpack('>I', data[off:off+4])[0]
        if tag == 0x3EC:  # HUNK_RELOC32
            off += 4
            while True:
                count = struct.unpack('>I', data[off:off+4])[0]
                off += 4
                if count == 0: break
                target = struct.unpack('>I', data[off:off+4])[0]
                off += 4
                offsets = []
                for i in range(count):
                    o = struct.unpack('>I', data[off:off+4])[0]
                    offsets.append(f'${o:04X}')
                    off += 4
                print(f'  target=hunk{target} offsets={offsets}')
        else:
            off += 4

dump_relocs('mybinary')
```

---

## References

- NDK39: `dos/doshunks.h`
- *Amiga ROM Kernel Reference Manual: Libraries* — AmigaDOS chapter, `InternalLoadSeg`
- vlink linker documentation — relocation section
- See also: [HUNK Format](hunk_format.md) — complete hunk type reference
- See also: [Exe Load Pipeline](exe_load_pipeline.md) — how LoadSeg uses relocations
