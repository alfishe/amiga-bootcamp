[← Home](../README.md) · [CPU & MMU](README.md)

# MMU Management — 68030/040/060 Memory Management Units

## Overview

The Motorola 68030, 68040, and 68060 include on-chip **MMUs** (Memory Management Units) that provide virtual-to-physical address translation, memory protection, and cache control. AmigaOS itself does **not use the MMU** for virtual memory — it was designed for a flat address space. However, several third-party tools and libraries use the MMU for:

- **Enforcer/MuForce** — detecting illegal memory accesses
- **VMM** — virtual memory (swap to disk)
- **CyberGuard/MuGuard** — memory protection
- **SetPatch/MuSetPatch** — cache management

---

## MMU Architecture Comparison

| Feature | 68030 | 68040 | 68060 |
|---|---|---|---|
| MMU type | External (on-chip optional) | On-chip, always present | On-chip, always present |
| Page sizes | 256B, 512B, 1K, 2K, 4K, 8K, 16K, 32K | 4K, 8K (fixed) | 4K, 8K (fixed) |
| Table levels | 1–4 configurable | Fixed 3-level | Fixed 3-level |
| TLB entries | 22 (ATC) | 64 (data) + 64 (instruction) | 48 (data) + 48 (instruction) |
| PMMU instructions | `PMOVE`, `PFLUSH`, `PTEST`, `PLOAD` | `PFLUSHA`, `PFLUSHN`, `CINV`, `CPUSH` | Same as 040 |
| Transparent translation | `TT0`, `TT1` (via PMOVE) | `DTT0/1`, `ITT0/1` (via MOVEC) | Same as 040 |
| Supervisor root pointer | `SRP` (via PMOVE) | `SRP` (via MOVEC) | `SRP` (via MOVEC) |
| CPU root pointer | `CRP` (via PMOVE) | `URP` (via MOVEC) | `URP` (via MOVEC) |

---

## Key Registers

### 68030

```
TC  — Translation Control
    Bit 31: E (enable)
    Bits 30–28: SRE, FCL (function code lookup)
    Bits 27–24: PS (page size)
    Bits 23–20: IS (initial shift)
    Bits 19–16: TIA (table index A bits)
    ...

TT0, TT1 — Transparent Translation Registers
    Bit 15: E (enable)
    Bits 31–24: Logical address base
    Bits 23–16: Logical address mask
    Bits 2–0: Function code

CRP — CPU Root Pointer (64-bit)
SRP — Supervisor Root Pointer (64-bit)
```

### 68040/060

```
TC  — Translation Control (MOVEC accessible)
    Bit 15: E (enable translation)
    Bit 14: P (page size: 0=4K, 1=8K)

DTT0, DTT1 — Data Transparent Translation
ITT0, ITT1 — Instruction Transparent Translation
    Same format: base/mask/enable/cache-mode

URP — User Root Pointer (32-bit, MOVEC)
SRP — Supervisor Root Pointer (32-bit, MOVEC)
```

---

## Page Table Entry Format (68040/060)

```
31          12  11  10  9  8  7  6  5  4  3  2  1  0
┌──────────────┬───┬───┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
│ Physical Addr│ U1│ U0│ S│CM1│CM0│ M│ U│ W│  UDT  │
└──────────────┴───┴───┴──┴──┴──┴──┴──┴──┴──┴──┴──┘

UDT: 00=invalid, 01=page descriptor, 10=valid4byte, 11=valid8byte
W:   write-protected
U:   used (accessed)
M:   modified (dirty)
CM:  cache mode (00=cacheable/writethrough, 01=cacheable/copyback,
     10=noncacheable/serialized, 11=noncacheable)
S:   supervisor only
```

---

## mmu.library (Third-Party)

Several third-party `mmu.library` implementations exist:

| Library | Author | Description |
|---|---|---|
| `mmu.library` (MuLib) | Thomas Richter | The standard; used by MuForce, MuGuard, VMM |
| `68040mmu.library` | Phase5 | Basic 040 MMU setup for CyberStorm |

### MuLib API (Key Functions)

```c
struct Library *MMUBase = OpenLibrary("mmu.library", 46);

/* Get current MMU context: */
struct MMUContext *ctx = CurrentContext(MMUBase);

/* Get page properties: */
ULONG props = GetPageProperties(ctx, address);

/* Set page properties: */
SetPageProperties(ctx, address, length,
    MAPP_READABLE | MAPP_WRITABLE,  /* what to set */
    ~0UL                              /* mask */
);

/* Remap a virtual page to a different physical address: */
RemapPage(ctx, virtualAddr, physicalAddr, properties);

/* Flush TLB: */
RebuildTree(ctx);  /* rebuild MMU tables and flush */
```

### Property Flags

```c
#define MAPP_READABLE       (1<<0)
#define MAPP_WRITABLE       (1<<1)
#define MAPP_EXECUTABLE     (1<<2)
#define MAPP_CACHEABLE      (1<<3)
#define MAPP_COPYBACK       (1<<4)
#define MAPP_SUPERVISORONLY (1<<5)
#define MAPP_USERPAGE0      (1<<6)
#define MAPP_USERPAGE1      (1<<7)
#define MAPP_GLOBAL         (1<<8)
#define MAPP_BLANK          (1<<9)   /* invalid/unmapped */
#define MAPP_SWAPPED        (1<<10)  /* paged out to disk */
#define MAPP_TRANSLATED     (1<<11)  /* virtual ≠ physical */
```

---

## Enforcer — How It Uses MMU

Enforcer maps address `$000000–$0003FF` (low memory) and `$00C00000+` (unassigned ranges) as **invalid pages**. Any access to these causes an MMU exception that Enforcer catches, logs, and allows the program to continue:

```
ENFORCER HIT: 00000000 READ  by task "BadApp" at 0002045A
```

---

## VMM — Virtual Memory

VMM (Virtual Memory Manager) uses the MMU to implement demand-paged virtual memory:
1. Maps physical RAM pages into the address space
2. When RAM is full, pages least-recently-used blocks to a swap file on disk
3. On access to a swapped-out page → MMU exception → VMM reads page back from disk
4. Transparent to applications — they see continuous RAM

---

## Direct MMU Programming (No Library)

```asm
; 68040: Enable MMU with 4K pages
    ; Set up page tables at PAGE_TABLE_BASE...
    movec.l  PAGE_TABLE_BASE,urp    ; set User Root Pointer
    movec.l  PAGE_TABLE_BASE,srp    ; set Supervisor Root Pointer
    move.l   #$8000,d0              ; TC: E=1, P=0 (4K pages)
    movec.l  d0,tc                  ; enable translation!
    pflusha                          ; flush all TLB entries

; 68040: Set transparent translation (map $00000000–$00FFFFFF 1:1)
    move.l   #$00FFE040,d0          ; base=$00, mask=$FF, E=1, CM=writethrough
    movec.l  d0,dtt0                ; data transparent translation 0
    movec.l  d0,itt0                ; instruction transparent translation 0
```

---

## References

- Motorola: *MC68030 User's Manual* — MMU chapter
- Motorola: *MC68040 User's Manual* — MMU chapter
- Motorola: *MC68060 User's Manual* — MMU chapter
- Thomas Richter: MuLib documentation (Aminet: `util/libs/MMULib.lha`)
- Enforcer source (public domain)
