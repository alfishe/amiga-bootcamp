[← Home](../README.md) · [CPU & MMU](README.md)

# Cache Management — CacheClearU, CacheControl, CACR

## Overview

68020+ processors have instruction and data caches that must be managed correctly, especially when loading code (hunks), self-modifying code, or DMA operations. AmigaOS provides `exec.library` functions for safe cache management.

---

## exec.library Cache Functions

| LVO | Function | Description |
|---|---|---|
| −636 | `CacheClearU()` | Flush all caches (user-friendly, safe) |
| −642 | `CacheClearE(addr, len, caches)` | Flush specific address range |
| −648 | `CacheControl(cacheBits, cacheMask)` | Enable/disable cache features |
| −762 | `CachePreDMA(addr, &len, flags)` | Prepare for DMA transfer |
| −768 | `CachePostDMA(addr, &len, flags)` | Cleanup after DMA transfer |

---

## When to Flush Caches

| Scenario | Function to Call |
|---|---|
| After loading code from disk | `CacheClearU()` |
| After JIT / dynamic code generation | `CacheClearE(code, len, CACRF_ClearI)` |
| Before DMA read from memory | `CachePreDMA()` (flush dirty data cache) |
| After DMA write to memory | `CachePostDMA()` (invalidate stale data cache) |
| After `SetFunction()` patching | `CacheClearU()` |

---

## CacheControl Bits

```c
/* exec/execbase.h — NDK39 */
#define CACRF_EnableI      (1<<0)  /* enable instruction cache */
#define CACRF_FreezeI      (1<<1)  /* freeze instruction cache */
#define CACRF_ClearI       (1<<3)  /* clear instruction cache */
#define CACRF_IBE          (1<<4)  /* instruction burst enable */
#define CACRF_EnableD      (1<<8)  /* enable data cache */
#define CACRF_FreezeD      (1<<9)  /* freeze data cache */
#define CACRF_ClearD       (1<<11) /* clear data cache */
#define CACRF_DBE          (1<<12) /* data burst enable */
#define CACRF_WriteAllocate (1<<13) /* write-allocate data cache */
#define CACRF_EnableE      (1<<30) /* enable external cache (A3640) */
#define CACRF_CopyBack     (1<<31) /* enable copyback mode */
```

---

## CACR Register (Direct Access)

```asm
; 68040 CACR bits:
;   bit 15: DE (data cache enable)
;   bit 14: — (reserved)
;   bit 13: —
;   bit 12: —  
;   bit 11: —
;   bit 10: —
;   bit 9: —
;   bit 8: IE (instruction cache enable)

; Read CACR:
    movec.l cacr,d0

; Flush all caches (68040/060):
    cpusha  dc              ; push data cache
    cpusha  ic              ; push instruction cache
    cinva   dc              ; invalidate data cache
    cinva   ic              ; invalidate instruction cache

; 68030:
    movec.l cacr,d0
    or.l    #$0808,d0       ; set ClearI + ClearD bits
    movec.l d0,cacr
```

---

## DMA and Cache Coherency

Amiga custom chips (blitter, copper, audio, disk) perform DMA directly to/from Chip RAM, bypassing the CPU cache. This creates coherency issues on 68040/060:

```c
/* Before blitter reads data you just wrote: */
CachePreDMA(data, &length, DMA_ReadFromRAM);

/* After blitter writes data you want to read: */
CachePostDMA(data, &length, 0);
```

---

## References

- NDK39: `exec/execbase.h`
- Motorola: *MC68040 User's Manual* — cache chapter
- ADCD 2.1: `CacheClearU`, `CacheClearE`, `CacheControl`
