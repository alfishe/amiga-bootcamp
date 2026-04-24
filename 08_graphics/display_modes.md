[← Home](../README.md) · [Graphics](README.md)

# Display Modes — Chipset Generations, ModeID, and Timing

## Overview

The Amiga's display system evolved through three generations of custom chips: **OCS** (Original Chip Set, A1000/A500/A2000), **ECS** (Enhanced, A3000/A600), and **AGA** (Advanced Graphics Architecture, A1200/A4000). Each generation expanded resolution, colour depth, and display flexibility while maintaining backward compatibility.

OS 3.0+ provides a **display database** that abstracts these capabilities. Applications query available modes by `ModeID` rather than hardcoding chipset-specific flags.

---

## Chipset Comparison

| Feature | OCS (Agnus/Denise) | ECS (Fat Agnus/Super Denise) | AGA (Alice/Lisa) |
|---|---|---|---|
| **Max Chip RAM** | 512 KB (8372) / 1 MB (8372A) | 2 MB (8375) | 2 MB (8374) |
| **Bitplanes** | 6 (32 colours, lowres) | 6 | 8 (256 colours) |
| **Palette entries** | 32 (4096 total, 12-bit RGB) | 32 (4096) | 256 (16.7M, 24-bit RGB) |
| **Max lowres** | 320×256 (PAL) | 320×256 | 320×256 |
| **Max hires** | 640×256 | 640×256 | 640×256 |
| **Super hires** | — | 1280×256 | 1280×256 |
| **Scan-doubled** | — | — | 640×512 non-interlaced |
| **HAM** | HAM6 (4096 colours) | HAM6 | HAM8 (262,144 colours) |
| **EHB** | EHB (64 colours) | EHB | EHB (superseded by 8 planes) |
| **Sprites** | 8 × 16px × 3 colours | 8 × 16px × 3 colours | 8 × 16/32/64px × 3/15 colours |
| **Fetch modes** | 1× | 1× | 1×, 2×, 4× (wider data bus) |
| **Bandwidth** | 3.58 MHz pixel clock | 3.58/7.16/14.32 MHz | Up to 28.64 MHz (4× fetch) |

---

## Display Timing Fundamentals

All Amiga display modes are based on PAL or NTSC television timing:

### PAL (Europe, Australia)

```
Line frequency:     15,625 Hz
Frame frequency:    50 Hz (25 Hz interlaced)
Lines per frame:    312.5 (625 interlaced)
Active lines:       ~256 (non-interlaced) / ~512 (interlaced)
Colour clock:       3,546,895 Hz
Pixel clock (lores): 7,093,790 Hz (1 pixel = 2 colour clocks)
Pixel clock (hires): 14,187,580 Hz
```

### NTSC (Americas, Japan)

```
Line frequency:     15,734 Hz
Frame frequency:    60 Hz (30 Hz interlaced)
Lines per frame:    262.5 (525 interlaced)
Active lines:       ~200 (non-interlaced) / ~400 (interlaced)
Colour clock:       3,579,545 Hz
Pixel clock (lores): 7,159,090 Hz
Pixel clock (hires): 14,318,180 Hz
```

### Display Cycle Anatomy

```
                    ←── Horizontal line (~64 µs PAL) ──→
┌───────────────────────────────────────────────────────────┐
│ HSYNC │ Left  │       Active Display Area        │ Right │
│       │Border │ (bitplane DMA + sprite DMA)      │Border │
│ ~4.7µs│       │                                  │       │
└───────────────────────────────────────────────────────────┘

Vertical:
  ┌── VSYNC (2.5 lines) ──┐
  │   Top Border           │
  │   Active Display       │ ← 256 lines (PAL) / 200 (NTSC)
  │   Bottom Border        │
  └────────────────────────┘
```

> **FPGA implication**: the MiSTer core must replicate these exact timings for correct DMA slot allocation. Many programs (especially demos) count DMA cycles and will break if timing is even slightly off.

---

## ModeID Format

A ModeID is a 32-bit value encoding the monitor driver and mode:

```
┌──────────────────────────────────────────────┐
│ 31       16 │ 15              0              │
│  Monitor ID │  Mode within monitor           │
└──────────────────────────────────────────────┘
```

### Standard Mode IDs

| ModeID | Name | Resolution | Depth | Chipset |
|---|---|---|---|---|
| `$00000000` | PAL:LORES | 320×256 | 5 | OCS+ |
| `$00008000` | PAL:HIRES | 640×256 | 4 | OCS+ |
| `$00000004` | PAL:LORES-LACE | 320×512 | 5 | OCS+ |
| `$00008004` | PAL:HIRES-LACE | 640×512 | 4 | OCS+ |
| `$00080000` | PAL:SUPERHIRES | 1280×256 | 2 | ECS+ |
| `$00080004` | PAL:SUPERHIRES-LACE | 1280×512 | 2 | ECS+ |
| `$00039000` | DBLPAL:LORES | 320×256 | 8 | AGA |
| `$00039004` | DBLPAL:HIRES | 640×256 | 8 | AGA |
| `$00039024` | DBLPAL:HIRES-LACE | 640×512 | 8 | AGA |
| `$00011000` | DBLNTSC:LORES | 320×200 | 8 | AGA |
| `$00011004` | DBLNTSC:HIRES | 640×200 | 8 | AGA |
| `$00000800` | HAM | 320×256 HAM6 | 6 | OCS+ |
| `$00000080` | EHB | 320×256 EHB | 6 | OCS+ |

### Mode Flags (bits within ModeID)

| Bit | Mask | Meaning |
|---|---|---|
| 2 | `$0004` | LACE — interlaced (double vertical resolution) |
| 11 | `$0800` | HAM — Hold-And-Modify mode |
| 7 | `$0080` | EHB — Extra Half-Brite mode |
| 15 | `$8000` | HIRES — double horizontal resolution |
| 19 | `$80000` | SUPERHIRES — quadruple horizontal resolution (ECS+) |

---

## AGA Fetch Modes

AGA introduced wider data fetch widths, reducing DMA overhead:

| Fetch Mode | Bits per Fetch | FMODE Value | Effect |
|---|---|---|---|
| 1× | 16 bits | 0 | OCS compatible — 1 word per slot |
| 2× | 32 bits | 1 | 2 words per slot — more bandwidth for deeper modes |
| 4× | 64 bits | 3 | 4 words per slot — required for 8-plane hires |

```c
/* Set AGA fetch mode (custom register): */
custom->fmode = 3;  /* 4× fetch — maximum bandwidth */
```

> [!WARNING]
> 4× fetch mode causes 64-pixel horizontal alignment constraints. Sprites also widen to 32 or 64 pixels in 2×/4× mode. Many OCS-era programs break if FMODE ≠ 0.

---

## Querying the Display Database

```c
/* graphics.library 39+ — enumerate all available modes: */
ULONG modeID = INVALID_ID;
struct DisplayInfo di;
struct DimensionInfo dims;
struct MonitorInfo mon;

while ((modeID = NextDisplayInfo(modeID)) != INVALID_ID)
{
    if (GetDisplayInfoData(NULL, (UBYTE *)&di, sizeof(di),
                           DTAG_DISP, modeID))
    {
        if (di.NotAvailable) continue;  /* skip unavailable modes */

        GetDisplayInfoData(NULL, (UBYTE *)&dims, sizeof(dims),
                           DTAG_DIMS, modeID);
        GetDisplayInfoData(NULL, (UBYTE *)&mon, sizeof(mon),
                           DTAG_MNTR, modeID);

        Printf("$%08lx: %ldx%ld, %ld colours, %s\n",
                modeID,
                dims.Nominal.MaxX - dims.Nominal.MinX + 1,
                dims.Nominal.MaxY - dims.Nominal.MinY + 1,
                1L << dims.MaxDepth,
                mon.Mspc->ms_Node.xln_Name);
    }
}
```

### Best Mode Selection

```c
/* Find the best mode matching desired specs: */
ULONG bestMode = BestModeID(
    BIDTAG_NominalWidth,  640,
    BIDTAG_NominalHeight, 480,
    BIDTAG_Depth,         8,
    BIDTAG_MonitorID,     PAL_MONITOR_ID,
    TAG_DONE);

if (bestMode != INVALID_ID)
    Printf("Best mode: $%08lx\n", bestMode);
```

---

## DMA Slot Budget

The display system shares DMA bandwidth with other custom chips. Each scanline has a fixed number of DMA slots:

| DMA Consumer | Slots Used |
|---|---|
| Disk DMA | 3 words |
| Audio (4 channels) | 4 words |
| Sprites (8) | 16 words |
| Bitplane (lowres, 5 planes) | 40 words |
| Bitplane (hires, 4 planes) | 80 words |
| Copper | 1 per instruction pair |
| Blitter | Variable (steals from CPU) |
| CPU | Whatever is left |

> In high-resolution 4-plane mode, bitplane DMA alone consumes 80 words per line — nearly the entire available bandwidth. This is why OCS/ECS hires is limited to 4 planes (16 colours) and AGA needed wider fetch modes.

---

## References

- NDK39: `graphics/displayinfo.h`, `graphics/modeid.h`, `graphics/gfxbase.h`
- HRM: *Amiga Hardware Reference Manual* — Display chapters
- ADCD 2.1: `NextDisplayInfo`, `GetDisplayInfoData`, `BestModeIDA`
- See also: [views.md](views.md) — ViewPort and View construction
- See also: [copper.md](copper.md) — Copper display list programming
- See also: [ham_ehb_modes.md](ham_ehb_modes.md) — special display modes
