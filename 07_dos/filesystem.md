[← Home](../README.md) · [AmigaDOS](README.md)

# Filesystem — FFS/OFS Block Structure and Disk Layout

## Overview

AmigaOS supports two native filesystem types: **OFS** (Old File System, OS 1.x) and **FFS** (Fast File System, OS 2.0+). Both use a block-based layout with 512-byte blocks. FFS differs by storing data blocks without headers, improving throughput. Understanding the on-disk layout is essential for FPGA core developers implementing virtual filesystems, HDF support, and ADF image handling.

---

## Disk Geometry and Layout

### ADF (Amiga Disk File) — Floppy Disk

```
Total: 880 KB = 1,760 sectors = 80 tracks × 2 sides × 11 sectors
Block size: 512 bytes
Blocks 0–1: Boot block (1 KB)
Block 880:  Root block (always at disk midpoint)
```

### HDF (Hard Disk File) — Hard Drive

```
Block 0:    Reserved (or RDB — Rigid Disk Block)
Block 1+:   RDB partition table (if present)
Partition:  Starts at first block of partition
            Root block at partition midpoint
```

---

## Block Types

| Type | ID | Constant | Purpose |
|---|---|---|---|
| Boot block | — | (bytes 0–1023) | Boot code + filesystem ID (`DOS\0` to `DOS\7`) |
| Root block | 2 | `T_HEADER` | Volume root directory — always at midpoint |
| File header | 2 | `T_HEADER` | File metadata + first 72 data block pointers |
| Directory | 2 | `T_HEADER` | Subdirectory — contains 72-slot hash table |
| Data block | 8 | `T_DATA` | OFS: 24-byte header + 488 data bytes |
| Extension | 16 | `T_LIST` | Overflow block pointers for files >72 blocks |
| Bitmap block | — | — | Free/allocated block tracking |

---

## Boot Block (Blocks 0–1)

```
Offset  Size  Field
──────  ────  ─────────────────────
$00     4     Filesystem ID — "DOS\0" to "DOS\7"
$04     4     Checksum
$08     4     Root block number (usually 880)
$0C     1012  Boot code (optional — loaded by ROM bootstrap)
```

### Filesystem ID Variants

| ID | Hex | Description |
|---|---|---|
| `DOS\0` | $444F5300 | OFS (original) |
| `DOS\1` | $444F5301 | FFS (fast file system) |
| `DOS\2` | $444F5302 | OFS + International mode (case-insensitive) |
| `DOS\3` | $444F5303 | FFS + International mode |
| `DOS\4` | $444F5304 | FFS + Directory cache |
| `DOS\5` | $444F5305 | OFS + International + Directory cache |
| `DOS\6` | $444F5306 | OFS + Long filenames (OS 3.5+) |
| `DOS\7` | $444F5307 | FFS + Long filenames (OS 3.5+) |

---

## Root Block (Block 880 on Floppy)

The root block is the entry point for the entire filesystem. It always lives at the midpoint of the partition:

```
root_block_number = (total_blocks) / 2  /* e.g., 1760/2 = 880 */
```

### Root Block Layout (512 bytes)

```
Offset  Size    Field                   Description
──────  ──────  ──────────────────────  ────────────────────────────────
$000    4       type                    Always 2 (T_HEADER)
$004    4       header_key              Own block number
$008    4       high_seq                0 (unused for root)
$00C    4       ht_size                 Hash table size (72 for DD floppy)
$010    4       first_data              0 (unused)
$014    4       checksum                Block checksum
$018    288     ht[72]                  Hash table: LONG[72] block pointers
                                        for directory entries (0 = empty slot)
$138    4       bm_flag                 Bitmap valid flag (-1 = valid)
$13C    100     bm_pages[25]            LONG[25] pointers to bitmap blocks
$1A0    4       bm_ext                  Pointer to extended bitmap block
$1A4    12      last_root_alteration    DateStamp: root last modified
$1B0    32      disk_name               BSTR: volume name (length-prefixed)
$1D0    4       (reserved)
$1D4    12      last_disk_alteration    DateStamp: disk last modified
$1E0    12      creation_date           DateStamp: volume creation date
$1EC    4       (reserved)
$1F0    4       extension              0 (unused for root)
$1F4    4       sec_type               1 = ST_ROOT
$1F8    4       (reserved)
$1FC    ← end of 512-byte block
```

---

## Hash Function

File and directory names are hashed into the hash table slots:

```c
/* The canonical AmigaDOS hash function: */
ULONG HashName(const char *name, ULONG table_size)
{
    ULONG hash = (ULONG)strlen(name);
    for (int i = 0; name[i]; i++)
    {
        hash = (hash * 13 + toupper((unsigned char)name[i])) & 0x7FF;
    }
    return hash % table_size;
}
/* table_size = 72 for DD floppy, 128 for HD floppy */
```

### Hash Collision Resolution

Collisions are resolved by **chaining**: each file/directory header has a `hash_chain` pointer (at offset `$1F0`) linking to the next entry that hashed to the same slot. The chain ends with 0.

```
Hash Table (root block):
  Slot 0: → 0 (empty)
  Slot 1: → Block 950 ("Startup-Sequence")
           └→ Block 1100 ("System-Startup") ← hash_chain
               └→ 0 (end)
  Slot 2: → Block 882 ("Libs")
  ...
```

---

## File Header Block

```
Offset  Size    Field                   Description
──────  ──────  ──────────────────────  ──────────────────────────────
$000    4       type                    2 (T_HEADER)
$004    4       header_key              Own block number
$008    4       high_seq                Number of data block pointers stored here
$00C    4       data_size               0 (unused in file header)
$010    4       first_data              First data block (OFS only — FFS uses table)
$014    4       checksum
$018    288     data_blocks[72]         LONG[72] — block pointers to data blocks
                                        Stored in REVERSE ORDER: [71]=first, [0]=last
$138    — ...   (padding/reserved)
$144    4       protect                 Protection bits (RWED)
$148    4       byte_size               File size in bytes
$14C    80      comment                 BSTR: file comment
$19C    12      date                    DateStamp: file modification date
$1A8    32      filename                BSTR: file name (length-prefixed)
$1D0    4       real_entry              For hard links: the real file header
$1D4    4       next_link               For hard links: next link to same file
$1EC    4       hash_chain              Next entry in same hash slot (0 = end)
$1F0    4       parent                  Block number of parent directory
$1F4    4       extension              Block number of extension block (0 = none)
$1F8    4       sec_type               -3 = ST_FILE
```

> **Reverse order**: Data block pointers in `data_blocks[]` are stored **last-to-first**. Index 71 points to the first data block, index 70 to the second, etc. This is a BCPL heritage quirk.

---

## OFS vs FFS — Data Block Differences

### OFS Data Block (T_DATA = 8)

```
$000    4       type            8 (T_DATA)
$004    4       header_key      Pointer back to file header
$008    4       seq_num         Sequence number (1-based)
$00C    4       data_size       Bytes of valid data in this block
$010    4       next_data       Next data block (0 = last)
$014    4       checksum
$018    488     data[488]       Actual file data (488 usable bytes)
```
**Efficiency**: 488 / 512 = **95.3%** — 24 bytes wasted per block on headers.

### FFS Data Block

```
$000    512     data[512]       Pure file data — no header overhead
```
**Efficiency**: 512 / 512 = **100%**

| Feature | OFS | FFS |
|---|---|---|
| Bytes per data block | 488 | 512 |
| Header overhead | 24 bytes/block | 0 |
| Self-describing blocks | Yes (can recover from corruption) | No |
| Max filename | 30 chars | 30 chars (107 with DOS\6/\7) |
| Throughput | ~5% slower | Baseline |
| International mode | DOS\2 | DOS\3 |
| Directory cache | No | DOS\4 |
| Min OS version | 1.0 | 2.0 |

---

## Bitmap Blocks — Free Space Tracking

The bitmap tracks which blocks are free (1) or allocated (0):

```c
/* Each bitmap block covers up to (512-4) × 8 = 4064 blocks */
struct BitmapBlock {
    ULONG checksum;         /* block checksum */
    ULONG map[127];         /* bit 1 = free, bit 0 = allocated */
    /* bit 0 of map[0] = block corresponding to this bitmap's range */
};
```

The root block's `bm_pages[25]` array can reference up to 25 bitmap blocks, covering 25 × 4064 = **101,600 blocks** (≈49 MB). Larger partitions need `bm_ext` extension blocks.

---

## Checksum Algorithm

```c
LONG ComputeBlockChecksum(ULONG *block, LONG longs)
{
    LONG sum = 0;
    block[5] = 0;  /* clear checksum field before computing */
    for (int i = 0; i < longs; i++)
        sum += block[i];
    return -sum;   /* store at block[5] so total = 0 */
}
/* Verify: if sum of all 128 longs (incl. checksum) = 0, block is valid */
```

---

## File Extension Blocks

Files larger than 72 data blocks need extension blocks to store additional pointers:

```
extension_block.data_blocks[72] → next 72 data block pointers
extension_block.extension → next extension block (or 0)
```

Each extension block adds 72 more data block pointers. With FFS (512 bytes/block):
- 72 blocks = 36 KB directly in file header
- +72 per extension = 36 KB more per extension
- Maximum chain depth is effectively unlimited

---

## Practical: Reading an ADF Image

```python
import struct

def read_adf(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    # Boot block — filesystem type
    fs_type = data[0:4]
    print(f"Filesystem: {fs_type}")  # b'DOS\x00' = OFS, b'DOS\x01' = FFS

    # Root block at block 880 (offset 880 * 512 = 450560)
    root_off = 880 * 512
    root = data[root_off:root_off + 512]

    # Volume name (BSTR at offset $1B0)
    name_len = root[0x1B0]
    vol_name = root[0x1B1:0x1B1 + name_len].decode('ascii')
    print(f"Volume: {vol_name}")

    # Hash table: 72 entries starting at offset $018
    ht = struct.unpack('>72I', root[0x18:0x18 + 72 * 4])
    for i, blk in enumerate(ht):
        if blk != 0:
            # Read the file/dir header at that block
            hdr_off = blk * 512
            hdr = data[hdr_off:hdr_off + 512]
            fname_len = hdr[0x1A8]
            fname = hdr[0x1A9:0x1A9 + fname_len].decode('ascii')
            sec_type = struct.unpack('>i', hdr[0x1F4:0x1F8])[0]
            kind = "DIR" if sec_type == 2 else "FILE"
            print(f"  [{i:2d}] {kind} {fname} (block {blk})")
```

---

## References

- NDK39: `dos/filehandler.h`
- Ralph Babel: *The AmigaDOS Manual* (3rd edition) — definitive FFS reference
- Laurent Clévy: *The Amiga Filesystem* — http://lclevy.free.fr/adflib/
- See also: [packet_system.md](packet_system.md) — filesystem handler protocol
- See also: [locks_examine.md](locks_examine.md) — lock/examine API layer
