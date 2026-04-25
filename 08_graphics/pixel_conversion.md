[← Home](../README.md) · [Graphics](README.md)

# Pixel Format Conversion — Chunky ↔ Planar and Beyond

## The Core Problem

Every Amiga programmer eventually hits the same wall: the custom chipset displays graphics in **planar** format, but nearly every interesting algorithm — 3D rendering, texture mapping, image decompression, PC game ports — produces output in **chunky** format. Converting between these two layouts is the single most CPU-intensive bottleneck in Amiga graphics programming.

This article covers:
1. **What** planar and chunky formats are, mathematically
2. **Why** the conversion is expensive
3. **How** every known solution works — from naive loops to the Kalms butterfly
4. **Where** this problem appears in broader computing (SoA/AoS, GPU swizzle, SIMD)

> [!NOTE]
> The Akiko hardware article covers the CD32's dedicated C2P register interface. This article covers the *algorithm theory* that applies to every Amiga model, and the broader data-layout concepts that connect the Amiga to modern computing.
>
> See: [Akiko — CD32 C2P Hardware](../01_hardware/aga_a1200_a4000/akiko_cd32.md)

---

## Planar vs Chunky — The Two Layouts

### Chunky (Packed Pixel)

Every pixel's complete colour index is stored contiguously. For 8-bit (256 colour) pixels:

```
Address:  $0000  $0001  $0002  $0003  $0004  $0005  $0006  $0007
Data:       $0D    $05    $1B    $0A    $FF    $03    $42    $7E
          pixel0 pixel1 pixel2 pixel3 pixel4 pixel5 pixel6 pixel7
```

Each byte = one pixel. Linear, simple, cache-friendly for rendering. This is how **every modern GPU**, every PC VGA card, every framebuffer since 1990 stores pixels.

### Planar (Bitplane)

Each pixel's colour index is **split across N separate memory regions** (bitplanes). For 8-bit pixels (8 bitplanes), each bitplane stores one bit of every pixel:

```
Bitplane 0: 1 0 1 1 0 0 1 0  ← bit 0 of pixels 0–7
Bitplane 1: 0 1 0 1 1 0 0 1  ← bit 1 of pixels 0–7
Bitplane 2: 1 1 0 0 0 1 1 0  ← bit 2
Bitplane 3: 0 1 1 0 1 1 0 0  ← bit 3
Bitplane 4: 1 0 1 0 1 0 0 1  ← bit 4
Bitplane 5: 1 0 0 0 0 0 1 0  ← bit 5
Bitplane 6: 0 0 1 0 0 0 0 1  ← bit 6
Bitplane 7: 0 0 0 0 1 0 1 0  ← bit 7
```

To read pixel 0's colour: collect bit 0 from each of the 8 planes → `10101100` = `$AC`. The 8 planes are **not interleaved** in standard Amiga layout — each is a separate contiguous memory block.

### Why the Amiga Uses Planar

The planar format was a brilliant engineering choice in 1985:

| Advantage | Explanation |
|---|---|
| **Bandwidth efficiency** | A 4-colour screen uses 2 bitplanes = ½ the memory bandwidth of 4bpp chunky. DMA fetches only the planes actually used. |
| **Scalable colour depth** | Adding a bitplane doubles the colour count without redesigning the display engine. OCS: 1–6 planes. AGA: 1–8 planes. |
| **Cheap colour cycling** | Rotating palette indices only requires changing colour registers — zero memory writes. |
| **Blitter efficiency** | Blitting a masked sprite at 4 colours touches only 2 planes (2 blits), not 4× the data. |
| **Copper integration** | The Copper can change palette registers mid-scanline, effectively multiplying colours without more bitplanes. |

The downside only became critical as rendering algorithms evolved past 2D sprites into 3D, texture mapping, and pixel-level effects that naturally produce chunky output.

---

## The Conversion — Mathematically

C2P is a **bit matrix transposition**. Given 32 chunky pixels (each 8 bits wide), you have a 32×8 bit matrix (32 rows × 8 columns). C2P transposes this to an 8×32 matrix (8 bitplanes × 32 bits each):

```
  Input (chunky):                    Output (planar):
    32 pixels × 8 bits                 8 bitplanes × 32 bits
  ┌──────────────────────────────┐  ┌────────────────────────────────────────┐
  │ P0:  b7 b6 b5 b4 b3 b2 b1 b0 │  │ Plane 0: p0.b0 p1.b0 p2.b0 ... p31.b0  │
  │ P1:  b7 b6 b5 b4 b3 b2 b1 b0 │  │ Plane 1: p0.b1 p1.b1 p2.b1 ... p31.b1  │
  │ ...                          │  │ ...                                    │
  │ P31: b7 b6 b5 b4 b3 b2 b1 b0 │  │ Plane 7: p0.b7 p1.b7 p2.b7 ... p31.b7  │
  └──────────────────────────────┘  └────────────────────────────────────────┘
```

This is equivalent to a 90° bit rotation. On a modern CPU with SIMD, this is trivial. On a 68020 with 8 data registers and no bit-parallel instructions, it is an algorithmic challenge that consumed thousands of programmer-hours across the demoscene.

---

## Solution 1 — The Naive Loop

The simplest approach: iterate over every pixel, extract each bit, and set it in the corresponding bitplane.

```c
/* Naive C2P — educational only, never use in production */
void c2p_naive(UBYTE *chunky, UBYTE *planes[8], int width, int height)
{
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            UBYTE pixel = chunky[y * width + x];
            int byte_offset = y * (width / 8) + (x / 8);
            int bit_position = 7 - (x & 7);

            for (int plane = 0; plane < 8; plane++)
            {
                if (pixel & (1 << plane))
                    planes[plane][byte_offset] |= (1 << bit_position);
                else
                    planes[plane][byte_offset] &= ~(1 << bit_position);
            }
        }
    }
}
```

**Performance:** ~200+ cycles per pixel on 68020. For 320×256 = 81,920 pixels → **~16 million cycles → ~1.1 seconds at 14 MHz**. This gives roughly **0.9 FPS**. Completely unusable.

**Why it's terrible:**
- One bit at a time — no parallelism
- Read-modify-write on every bitplane byte (bus-killing)
- No register reuse — constant memory traffic
- Branch on every bit (pipeline flush on 68020)

---

## Solution 2 — The Merge (Butterfly) Algorithm

This is the standard approach used by virtually all serious Amiga C2P routines. Invented independently by several demoscene coders and formalised by **Mikael Kalms** (Kalmalyzer) and others.

### The Key Insight

Instead of processing one pixel at a time, load **32 pixels** (8 longwords = 256 bits) into CPU registers and perform a series of **bit-level swap operations** (called "merges") that progressively rearrange the bits into planar order. Each merge pass swaps bits at a different granularity: 16-bit blocks, then 8-bit, then 4-bit, 2-bit, and 1-bit.

This is exactly a **butterfly network** — the same structure used in the FFT (Fast Fourier Transform) and Batcher's bitonic sort.

### The Merge Primitive

The fundamental building block is a 2-register swap that exchanges bits at a given stride:

```asm
; merge(d0, d1, mask, shift)
; Exchanges bits between d0 and d1 where mask selects which bits to swap
; and shift determines the stride

    move.l  d0, d2          ; temp = a
    lsr.l   #shift, d2      ; temp >>= stride
    eor.l   d1, d2          ; temp ^= b
    and.l   #mask, d2       ; temp &= mask (select bits to swap)
    eor.l   d2, d1          ; b ^= temp (swap into b)
    lsl.l   #shift, d2      ; temp <<= stride (restore position)
    eor.l   d2, d0          ; a ^= temp (swap into a)
```

**7 instructions** per merge. Each merge moves half the bits in two registers to their correct positions.

### Pass Structure for 8 Bitplanes

A full 8-bitplane C2P conversion on 32 pixels requires **5 passes** of merge operations:

| Pass | Block Size | Mask | Swap Distance | Effect |
|---|---|---|---|---|
| 1 | 16-bit | `$0000FFFF` | 16 | Swap upper/lower halves of longword pairs |
| 2 | 8-bit | `$00FF00FF` | 8 | Swap bytes within pairs |
| 3 | 4-bit | `$0F0F0F0F` | 4 | Swap nibbles |
| 4 | 2-bit | `$33333333` | 2 | Swap bit-pairs |
| 5 | 1-bit | `$55555555` | 1 | Swap individual bits |

After all 5 passes, the 8 data registers contain one longword per bitplane.

### Full 8-Bitplane C2P Inner Loop

```asm
; Kalms-style C2P inner loop — converts 32 chunky pixels (8 longwords)
; to 8 planar longwords (one per bitplane)
;
; Input:  d0-d7 = 8 longwords of chunky data (4 pixels each)
; Output: d0-d7 = 8 longwords of planar data (one per bitplane)

; ---- Pass 1: 16-bit swap ----
    swap    d0              ; exchange upper/lower words of d0
    swap    d1
    swap    d2
    swap    d3
    ; (merge d0,d4), (merge d1,d5), (merge d2,d6), (merge d3,d7)
    ; using mask $0000FFFF, shift 16

    move.l  d0, a3          ; temp save
    move.l  d4, d0
    move.w  a3, d0          ; d0 = d4.hi : d0.lo
    move.w  d4, a3          ; a3 = d0.hi : d4.lo
    move.l  a3, d4

    move.l  d1, a3
    move.l  d5, d1
    move.w  a3, d1
    move.w  d5, a3
    move.l  a3, d5

    move.l  d2, a3
    move.l  d6, d2
    move.w  a3, d2
    move.w  d6, a3
    move.l  a3, d6

    move.l  d3, a3
    move.l  d7, d3
    move.w  a3, d3
    move.w  d7, a3
    move.l  a3, d7

; ---- Pass 2: 8-bit swap ----
; mask = $00FF00FF, shift = 8
    move.l  #$00FF00FF, a3
    ; merge(d0, d2)
    move.l  d0, a4
    lsr.l   #8, a4
    eor.l   d2, a4
    and.l   a3, a4
    eor.l   a4, d2
    lsl.l   #8, a4
    eor.l   a4, d0
    ; merge(d1, d3) ... merge(d4, d6) ... merge(d5, d7) ...
    ; (same pattern repeated for each pair)

; ---- Pass 3: 4-bit swap ----
; mask = $0F0F0F0F, shift = 4
    ; merge(d0, d1), merge(d2, d3), merge(d4, d5), merge(d6, d7)

; ---- Pass 4: 2-bit swap ----
; mask = $33333333, shift = 2

; ---- Pass 5: 1-bit swap ----
; mask = $55555555, shift = 1

; Result: d0 = bitplane 0 (32 bits), d1 = bitplane 1, ... d7 = bitplane 7
```

> [!NOTE]
> The above is a pedagogical skeleton. Production C2P routines are **heavily unrolled** and use every register trick available — address registers as temporary storage, interleaving loads with merges to hide memory latency, and sometimes splitting the conversion across two phases to overlap with Chip RAM writes.

### Performance

| Metric | Naive | Merge/Butterfly | Improvement |
|---|---|---|---|
| Instructions per 32 pixels | ~6,400+ | ~160–200 | **32–40×** |
| Cycles per pixel (68020 @ 14 MHz) | ~200 | ~5–7 | **~30×** |
| 320×256 full frame | ~1.1 s | ~35 ms | **~30× (28 FPS)** |
| 320×256 per frame budget | 0.9 FPS | **28 FPS** | Playable |

---

## Solution 3 — Akiko Hardware C2P (CD32 Only)

The CD32's Akiko chip implements C2P in dedicated silicon. The CPU feeds 8 longwords of chunky data to register `$B80030` and reads back 8 longwords of planar data from the same address.

| Metric | Software C2P (68020) | Akiko |
|---|---|---|
| Method | CPU merge/butterfly | Hardware register pipeline |
| Throughput | ~1.5 MB/s | ~1.5 MB/s |
| CPU cost | 100% | ~50% (register I/O) |
| Availability | All Amigas | **CD32 only** |

Akiko's throughput is approximately the same as optimised software C2P on the 68020 because both are limited by the Chip RAM bus bandwidth (~3.5 MB/s shared). On faster CPUs (68040/060), software C2P **outperforms** Akiko because the CPU can process data faster than the register interface can shuttle it.

Full Akiko protocol: [Akiko — CD32 C2P Hardware](../01_hardware/aga_a1200_a4000/akiko_cd32.md#chunky-to-planar-c2p-conversion)

---

## Solution 4 — Blitter-Assisted C2P

The Blitter can be used as part of a C2P pipeline, but it cannot perform the transposition itself. Typical usage:

1. CPU performs the merge/butterfly in registers → outputs planar longwords to a temporary buffer in Chip RAM
2. Blitter copies the planar data from the temporary buffer to the screen's bitplanes with correct modulo

This approach **overlaps** CPU computation with Blitter DMA — while the Blitter writes frame N's planes to the screen, the CPU computes frame N+1's transposition.

```
Time ──────────────────────────────────────────────────────→
CPU:   [merge frame 0] [merge frame 1] [merge frame 2] ...
Blitter:               [write frame 0] [write frame 1] ...
                       ↑ overlap: CPU and Blitter run in parallel
```

> [!WARNING]
> On 68040/060 systems, the Blitter is often **slower** than letting the CPU do both the merge and the writes via `MOVE16` (68040) or unrolled `MOVEM.L`. The Blitter's 16-bit bus (even in AGA FMODE×4) adds DMA contention that may actually slow down the CPU's merge passes.

---

## Solution 5 — WriteChunkyPixels (AmigaOS)

AmigaOS 3.0+ provides `WriteChunkyPixels()` in `graphics.library`, which performs C2P conversion internally using the best available method:

```c
#include <graphics/gfx.h>

WriteChunkyPixels(rp,
    xstart, ystart, xstop, ystop,
    chunky_buffer, chunky_bytes_per_row);
```

On CD32, this function auto-detects Akiko and uses it. On other AGA machines, it uses an internal software C2P. However, the OS implementation is **not** as fast as the best demoscene routines — it prioritises correctness and generality over raw speed.

---

## Solution 6 — RTG: Eliminating C2P Entirely

The ultimate solution to C2P is to **not do it at all**. Retargetable Graphics (RTG) cards like the Picasso IV, CyberVision 64, and MiSTer's virtual `uaegfx` provide a chunky framebuffer directly. The rendering engine writes chunky pixels to VRAM, and the card's RAMDAC/scaler converts them to video output.

The irony: RTG cards must perform the **reverse** conversion (P2C — planar-to-chunky) when legacy planar software runs on an RTG screen. The CyberVision 64 included a dedicated **Roxxler** chip for this. Without hardware help, P2C on software is equally expensive.

See: [RTG — Retargetable Graphics](../16_driver_development/rtg_driver.md#planar-to-chunky-conversion-c2p)

---

## Choosing the Right Approach

| Platform | Recommended C2P | Why |
|---|---|---|
| A500/A2000 (68000) | Merge algorithm (simplified, fewer planes) | No fast multiply; 68000 can manage 4–5 plane C2P at ~15 FPS |
| A1200 (68020) | Kalms merge, 5-pass | Sweet spot: enough registers, usable I-cache |
| CD32 (68020 + Akiko) | Akiko hardware | Frees ~50% CPU for game logic |
| A4000 (68030/040) | CPU merge (skip Akiko if not CD32) | 68040 `MOVE16` makes CPU writes fast enough |
| 68060 accelerated | CPU merge, no Blitter | 68060 superscalar outperforms everything else |
| MiSTer FPGA | RTG (`uaegfx`) | Chunky framebuffer in DDR — no C2P needed |

---

## The Bigger Picture — Data Layout Transformation

C2P is not unique to the Amiga. It is an instance of a fundamental problem in computer architecture: **transforming data layout between Structure-of-Arrays (SoA) and Array-of-Structures (AoS)**.

### SoA vs AoS — The Universal Duality

```
AoS (Array of Structures) = Chunky:
  struct Pixel { r, g, b, a; };
  Pixel pixels[1024];
  // Memory: r0 g0 b0 a0 r1 g1 b1 a1 r2 g2 b2 a2 ...
  // Each element's fields are contiguous

SoA (Structure of Arrays) = Planar:
  struct Pixels {
    float r[1024];
    float g[1024];
    float b[1024];
    float a[1024];
  };
  // Memory: r0 r1 r2 ... r1023 g0 g1 g2 ... g1023 ...
  // Each field is contiguous across all elements
```

The Amiga's planar format is **SoA**: each bitplane is an array of one field (one bit) across all pixels. The chunky format is **AoS**: each pixel's fields (all 8 bits) are packed together.

### Where This Problem Appears Today

| Domain | SoA (Planar-Like) | AoS (Chunky-Like) | Conversion |
|---|---|---|---|
| **Amiga graphics** | Bitplanes (Agnus DMA) | Chunky pixel buffer (CPU render) | C2P algorithm |
| **GPU compute shaders** | SoA buffer layouts (SSBO) | Vertex attributes (interleaved VBO) | Shader transpose |
| **SIMD / AVX-512** | Separate float arrays (vectorisable) | Struct arrays (gather/scatter) | `_mm512_transpose` intrinsics |
| **Database engines** | Columnar storage (Parquet, Arrow) | Row-oriented storage (MySQL) | Column↔row materialisation |
| **Image compression** | Colour planes (JPEG YCbCr) | RGB pixels (BMP) | MCU block decomposition |
| **GPU texture memory** | Block-compressed (BC/ASTC) | Linear RGBA | Hardware texture unit decode |
| **Neural network inference** | NCHW tensor layout (channels first) | NHWC (channels last) | Layout transposition kernel |

### Why Each System Prefers a Different Layout

| Layout | Optimal For | Reason |
|---|---|---|
| **SoA / Planar** | Streaming one field across many elements | Maximises cache line utilisation, enables SIMD vectorisation |
| **AoS / Chunky** | Random-access to complete elements | All fields of one element in one cache line |

The Amiga's custom DMA engine streams bitplane data to the display sequentially — plane 0 for the whole line, then plane 1, etc. This is a **SoA access pattern**, perfectly matched by the planar layout. The CPU, which wants to set a single pixel's complete colour, has the opposite need — it wants **AoS**.

### Modern Hardware Parallels

| Amiga Component | Modern Equivalent | Function |
|---|---|---|
| **Akiko C2P register** | GPU texture swizzle unit | Hardware layout transposition |
| **Blitter + merge algorithm** | CUDA shared memory transpose kernel | CPU/coprocessor-assisted transpose |
| **RTG (planar bypass)** | Unified chunky framebuffer (since VGA) | Eliminates the problem entirely |
| **Copper palette cycling** | GPU palette shader / LUT texture | Colour manipulation without pixel writes |
| **FMODE (fetch width)** | GPU memory bus width (256/384/512-bit) | Wider bus = more data per DMA cycle |

### GPU Texture Swizzle — The Modern Akiko

Modern GPUs store textures in **swizzled** (Morton/Z-order) layouts rather than linear row-major order. This is architecturally identical to what the Amiga does with planar bitmaps: the hardware's memory access pattern doesn't match the CPU's logical layout, so a dedicated hardware unit transparently converts between them.

```
Linear (CPU view):             Morton/Z-order (GPU internal):
  0  1  2  3                     0  1  4  5
  4  5  6  7          →          2  3  6  7
  8  9 10 11                     8  9 12 13
 12 13 14 15                    10 11 14 15
```

When you call `glTexImage2D()` or `vkCmdCopyBufferToImage()`, the GPU driver performs a layout conversion from linear (CPU-friendly) to swizzled (GPU-cache-friendly). This is the exact same class of operation as Amiga C2P — a hardware-accelerated data layout transformation that is invisible to the application programmer.

---

## Performance Comparison Across Eras

| System | Data Layout Problem | Throughput | Method |
|---|---|---|---|
| A500 (1987, 7 MHz 68000) | C2P 320×256×4bpp | ~2 MB/s | CPU merge, 4 planes |
| A1200 (1992, 14 MHz 68020) | C2P 320×256×8bpp | ~1.5 MB/s | CPU merge, 8 planes |
| CD32 (1993, 14 MHz + Akiko) | C2P 320×256×8bpp | ~1.5 MB/s | Akiko hardware |
| 486 DX2/66 (1992) | No conversion needed | N/A | VGA Mode 13h = chunky |
| Pentium MMX (1997) | Colour space (YUV→RGB) | ~200 MB/s | MMX SIMD |
| GTX 1080 (2016) | Texture swizzle (linear→tiled) | ~300 GB/s | Hardware TMU |
| Apple M2 (2022) | SoA↔AoS for ML tensors | ~100 GB/s | Hardware AMX |

The throughput gap tells the story: what consumed 100% of a 68020's capability is handled by a dedicated hardware unit at 200,000× the bandwidth on modern silicon. But the fundamental problem — **data layout mismatch between producer and consumer** — is identical.

---

## Historical Timeline

| Year | Event |
|---|---|
| 1985 | Amiga launches with planar display. C2P not needed — all software renders directly to bitplanes |
| 1989 | First 3D demos appear (Juggler, etc.). Rendering in chunky buffers starts |
| 1991 | Demoscene coders develop first optimised C2P routines for 68000 |
| 1992 | AGA ships (A1200/A4000). 8 bitplanes = C2P problem gets 2× harder |
| 1993 | CD32 ships with Akiko — first hardware C2P. Mikael Kalms publishes optimised CPU routines |
| 1994 | Kalms C2P library becomes the de facto standard. Multiple variants for 020/030/040/060 |
| 1995 | RTG cards (Picasso II, CyberVision 64) begin to make C2P irrelevant for productivity |
| 1996 | CyberVision 64 ships with Roxxler P2C chip — the reverse problem, solved in hardware |
| 1998 | 68060 accelerators make CPU C2P faster than any hardware solution |
| 2020+ | MiSTer FPGA core implements RTG via `uaegfx` — C2P eliminated for modern setups |

---

## Implementing C2P — Practical Checklist

For developers writing Amiga software that renders in chunky format:

1. **Allocate the chunky buffer in Fast RAM** (`MEMF_FAST`) — the CPU reads it during conversion, and Fast RAM has no DMA contention
2. **Allocate the planar screen in Chip RAM** (`MEMF_CHIP | MEMF_DISPLAYABLE`) — this is mandatory for display DMA
3. **Use a proven C2P library** — Kalms C2P (`kalms-c2p` on GitHub/Aminet) is the gold standard
4. **Match the routine to your CPU** — different unrolling for 68020 vs 68040 vs 68060
5. **Use triple buffering** if possible — render to buffer A, C2P buffer B into Chip RAM, display buffer C
6. **On CD32, detect and use Akiko** — `WriteChunkyPixels()` does this automatically
7. **On RTG systems, skip C2P entirely** — render chunky directly to the RTG card's VRAM
8. **Profile with CIA timers** — the bottleneck shifts between CPU merge and Chip RAM write speed depending on configuration

### Adaptive Detection

```c
#include <graphics/gfxbase.h>
#include <cybergraphx/cybergraphics.h>

extern struct GfxBase *GfxBase;

/* Determine best C2P strategy for current hardware */
enum C2P_Strategy determine_c2p_strategy(struct BitMap *screen_bm)
{
    /* Check for RTG screen first — no C2P needed */
    if (GetCyberMapAttr(screen_bm, CYBRMATTR_ISRTG))
        return C2P_NONE_RTG;

    /* Check for Akiko (CD32) */
    if (GfxBase->ChunkyToPlanarPtr != NULL)
        return C2P_AKIKO;

    /* Check CPU type for best software routine */
    UWORD attn = SysBase->AttnFlags;
    if (attn & AFF_68060) return C2P_KALMS_060;
    if (attn & AFF_68040) return C2P_KALMS_040;
    if (attn & AFF_68020) return C2P_KALMS_020;

    return C2P_KALMS_000;  /* 68000 fallback */
}
```

---

## References

- Mikael Kalms — [kalms-c2p](https://github.com/Kalmalyzer/kalms-c2p) — the definitive C2P library (GitHub)
- Scout/Azure — "Chunky 2 Planar Tutorial" — the seminal demoscene document explaining the transposition theory
- *Amiga Hardware Reference Manual* — bitplane DMA, display pipeline
- NDK39: `graphics/gfx.h` — `WriteChunkyPixels()` prototype
- Intel — [Structure of Arrays vs Array of Structures](https://www.intel.com/content/www/us/en/developer/articles/technical/memory-layout-transformations.html) — modern SoA/AoS guide
- NVIDIA — CUDA Programming Guide, "Shared Memory Matrix Transpose" — GPU equivalent of C2P

## See Also

- [Akiko — CD32 C2P Hardware](../01_hardware/aga_a1200_a4000/akiko_cd32.md) — Akiko register protocol
- [BitMap — Planar Layout](bitmap.md) — how Amiga bitmaps are structured in memory
- [Blitter Programming](blitter_programming.md) — Blitter DMA used in Blitter-assisted C2P
- [RTG — Retargetable Graphics](../16_driver_development/rtg_driver.md) — chunky framebuffer cards that eliminate C2P
- [Memory Types](../01_hardware/common/memory_types.md) — Chip vs Fast RAM (critical for C2P buffer placement)
