[← Home](../../README.md) · [Hardware](../README.md)

# Memory Types — Chip RAM, Fast RAM, Slow RAM, and the DMA Bus

## Overview

The Amiga's memory architecture is fundamentally different from any other home computer of its era. Rather than treating all RAM as equal, the system divides memory into **distinct classes** based on which hardware can access it. This division exists because the custom chipset (Agnus/Alice, Denise/Lisa, Paula) has its own DMA engine that operates on a dedicated bus — and that bus only reaches certain RAM.

Understanding this distinction is not optional. It determines where screen buffers live, why games run faster with expansion RAM, why the [Blitter](../../08_graphics/blitter_programming.md) can't touch Fast RAM, and why a $50 accelerator card with 8 MB of Fast RAM can feel like a new machine.

> [!WARNING]
> The 68000 is **Big-Endian**. All multi-byte values in memory (pointers, word-sized registers, structure fields) are stored most-significant byte first. Modern developers working with Amiga memory dumps or binary formats will misread data if they assume little-endian layout.

---

## Memory Type Classification

### The Three Types

| Type | Full Name | Who Can Access It? | Speed (Stock A500) | DMA Visible? | Address Range |
|---|---|---|---|---|---|
| **Chip RAM** | Chipset-accessible RAM | CPU + all custom chips (Blitter, Copper, bitplane DMA, sprite DMA, audio DMA, disk DMA) | ~3.5 MHz effective (contended) | ✓ Yes | `$000000`–`$07FFFF` (512 KB) to `$1FFFFF` (2 MB) |
| **Slow RAM** | Pseudo-Fast / Ranger / "Trapdoor" RAM | CPU only — but on the Chip RAM bus | ~3.5 MHz effective (still contended) | ✗ No (not used by DMA) | `$C00000`–`$C7FFFF` (512 KB) |
| **Fast RAM** | True Fast / Zorro / Accelerator RAM | CPU only — on a separate bus | Full CPU speed (7–50+ MHz, no contention) | ✗ No | `$200000`+ (Zorro II) or `$01000000`+ (Zorro III) |

> These address ranges are excerpts — for the complete 24-bit and 32-bit memory maps showing how Chip, Slow, Fast RAM, CIAs, custom chips, ROM, and Autoconfig space interleave, see [address_space.md](address_space.md).

### Why "Slow RAM" Exists

The A500's internal 512 KB expansion (the "trapdoor" board) and the A500 external side-expansion both map to `$C00000`–`$C7FFFF`. This RAM is **on the same bus as Chip RAM**, so it suffers the same DMA contention — the CPU waits whenever the custom chips are using the bus. However, the custom chips **do not** fetch DMA data from this range. It's the worst of both worlds: too slow for CPU work (bus contention), but invisible to DMA (can't be used for screen buffers or audio).

AmigaOS classifies Slow RAM as `MEMF_CHIP` on some models, and some games and demos actually rely on this. The behavior varies by Agnus revision — Fat Agnus (8372) on the A500+ can optionally remap $C00000 into the Chip RAM address space, making it true Chip RAM.

### Why Fast RAM Matters

On a stock A500 with only Chip RAM, the CPU and custom chips compete for every bus cycle. Adding Fast RAM (via Zorro or an accelerator) gives the CPU its own private memory bus:

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│        Chip RAM Bus         │     │       Fast RAM Bus          │
│       (16-bit, 3.58 MHz)    │     │  (16/32-bit, CPU speed)     │
├─────────────────────────────┤     ├─────────────────────────────┤
│ Agnus (DMA master)          │     │ CPU only (no contention)    │
│ ├── Bitplane DMA            │     │                             │
│ ├── Sprite DMA              │     │ Code, stack, data structs   │
│ ├── Copper DMA              │     │ Non-DMA allocations         │
│ ├── Blitter DMA             │     │                             │
│ ├── Audio DMA (Paula)       │     └─────────────────────────────┘
│ ├── Disk DMA                │
│ └── CPU (leftover slots)    │
└─────────────────────────────┘
```

When the CPU executes code from Fast RAM, it runs at full speed while the custom chips simultaneously work Chip RAM. This is why an A500 with a 68020 accelerator + 8 MB Fast RAM feels dramatically faster even though the display hardware hasn't changed.

---

## DMA Accessibility Matrix

This is the critical table. **If a hardware DMA channel needs data, that data must be in Chip RAM.**

| Operation / Consumer | Chip RAM | Slow RAM | Fast RAM | ROM |
|---|---|---|---|---|
| **Bitplane display (Agnus)** | ✓ Required | ✗ | ✗ | ✗ |
| **Sprite data (Agnus)** | ✓ Required | ✗ | ✗ | ✗ |
| **Copper list (Agnus)** | ✓ Required | ✗ | ✗ | ✗ |
| **Blitter source/dest (Agnus)** | ✓ Required | ✗ | ✗ | ✗ |
| **Audio sample data (Paula)** | ✓ Required | ✗ | ✗ | ✗ |
| **Disk DMA buffer (Agnus)** | ✓ Required | ✗ | ✗ | ✗ |
| **CPU code execution** | ✓ Slow (contended) | ✓ Slow (contended) | ✓ Fast (uncontended) | ✓ |
| **CPU data read/write** | ✓ Slow (contended) | ✓ Slow (contended) | ✓ Fast (uncontended) | Read only |
| **68040/060 cache** | ✓ Cacheable | ✓ Cacheable | ✓ Cacheable | ✓ Cacheable |

> [!IMPORTANT]
> There is **no hardware error** when the Blitter, Copper, or other DMA engine is pointed at a Fast RAM address. The DMA engine's address lines simply wrap into the Chip RAM address space, silently reading/writing the wrong location. This is the single most common source of "random corruption" bugs on accelerated Amigas.

---

## AllocMem() Flags

AmigaOS classifies memory through the `MEMF_` flags passed to `AllocMem()`. The kernel maintains a linked list of `MemHeader` structures, one per contiguous memory region:

```c
/* exec/memory.h — NDK39 */
#define MEMF_ANY        0L        /* No preference */
#define MEMF_PUBLIC      (1L<<0)  /* Accessible to all tasks and DMA */
#define MEMF_CHIP        (1L<<1)  /* Custom chip DMA-accessible */
#define MEMF_FAST        (1L<<2)  /* CPU-only, no DMA, no contention */
#define MEMF_LOCAL       (1L<<8)  /* Not mappable (always present) */
#define MEMF_24BITDMA    (1L<<9)  /* Within 24-bit address space */
#define MEMF_CLEAR       (1L<<16) /* Zero-fill before returning */
#define MEMF_REVERSE     (1L<<17) /* Allocate from top of pool */
#define MEMF_LARGEST     (1L<<18) /* Query: return largest free block */
#define MEMF_TOTAL       (1L<<19) /* Query: return total of this type */
#define MEMF_NO_EXPUNGE  (1L<<31) /* V39: don't expunge libraries */
```

### Allocation Priority

When `MEMF_ANY` is used (the default), AmigaOS allocates from the **fastest available** memory first:

1. **Fast RAM** (Zorro III 32-bit > Zorro II 16-bit > accelerator on-board)
2. **Slow RAM** (if classified as `MEMF_PUBLIC`)
3. **Chip RAM** (last resort)

This is why adding Fast RAM instantly speeds up the system — Workbench, libraries, and application code automatically move out of Chip RAM, freeing it for display and audio.

> [!NOTE]
> `MEMF_CHIP` forces allocation from Chip RAM regardless of availability. Use it only when the data must be DMA-visible (screen buffers, audio samples, Copper lists, sprite data). Requesting `MEMF_CHIP` for code or non-DMA data wastes the most constrained resource in the system.

---

## Per-Model Stock Configurations

| Model | Year | CPU | Stock Chip RAM | Max Chip RAM | Stock Fast/Slow RAM | Expansion Slots | Notes |
|---|---|---|---|---|---|---|---|
| **A1000** | 1985 | 68000 @ 7.09 MHz | 256 KB | 512 KB | None | Side expansion | WCS (Writable Control Store) for Kickstart |
| **A500** | 1987 | 68000 @ 7.09 MHz | 512 KB | 1 MB (2 MB with mod) | 512 KB Slow (trapdoor) | Trapdoor + side slot | Most common model |
| **A500+** | 1991 | 68000 @ 7.09 MHz | 1 MB | 2 MB | None stock | Trapdoor + side slot | ECS chipset, Fat Agnus |
| **A2000** | 1987 | 68000 @ 7.09 MHz | 512 KB–1 MB | 2 MB (with Super Agnus) | None stock | 5× Zorro II + CPU slot | Big-box, expandable |
| **A600** | 1992 | 68000 @ 7.09 MHz | 1 MB | 2 MB | None stock | PCMCIA Type II + trapdoor | Smallest desktop |
| **A3000** | 1990 | 68030 @ 25 MHz | 1–2 MB | 2 MB | 4–16 MB Fast (on-board) | 4× Zorro III + CPU slot | 32-bit bus, first Zorro III |
| **A1200** | 1992 | 68EC020 @ 14 MHz | 2 MB | 2 MB | None stock | Trapdoor 150-pin + PCMCIA | AGA chipset |
| **A4000** | 1992 | 68030 @ 25 MHz or 68040 @ 25 MHz | 2 MB | 2 MB | 4–16 MB Fast (on-board) | 5× Zorro III + CPU slot | AGA, big-box |
| **CDTV** | 1991 | 68000 @ 7.09 MHz | 1 MB | 2 MB (Super Agnus mod) | None stock | None (A2000-compatible internal) | OCS, CD-ROM, IR remote, NVRAM |
| **CD32** | 1993 | 68EC020 @ 14 MHz | 2 MB | 2 MB | None stock | FMV slot only (SX-1/SX-32 add-on) | AGA, Akiko C2P, 2× CD-ROM |

### Expansion Capabilities

| Model | Chip RAM Expandable? | Fast RAM Options | Maximum Practical Fast RAM |
|---|---|---|---|
| **A1000** | To 512 KB (internal) | Side expansion only | ~2 MB (rare 3rd-party) |
| **A500** | To 1 MB via trapdoor; 2 MB with Agnus swap | Zorro side expansion, accelerator | 8 MB (accelerator) |
| **A500+** | To 2 MB via trapdoor | Side expansion, accelerator | 8 MB (accelerator) |
| **A2000** | To 2 MB (Super Agnus + RAM) | Zorro II cards, CPU slot accelerator | 8 MB (Zorro II) + 128 MB (accelerator) |
| **A600** | To 2 MB via trapdoor | PCMCIA (up to 4 MB), trapdoor accelerator | 64 MB (accelerator) |
| **A3000** | Fixed 2 MB | On-board (Ramsey), Zorro III cards | 256 MB (Zorro III) |
| **A1200** | Fixed 2 MB | Trapdoor accelerator, PCMCIA (4 MB) | 256 MB (accelerator) |
| **A4000** | Fixed 2 MB | On-board (Ramsey), Zorro III, CPU slot | 256 MB+ (accelerator + Zorro III) |
| **CDTV** | To 2 MB (Super Agnus mod) | None standard; internal A2000-compatible bus | ~2 MB (rare 3rd-party via internal expansion) |
| **CD32** | Fixed 2 MB | SX-1/SX-32 add-on provides trapdoor-style slot | 128 MB (SX-32 + accelerator) |

---

## Third-Party Accelerators and Memory Expansion

Accelerator cards are the primary way to add Fast RAM. They plug into the CPU slot (A2000/A3000/A4000) or the trapdoor connector (A500/A600/A1200) and provide a faster CPU plus private memory:

### Classic (1990s) Accelerators

| Card | For Model | CPU | Max Fast RAM | Bus Width | Other Features |
|---|---|---|---|---|---|
| **GVP A530** | A500 | 68030 @ 40 MHz | 8 MB | 32-bit | SCSI, IDE |
| **Blizzard 1230 Mk IV** | A1200 | 68030 @ 50 MHz | 128 MB (SIMM) | 32-bit | SCSI option |
| **Blizzard 1260** | A1200 | 68060 @ 50 MHz | 128 MB (SIMM) | 32-bit | SCSI option |
| **Warp Engine** | A3000/A4000 | 68040 @ 40 MHz | 128 MB (4×SIMM) | 32-bit | SCSI-2 DMA |
| **CyberStorm Mk III** | A3000/A4000 | 68060 @ 50 MHz | 128 MB (SIMM) | 32-bit | SCSI, Ethernet option |
| **GVP G-Force 040** | A2000 | 68040 @ 33 MHz | 32 MB | 32-bit | SCSI |

### Modern (2020s) Accelerators

| Card | For Model | CPU | Max Fast RAM | Bus Width | Other Features |
|---|---|---|---|---|---|
| **TF536** | A500 | 68030 @ 50 MHz | 64 MB | 32-bit | IDE |
| **TF1260** | A1200 | 68060 @ 50+ MHz | 128 MB | 32-bit | IDE, PCMCIA-friendly |
| **PiStorm** | A500/A2000 | ARM (emulated 68k) | 256 MB+ | Virtual | RTG, network, SD card |
| **PiStorm32** | A1200 | ARM (emulated 68k) | 256 MB+ | Virtual | RTG, network |
| **Vampire V2** | A500/A600 | FPGA (68080) | 128 MB | 32-bit | RTG, HDMI, Ethernet |
| **Vampire V4 SA** | Standalone | FPGA (68080) | 512 MB | 64-bit | Full system, AGA compatible |

> [!NOTE]
> PCMCIA memory cards (A600/A1200) provide up to 4 MB of Fast RAM but are limited to 16-bit Zorro II speed. Some accelerators conflict with the PCMCIA port when mapped above 8 MB — check for "PCMCIA-friendly" jumper settings.

---

## When to Use Each Memory Type

| Scenario | Use | Why |
|---|---|---|
| Screen bitmaps | `MEMF_CHIP` | Bitplane DMA can only read Chip RAM |
| Audio sample buffers | `MEMF_CHIP` | Paula audio DMA can only read Chip RAM |
| Copper lists | `MEMF_CHIP` | Copper DMA can only read Chip RAM |
| Sprite data | `MEMF_CHIP` | Sprite DMA can only read Chip RAM |
| Blitter source/destination | `MEMF_CHIP` | Blitter DMA can only access Chip RAM |
| Application code | `MEMF_ANY` | Let OS pick the fastest available |
| Data structures (non-DMA) | `MEMF_ANY` | No need for DMA visibility |
| Stacks | `MEMF_ANY` | CPU-only |
| Libraries (loaded by LoadSeg) | `MEMF_ANY` | Automatic — exec allocates from fastest |
| Disk I/O buffers (trackdisk) | `MEMF_CHIP` | Disk DMA requires Chip RAM |

---

## Historical Context — Why This Design?

### The 1985 Perspective

When Jay Miner designed the Amiga custom chipset, RAM was expensive ($50+/MB) and bus bandwidth was precious. The split architecture was a deliberate trade-off:

**Pros:**
- Custom chips got dedicated, guaranteed DMA bandwidth — no CPU could starve the display
- The CPU could run from a separate bus (once Fast RAM was added), achieving true parallelism impossible on competitors
- 512 KB of Chip RAM was enough for full-color animation + stereo audio + multitasking — competitors needed 2–4× more RAM for less capability

**Cons:**
- Programmers had to understand which memory type to use — a `malloc()` from C wasn't sufficient
- Chip RAM was the most constrained resource; running out killed the system even with megabytes of Fast RAM available
- The "Slow RAM" compromise ($C00000) confused everyone

### Competitive Comparison (1985–1992)

| Feature | Amiga | Atari ST | Mac 128K/Plus | IBM PC/AT |
|---|---|---|---|---|
| **Memory architecture** | Split: Chip + Fast | Unified | Unified | Unified |
| **DMA coprocessors** | Agnus, Denise, Paula | None (STE added DMA later) | None | None (VGA had limited buffer DMA) |
| **CPU/display parallelism** | Yes (with Fast RAM) | No — CPU shares bus | No — CPU shares bus | Partial (VGA has own buffer) |
| **Memory ceiling (stock)** | 512 KB Chip + expandable | 512 KB–4 MB | 128 KB–4 MB | 256 KB–16 MB |
| **Programmer burden** | High (must track MEMF_ types) | Low (all RAM is equal) | Low | Low |

---

## Modern Analogies

| Amiga Concept | Modern Equivalent | Notes |
|---|---|---|
| Chip RAM | GPU VRAM (Vulkan `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT`) | Memory visible to the graphics/DMA hardware; the CPU can access it but shares bandwidth |
| Fast RAM | System RAM (Vulkan `VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT`) | CPU-only memory; fast, uncontended, but the GPU can't directly DMA from it |
| `MEMF_CHIP` allocation | `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT` allocation | Explicitly requesting DMA-visible memory |
| `MEMF_ANY` allocation | `malloc()` / `new` | Let the runtime pick the best available memory |
| Chip RAM bus contention | PCIe bandwidth sharing | CPU and GPU compete for bus bandwidth; dedicated VRAM avoids this |
| Slow RAM | Shared memory (integrated GPU) | On the same bus as the GPU, but not used by it — the worst of both worlds |
| AllocMem priority order | NUMA-aware allocation | Modern OS allocates from the closest/fastest memory node first |

---

## Pitfalls & Common Mistakes

### Pitfall 1: "The Silent Corruption" — DMA to Fast RAM

```c
/* ✗ BAD: Audio buffer in Fast RAM */
BYTE *sample = AllocMem(44100, MEMF_ANY);  /* May return Fast RAM! */
/* Paula DMA reads from Chip RAM bus — gets garbage */
```

**Why it's bad**: There is no error, no crash, no diagnostic. The DMA controller's address lines don't reach Fast RAM — they wrap into whatever Chip RAM happens to be at the aliased address. You hear random noise instead of your sample. On a stock A500 (Chip RAM only) the same code works perfectly, so the bug only appears on accelerated machines — the exact systems your advanced users have.

```c
/* ✓ GOOD: Audio buffer in Chip RAM */
BYTE *sample = AllocMem(44100, MEMF_CHIP | MEMF_CLEAR);
```

**Why this fixes it**: `MEMF_CHIP` guarantees the allocation comes from DMA-visible memory. The audio hardware can now reach every byte. Using `MEMF_CLEAR` also eliminates audible pops from uninitialized data.

### Pitfall 2: "The Chip RAM Hog" — Wasting Chip RAM on Non-DMA Data

```c
/* ✗ BAD: Allocating code/data in Chip RAM unnecessarily */
struct GameState *state = AllocMem(sizeof(*state), MEMF_CHIP);
```

**Why it's bad**: Chip RAM is the scarcest resource on every Amiga — typically 512 KB to 2 MB. Every byte you waste on non-DMA data is a byte unavailable for screen buffers, audio samples, and Copper lists. On a stock A500 with 512 KB, a game that hogs 100 KB of Chip RAM for its data structures may fail to open a 5-bitplane screen. Even on a 2 MB AGA machine, Chip RAM fills fast: a 320×256×5 double-buffered display already consumes 2×51,200 = 100 KB per bitplane set.

```c
/* ✓ GOOD: Let OS pick fastest memory */
struct GameState *state = AllocMem(sizeof(*state), MEMF_ANY | MEMF_CLEAR);
```

**Why this changes the game**: `MEMF_ANY` lets AmigaOS place the allocation in Fast RAM when available. On an accelerated machine, this frees Chip RAM for display hardware AND runs faster (no DMA contention). On a stock A500 with only Chip RAM, `MEMF_ANY` falls back to Chip RAM automatically — same behavior, zero code changes.

### Pitfall 3: "The Slow RAM Trap" — Assuming $C00000 is Fast

Slow RAM at `$C00000` is on the Chip RAM bus. Code executing from Slow RAM runs at the same contended speed as Chip RAM — it provides **no** performance benefit over Chip RAM for CPU-bound work.

**Why it's bad**: Developers who add a trapdoor expansion to their A500 and see "1 MB" in the early startup menu assume they've doubled their performance. They haven't. The extra 512 KB at `$C00000` shares the same 16-bit bus with the custom chips — every DMA cycle from Agnus steals a cycle from the CPU, exactly as in Chip RAM. The only advantage is that Slow RAM isn't consumed by screen buffers, so it's available for code/data. But it's emphatically not "Fast" — that name is reserved for memory on a separate bus. Moving performance-critical game loops to Slow RAM produces zero speedup vs. Chip RAM.

### Pitfall 4: "The PCMCIA Conflict" — A1200 Memory Above 8 MB

On the A1200, the PCMCIA port maps to `$600000`–`$9FFFFF`. Accelerator cards that place Fast RAM in this range disable the PCMCIA port entirely. Many modern accelerators (TF1260) include a "PCMCIA-friendly" jumper that limits Fast RAM to 4 MB to avoid this.

**Why it matters**: PCMCIA is the A1200's only practical way to add CompactFlash storage or networking without opening the case. Losing it for the sake of 4 extra MB of Fast RAM is a poor trade-off. Always check whether your accelerator has a PCMCIA compatibility mode before assuming full memory is available.

---

## Adaptive Software Behavior

Well-written Amiga software doesn't assume a fixed memory configuration. It detects what's available at runtime and adjusts its behavior:

### Detecting Available Memory

```c
#include <exec/memory.h>

ULONG chipFree = AvailMem(MEMF_CHIP);           /* Free Chip RAM */
ULONG fastFree = AvailMem(MEMF_FAST);           /* Free Fast RAM (0 if none) */
ULONG totalFree = AvailMem(MEMF_ANY);           /* Total free memory */
BOOL  hasFastRAM = (fastFree > 0);              /* Fast RAM present? */
ULONG chipTotal = AvailMem(MEMF_CHIP | MEMF_TOTAL);  /* Total Chip RAM installed */
```

### Strategy: Chip-Only Mode (Stock A500 / A600)

When no Fast RAM is available, everything competes for the same 512 KB–2 MB:

```c
if (!hasFastRAM) {
    /* All memory is Chip RAM — conserve aggressively */
    numBitplanes = 4;               /* Use 16 colours instead of 32 */
    useDoubleBuffer = FALSE;        /* Single buffer saves 40 KB per plane */
    maxBOBs = 8;                    /* Fewer sprites = less Blitter work */
    musicQuality = QUALITY_LOW;     /* 4-bit 11 kHz samples save Chip RAM */
    preloadLevel = FALSE;           /* Stream level data from disk */
}
```

**Why**: On a Chip-only system, the CPU, Blitter, display, and audio all share one bus. Reducing display complexity (fewer bitplanes) frees DMA slots for the Blitter AND frees Chip RAM for audio/game data. This is why many A500 games use 4 bitplanes (16 colours) while the same game on an accelerated A1200 uses 5 or even 8.

### Strategy: Chip + Fast RAM Mode (Accelerated Systems)

When Fast RAM is available, the architecture unlocks true parallelism:

```c
if (hasFastRAM) {
    /* CPU runs from Fast RAM at full speed; Chip RAM for DMA only */
    numBitplanes = 5;                /* 32 colours — display looks better */
    useDoubleBuffer = TRUE;          /* Flicker-free, worth the Chip RAM */
    maxBOBs = 24;                    /* More BOBs — CPU can compute while Blitter blits */
    musicQuality = QUALITY_HIGH;     /* 8-bit 22 kHz — Chip RAM freed by code in Fast RAM */
    preloadLevel = TRUE;             /* Load entire level into Fast RAM — no disk latency */

    /* Allocate non-DMA data from Fast RAM explicitly: */
    level = AllocMem(levelSize, MEMF_FAST | MEMF_CLEAR);
    if (!level)
        level = AllocMem(levelSize, MEMF_ANY | MEMF_CLEAR); /* Fallback */
}
```

**Why this changes everything**: The CPU no longer waits for the Blitter — it computes physics, AI, and input from its own private bus while the Blitter simultaneously processes screen memory. Game loops that took 20 ms on a stock A500 can complete in 8 ms on a 68030 + Fast RAM, not because the CPU is faster (though it often is), but because the CPU and custom chips now run in **parallel** instead of fighting over one bus.

### Graceful Degradation Pattern

The best Amiga software uses a tiered allocation strategy:

```c
/* Try Fast RAM first, fall back to any available: */
void *AllocBest(ULONG size, ULONG flags) {
    void *mem;

    /* For DMA-visible data, always use MEMF_CHIP: */
    if (flags & MEMF_CHIP)
        return AllocMem(size, flags);

    /* Try Fast RAM first (fastest): */
    mem = AllocMem(size, MEMF_FAST | (flags & ~MEMF_FAST));
    if (mem) return mem;

    /* Fall back to any available memory: */
    return AllocMem(size, MEMF_ANY | (flags & ~MEMF_FAST));
}
```

### Real-World Examples

| Software | Chip-Only Behavior | With Fast RAM |
|---|---|---|
| **WHDLoad** | Patches games to run from Chip RAM sandbox | Preloads entire game into Fast RAM, eliminates disk access |
| **Protracker** | Loads samples into Chip RAM, limits module size | Decompresses/mixes in Fast RAM, copies final audio buffers to Chip RAM |
| **Workbench 3.1** | Libraries and windows in Chip RAM (slow) | Libraries auto-load into Fast RAM, only screen buffers use Chip RAM |
| **Doom (Amiga port)** | Won't run — requires Fast RAM for framebuffer conversion | Renders chunky pixels in Fast RAM, c2p converts to Chip RAM bitplanes |
| **ShapeShifter** | Won't run — Mac emulation needs contiguous Fast RAM | Maps Mac address space into Fast RAM, uses Chip RAM only for display output |


---

## Impact on FPGA/Emulation

For MiSTer FPGA core developers, accurate memory type emulation is critical:

- **Address decoding**: Agnus/Alice must correctly decode Chip RAM range (512 KB / 1 MB / 2 MB depending on chip revision) and reject addresses outside it
- **Bus arbitration**: DMA slots must be allocated with correct priority (display > sprite > audio > disk > Copper > Blitter > CPU)
- **Slow RAM behavior**: The $C00000 range must share the Chip RAM bus timing, not run at Fast RAM speed
- **Fat Agnus detection**: Software reads VPOSR (`$DFF004`) bits 14–8 to detect Agnus revision and Chip RAM size — this must return correct values
- **MEMF_CHIP boundary**: The exec memory list must correctly reflect the Chip RAM size so `AvailMem(MEMF_CHIP)` returns the right value
- **Fast RAM emulation**: When emulating accelerators, Fast RAM must be on a separate bus with zero-wait-state access to show the correct performance improvement

---

## Best Practices

1. **Always use `MEMF_CHIP` for DMA-visible data** — screen buffers, audio samples, Copper lists, sprite data, disk buffers
2. **Never use `MEMF_CHIP` for code, stacks, or non-DMA data structures** — it wastes the most constrained memory type
3. **Use `MEMF_ANY` for everything else** — let AmigaOS allocate from the fastest available pool
4. **Check `AvailMem(MEMF_CHIP)` before allocating large Chip RAM blocks** — running out of Chip RAM crashes the display
5. **Test on systems with and without Fast RAM** — many bugs only appear when allocations land in unexpected memory types
6. **Use `TypeOfMem()` to verify** — if you need to confirm a pointer is in Chip RAM, call `TypeOfMem(ptr)` and check for `MEMF_CHIP`

---

## FAQ

**Q: Can I make Slow RAM into Chip RAM?**
A: On machines with Fat Agnus (8372) or Super Agnus (8372A), sometimes. The A500+ and A2000 rev 6+ can remap the Slow RAM range into the Chip RAM address space with a jumper setting, but this requires the correct Agnus revision.

**Q: Why does my game crash on an A3000 but work on an A500?**
A: Likely a `MEMF_ANY` allocation that returns Fast RAM. On the A500 (Chip RAM only), `MEMF_ANY` returns Chip RAM. On the A3000, it returns Fast RAM — and if you pass that pointer to the Blitter or display hardware, you get corruption.

**Q: Does AGA (A1200/A4000) change anything about memory types?**
A: No. AGA (Alice/Lisa) uses the same Chip RAM bus architecture as OCS/ECS. The maximum Chip RAM is still 2 MB. AGA adds wider DMA fetches (64-bit via FMODE) but doesn't change the Chip/Fast RAM split.

**Q: How does WHDLoad handle memory type issues?**
A: WHDLoad patches old games that assume all memory is Chip RAM. It redirects allocations, fixes hardcoded addresses, and provides a Chip RAM "sandbox" so games written for a stock A500 can run on accelerated systems.

---

## References

- NDK 3.9: `exec/memory.h` — MEMF_ flag definitions
- ADCD 2.1 Hardware Manual — memory map chapter
- *Amiga Hardware Reference Manual* 3rd ed. — Chapter 1 (System Overview)
- See also: [address_space.md](address_space.md) — full 24-bit/32-bit address map
- See also: [chip_ram_expansion.md](../ecs_a600_a3000/chip_ram_expansion.md) — 2 MB Chip RAM with Super Agnus
- See also: [zorro_bus.md](zorro_bus.md) — Zorro II/III expansion bus (Fast RAM cards)
- See also: [blitter_programming.md](../../08_graphics/blitter_programming.md) — Blitter DMA (Chip RAM only)
- See also: [exec_memory.md](../../06_exec_os/exec_memory.md) — AmigaOS memory management API
