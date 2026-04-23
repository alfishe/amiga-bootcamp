[← Home](../README.md) · [AmigaDOS](README.md)

# Filesystem — FFS/OFS Block Structure

## Overview

AmigaOS supports two native filesystem types: **OFS** (Old File System, OS 1.x) and **FFS** (Fast File System, OS 2.0+). Both use a block-based layout with 512-byte blocks. FFS differs by storing data blocks without headers, improving throughput.

---

## Block Types

| Block | Type ID | Description |
|---|---|---|
| Boot block | `"DOS\0"` / `"DOS\1"` | Blocks 0–1; OFS=`DOS\0`, FFS=`DOS\1` |
| Root block | `T_HEADER` (2) | Always at middle of partition; directory root |
| File header | `T_HEADER` (2) | Metadata for one file |
| Directory header | `T_HEADER` (2) | Metadata for one directory |
| Data block | `T_DATA` (8) | OFS: header + data; FFS: pure data |
| File extension | `T_LIST` (16) | Overflow pointer table for large files |
| Hash chain | — | Root/dir blocks have a 72-entry hash table |

---

## Root Block Layout (Simplified)

| Offset | Field | Description |
|---|---|---|
| 0 | `type` | Always 2 (`T_HEADER`) |
| 4 | `header_key` | Own block number |
| 8 | `high_seq` | Number of data blocks in hash table |
| 12 | `ht_size` | Hash table size (usually 72) |
| 16 | `first_data` | Unused |
| 20 | `checksum` | Block checksum |
| 24–312 | `ht[72]` | Hash table: block pointers for directory entries |
| 420 | `bm_flag` | Bitmap valid flag (`-1` = valid) |
| 424–472 | `bm_pages[25]` | Pointers to bitmap blocks |
| 484 | `last_altered_days` | Modification date |
| 504 | `disk_name` | BSTR: volume name |

---

## Hash Function

File/directory names are hashed into the 72-slot table:

```c
ULONG hash_name(const char *name, int table_size) {
    ULONG hash = strlen(name);
    for (int i = 0; name[i]; i++) {
        hash = hash * 13 + toupper(name[i]);
        hash &= 0x7FF;
    }
    return hash % table_size;
}
```

Collisions are resolved by chaining: each file/dir header has a `hash_chain` pointer to the next entry in the same slot.

---

## OFS vs FFS

| Feature | OFS (`DOS\0`) | FFS (`DOS\1`) |
|---|---|---|
| Data blocks | 24-byte header + 488 bytes data | Pure 512 bytes data |
| Max filename | 30 chars | 30 chars |
| International | No | `DOS\2` (INTL OFS), `DOS\3` (INTL FFS) |
| Dir cache | No | `DOS\4` (FFS + dir cache) |
| Throughput | ~488/512 = 95% efficiency | 100% efficiency |

---

## Checksum Algorithm

```c
LONG compute_checksum(ULONG *block, int longs) {
    LONG sum = 0;
    for (int i = 0; i < longs; i++) sum += block[i];
    return -sum;  /* stored in the checksum field to make total = 0 */
}
```

---

## References

- NDK39: `dos/filehandler.h`
- Ralph Babel: *The AmigaDOS Manual* (3rd edition) — definitive FFS reference
- Laurent Clevy: *The Amiga Filesystem* — http://lclevy.free.fr/adflib/
