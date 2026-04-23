[← Home](../README.md) · [Exec Kernel](README.md)

# Memory Management — AllocMem, FreeMem, MemHeader

## Overview

AmigaOS memory management is built directly into `exec.library`. There is no `malloc`/`free` in the OS itself — applications call `AllocMem` and `FreeMem` which operate on a linked list of `MemHeader` regions representing physical RAM.

---

## MemHeader — Memory Region Descriptor

```c
/* exec/memory.h — NDK39 */
struct MemHeader {
    struct Node  mh_Node;       /* ln_Type=NT_MEMORY, ln_Pri=region priority */
                                /* ln_Name = e.g. "chip memory" */
    UWORD        mh_Attributes; /* MEMF_* flags describing this region */
    struct MemChunk *mh_First;  /* pointer to first free chunk in this region */
    APTR         mh_Lower;      /* lowest byte address of region */
    APTR         mh_Upper;      /* highest byte address + 1 */
    ULONG        mh_Free;       /* total free bytes currently */
};

struct MemChunk {
    struct MemChunk *mc_Next;   /* next free chunk (NULL = end of list) */
    ULONG            mc_Bytes;  /* size of this free chunk in bytes */
};
```

The OS maintains a doubly-linked list of `MemHeader` regions at `SysBase→MemList`. On a stock A1200:
- `"chip memory"` covering `$000000–$1FFFFF` (2 MB Chip RAM)
- `"fast memory"` covering `$200000–$9FFFFF` (up to 8 MB Fast RAM if fitted)

---

## MEMF_ Flag Constants

```c
/* exec/memory.h — NDK39 */
#define MEMF_ANY      0L          /* no placement preference */
#define MEMF_PUBLIC   (1L<<0)     /* accessible by all hardware/software */
#define MEMF_CHIP     (1L<<1)     /* must be in Chip RAM (DMA-reachable) */
#define MEMF_FAST     (1L<<2)     /* prefer Fast RAM (CPU-only, faster) */
#define MEMF_CLEAR    (1L<<16)    /* zero-fill the allocation */
#define MEMF_LARGEST  (1L<<17)    /* return single largest free block */
#define MEMF_REVERSE  (1L<<18)    /* allocate from top of list */
#define MEMF_TOTAL    (1L<<19)    /* AvailMem: report total, not largest free */
```

**Chip RAM** is required for anything the custom chips DMA from — bitmaps, audio samples, Copper lists, blitter sources/destinations, sprite data. The custom chip DMA controllers cannot reach Fast RAM.

**Fast RAM** has no DMA contention with the custom chips, making it faster for pure CPU use.

---

## AllocMem / FreeMem

```c
/* exec/execbase.h — LVO -198 */
APTR AllocMem(ULONG byteSize, ULONG requirements);
/* Returns: pointer to allocated block, or NULL on failure */

/* LVO -210 */
void FreeMem(APTR memoryBlock, ULONG byteSize);
```

### Usage

```c
/* Allocate 512 bytes of Chip RAM, zero-filled: */
UBYTE *buf = AllocMem(512, MEMF_CHIP | MEMF_CLEAR);
if (!buf) { /* handle out-of-memory */ }

/* Free it: */
FreeMem(buf, 512);
```

> [!IMPORTANT]
> `FreeMem` requires the **exact same size** as `AllocMem`. The OS does not store the size internally — you must track it yourself.

---

## AllocVec / FreeVec (OS 2.0+)

```c
/* LVO -684 (exec.library 36+) */
APTR AllocVec(ULONG byteSize, ULONG requirements);
void FreeVec(APTR memoryBlock);   /* LVO -690 */
```

`AllocVec` stores the size in the 4 bytes immediately before the returned pointer, allowing `FreeVec` to work without a size argument. Prefer this in new code.

---

## AvailMem — Query Free Memory

```c
/* LVO -216 */
ULONG AvailMem(ULONG requirements);
```

```c
ULONG chip_free = AvailMem(MEMF_CHIP);
ULONG fast_free = AvailMem(MEMF_FAST);
ULONG total_chip = AvailMem(MEMF_CHIP | MEMF_TOTAL);
```

---

## Pool Allocator (OS 3.0+)

For many small allocations, use the pool API which reduces fragmentation:

```c
/* LVO -696 */
APTR pool = CreatePool(MEMF_ANY, 4096, 1024);
/* puddleSize=4096, threshSize=1024 */

APTR p1 = AllocPooled(pool, 32);   /* LVO -702 */
FreePooled(pool, p1, 32);           /* LVO -708 */

DeletePool(pool);                   /* LVO -714 */
```

---

## Memory Map (A1200 Example)

| Range | Type | Used for |
|---|---|---|
| `$000000–$000400` | Chip | 68k exception vectors |
| `$000400–$000BFF` | Chip | exec library, SysBase |
| `$000C00–$1FFFFF` | Chip | Application allocations, DMA buffers |
| `$200000–$9FFFFF` | Fast | Fast RAM expansion (if present) |
| `$A00000–$BFFFFF` | Slow/Ranger | A500 slow RAM (not on A1200) |
| `$BFD000–$BFDFFF` | CIA | CIA-B registers |
| `$BFE001–$BFEFFF` | CIA | CIA-A registers |
| `$C00000–$D7FFFF` | Slow | A500 slow RAM expansion |
| `$D80000–$DFFFFF` | Custom | Custom chip registers ($DFF000) |
| `$E00000–$E7FFFF` | ROM mirror | (A500) |
| `$F80000–$FFFFFF` | ROM | Kickstart 3.1 (512 KB) |

---

## References

- NDK39: `exec/memory.h`, `exec/execbase.h`
- ADCD 2.1: `AllocMem`, `FreeMem`, `AllocVec`, `FreeVec`, `CreatePool`
- [address_space.md](../01_hardware/common/address_space.md) — full address map
- *Amiga ROM Kernel Reference Manual: Exec* — memory management chapter
