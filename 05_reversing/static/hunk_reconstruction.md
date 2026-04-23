[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Static Analysis — HUNK Reconstruction

## Overview

Manually parsing a HUNK binary from a hex dump is a foundational Amiga RE skill. It reveals segment boundaries, symbol tables, and relocation data before any tool processing.

---

## Step 1 — Identify Magic and Header

```bash
xxd mybinary | head -8
```

```
00000000: 0000 03f3  ← HUNK_HEADER magic
00000004: 0000 0000  ← resident library list (always 0)
00000008: 0000 0003  ← num_hunks = 3
0000000c: 0000 0000  ← first_hunk = 0
00000010: 0000 0002  ← last_hunk = 2
00000014: 0000 0200  ← hunk 0: 0x200 longs = 0x800 bytes (code)
00000018: 0000 0020  ← hunk 1: 0x20 longs = 0x80 bytes (data)
0000001c: 0000 0010  ← hunk 2: 0x10 longs = 0x40 bytes (BSS)
```

Each size longword: **bits 31–30** = memory type flag, **bits 29–0** = size in longs.

---

## Step 2 — Walk the Hunk Stream

After the header, scan longword-by-longword:

```
$000003E9  → HUNK_CODE: read next longword = size, then size*4 bytes
$000003EA  → HUNK_DATA: same
$000003EB  → HUNK_BSS: read size longword only (no data)
$000003EC  → HUNK_RELOC32: read pairs until terminator 0
$000003F0  → HUNK_SYMBOL: read (name_len, name, value) until name_len=0
$000003F1  → HUNK_DEBUG: read size longword, skip size*4 bytes
$000003F2  → HUNK_END: advance to next hunk
```

### Grep for hunk boundaries
```bash
xxd mybinary | grep -E "0003 (e9|ea|eb|ec|f0|f1|f2|f3)"
```

---

## Step 3 — Extract HUNK_SYMBOL Table

```bash
# find HUNK_SYMBOL ($3F0)
python3 - <<'EOF'
import struct, sys

data = open("mybinary", "rb").read()
i = 0
while i < len(data) - 4:
    tag = struct.unpack_from(">I", data, i)[0]
    if tag == 0x3F0:  # HUNK_SYMBOL
        print(f"HUNK_SYMBOL at offset {i:#x}")
        i += 4
        while True:
            nlen = struct.unpack_from(">I", data, i)[0]
            if nlen == 0: break
            name = data[i+4 : i+4+nlen*4].rstrip(b"\x00").decode("ascii","replace")
            val  = struct.unpack_from(">I", data, i+4+nlen*4)[0]
            print(f"  {name} = {val:#x}")
            i += 4 + nlen*4 + 4
    else:
        i += 4
EOF
```

---

## Step 4 — Resolve HUNK_EXT Imports/Exports

In object files (HUNK_UNIT), `HUNK_EXT` carries import/export tables:

```python
# Simplified HUNK_EXT parser
elif tag == 0x3EF:  # HUNK_EXT
    i += 4
    while True:
        word = struct.unpack_from(">I", data, i)[0]
        if word == 0: break
        ext_type = (word >> 24) & 0xFF
        nlen     = word & 0x00FFFFFF
        name = data[i+4 : i+4+nlen*4].rstrip(b"\x00").decode("ascii","replace")
        i += 4 + nlen * 4
        if ext_type in (1, 2):         # EXT_DEF / EXT_ABS
            val = struct.unpack_from(">I", data, i)[0]; i += 4
            print(f"  EXPORT {name} = {val:#x}")
        elif ext_type == 0x81:         # EXT_REF32
            nrefs = struct.unpack_from(">I", data, i)[0]; i += 4
            refs  = struct.unpack_from(f">{nrefs}I", data, i); i += nrefs*4
            print(f"  IMPORT {name} @ {[hex(r) for r in refs]}")
```

---

## Step 5 — Annotating Reloc Patches in IDA

After loading the HUNK file in IDA:
1. `View → Open Subviews → Fixups` — lists all HUNK_RELOC32 patch sites
2. Press `F5` on a relocated longword to see the computed address
3. Use `Edit → Operand type → Offset (data segment)` to annotate as a pointer

IDA's Amiga loader applies relocations automatically, so all cross-hunk pointers show their final resolved addresses.

---

## References

- NDK39: `dos/doshunks.h`
- `hunk_format.md` — hunk type code reference
- `hunk_relocation.md` — HUNK_RELOC32 mechanics
- vlink documentation (HUNK appendix): http://sun.hasenbraten.de/vlink/
