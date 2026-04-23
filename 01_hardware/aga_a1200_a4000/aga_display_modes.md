[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Display Modes

## Overview

AGA introduces several new display modes and extends existing ones, enabled via the OS **screenmode** system (`graphics/modeid.h`) and `OpenScreenTags()`.

## Mode ID System

AmigaOS uses 32-bit **ModeIDs** to identify display modes. The format is:
```
[Monitor ID (16 bits)] | [Mode flags (16 bits)]
```

Key AGA monitor IDs:
```c
#define PAL_MONITOR_ID      0x00000000
#define NTSC_MONITOR_ID     0x00010000
#define A2024_MONITOR_ID    0x00020000
#define VGA_MONITOR_ID      0x00031000  /* ECS productivity */
#define A2024_10HZ_ID       0x00040000
#define DBLPAL_MONITOR_ID   0x00420000  /* AGA double PAL */
#define DBLNTSC_MONITOR_ID  0x00400000  /* AGA double NTSC */
#define SUPER72_MONITOR_ID  0x00080000
```

Mode flags (lower 16 bits):
```c
#define LORES_KEY    0x0000  /* 320 wide (PAL) */
#define HIRES_KEY    0x8000  /* 640 wide */
#define HAM_KEY      0x0800  /* HAM mode */
#define EXTRAHALFBRITE_KEY 0x0080 /* EHB */
#define LACE_KEY     0x0004  /* interlace */
```

## Standard AGA Modes

| Mode ID | Resolution | Colours | H rate |
|---|---|---|---|
| `PAL_MONITOR_ID \| LORES_KEY` | 320×256 | 256 | 15.6 kHz |
| `PAL_MONITOR_ID \| HIRES_KEY` | 640×256 | 256 | 15.6 kHz |
| `PAL_MONITOR_ID \| HIRES_KEY \| LACE_KEY` | 640×512 | 256 | 15.6 kHz (interlace) |
| `DBLPAL_MONITOR_ID \| LORES_KEY` | 320×512 | 256 | 31.25 kHz |
| `DBLPAL_MONITOR_ID \| HIRES_KEY` | 640×512 | 256 | 31.25 kHz |
| `PAL_MONITOR_ID \| LORES_KEY \| HAM_KEY` | 320×256 | 262,144 (HAM8) | 15.6 kHz |
| `SUPER72_MONITOR_ID \| HIRES_KEY` | 800×600 (approx) | 256 | 28+ kHz |

## Opening an AGA Screen (OS 3.1)

```c
#include <intuition/screens.h>
#include <graphics/modeid.h>
#include <proto/intuition.h>

struct Screen *scr;

/* 256-colour AGA screen, PAL, 320×256 */
scr = OpenScreenTags(NULL,
    SA_DisplayID,  PAL_MONITOR_ID | LORES_KEY,
    SA_Width,      320,
    SA_Height,     256,
    SA_Depth,      8,           /* 8 bitplanes = 256 colours */
    SA_Colors32,   (ULONG)colour_table,  /* LoadRGB32 format */
    SA_Title,      (ULONG)"My AGA Screen",
    SA_Quiet,      TRUE,
    TAG_DONE);
```

## HAM8 Screen

```c
scr = OpenScreenTags(NULL,
    SA_DisplayID,  PAL_MONITOR_ID | LORES_KEY | HAM_KEY,
    SA_Width,      320,
    SA_Height,     256,
    SA_Depth,      8,
    TAG_DONE);
```

> [!NOTE]
> HAM8 screens require 8 bitplanes. The display system automatically programmes BPLCON0 with HAM=1. The first 64 colour registers are used as the HAM8 index palette.

## BestModeID() — Querying Available Modes

```c
#include <proto/graphics.h>

ULONG modeid = BestModeID(
    BIDTAG_NominalWidth,  640,
    BIDTAG_NominalHeight, 512,
    BIDTAG_Depth,         8,
    BIDTAG_MonitorID,     DBLPAL_MONITOR_ID,
    TAG_DONE);

if (modeid == INVALID_ID) {
    /* Requested mode not available */
}
```

## Double Scan Modes (DblPAL / DblNTSC)

`DBLPAL` and `DBLNTSC` modes use AGA's scan doubler to produce non-interlaced 31 kHz output from PAL/NTSC timing:

- DblPAL: 320×512 or 640×512, 31.25 kHz — compatible with VGA monitors
- DblNTSC: 320×400 or 640×400, 31.47 kHz

These require a multisync monitor and AGA chipset. The A1200 can drive a 1084S in scan-doubled mode.

## Super72 Mode

Super72 provides approximately 800×600 resolution at ~28 kHz horizontal:
- Used by some Workbench productivity configurations
- Requires multisync monitor
- Available via `SUPER72_MONITOR_ID`

## References

- NDK39: `graphics/modeid.h` — all monitor and mode ID definitions
- ADCD 2.1: `Libraries_Manual_guide/` — graphics.library OpenScreen
- Autodocs: `BestModeID`, `OpenScreenTags`
- AmigaMail Vol. 2 — AGA display mode programming
