[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# ECS Productivity & Multiscan Display Modes

## Overview

ECS introduces **BEAMCON0** which allows the Amiga to produce non-standard display timings. The most useful are **productivity mode** (~28 kHz / 31 kHz horizontal) and **multiscan mode**, which provide flicker-free, high-resolution displays compatible with standard SVGA monitors.

These modes are available on A3000 and some A2000/A600 configurations with a multisync monitor.

## Standard OCS Timings (for reference)

| Mode | H rate | V rate | Resolution |
|---|---|---|---|
| PAL LORES | 15.625 kHz | 50 Hz | 320×256 |
| PAL HIRES | 15.625 kHz | 50 Hz | 640×256 |
| NTSC LORES | 15.720 kHz | 60 Hz | 320×200 |
| NTSC HIRES | 15.720 kHz | 60 Hz | 640×200 |
| PAL interlace | 15.625 kHz | 50 Hz (25 Hz/field) | 320×512 / 640×512 |

## ECS Multiscan Modes

| Mode | H rate | V rate | Resolution | BEAMCON0 |
|---|---|---|---|---|
| Productivity | ~28.6 kHz | 57 Hz | 640×480 | $0A00 |
| Super72 | ~28.6 kHz | 72 Hz | 800×600 (approx) | varies |
| DblPAL | 31.25 kHz | 50 Hz | 640×512 | custom |
| DblNTSC | 31.47 kHz | 60 Hz | 640×400 | custom |
| VGA-like | 31.47 kHz | 60 Hz | 640×480 | custom |

## Programming Productivity Mode

Productivity mode on the A3000 (PAL, 640×480):

```asm
; Set BEAMCON0 for variable beam timing
move.w  #$0A00, $DFF1DC    ; VARBEAMEN | VARVSYEN

; Program horizontal total, sync, blank (custom timing)
move.w  #$71, $DFF1C0      ; HTOTAL (horizontal total - 1)
move.w  #$0F, $DFF1C4      ; HSSTRT (H sync start)
move.w  #$19, $DFF1C6      ; HSSTOP (H sync stop)
move.w  #$09, $DFF1C8      ; HBSTRT (H blank start)
move.w  #$71, $DFF1CA      ; HBSTOP (H blank stop)

; Vertical timing
move.w  #$0242, $DFF1E0    ; VTOTAL
move.w  #$0015, $DFF1E6    ; VSSTRT
move.w  #$001D, $DFF1E8    ; VSSTOP
```

> [!NOTE]
> The exact register values depend on the target monitor's sync requirements. The A3000's monitor (1084S or Commodore 1950) has a specific timing window. Always consult the monitor's datasheet.

## OS Support: ScreenModes

AmigaOS 3.1 integrates ECS productivity modes through the **screenmode** system:

```c
#include <graphics/modeid.h>
#include <libraries/asl.h>

/* Open a 640×480 productivity screen */
struct Screen *scr = OpenScreenTags(NULL,
    SA_DisplayID,  PRODDBL_MONITOR_ID | HIRES_KEY,
    SA_Width,      640,
    SA_Height,     480,
    SA_Depth,      4,
    TAG_DONE);
```

**Key mode IDs for ECS:**
```c
#define MULTISCAN_MONITOR_ID  0x00041000  /* multiscan / productivity */
#define SUPER72_MONITOR_ID    0x00081000
#define DBLNTSC_MONITOR_ID    0x00401000
#define DBLPAL_MONITOR_ID     0x00421000
```

These IDs are returned by `BestModeID()` and accepted by `OpenScreen()` / `OpenScreenTags()`.

## Hardware Requirements

- **ECS chipset** (Super Agnus + ECS Denise) — required for BEAMCON0
- **Multisync monitor** — standard 15 kHz PAL/NTSC monitors do not support 31 kHz
- **A3000** — has built-in multiscan support; A2000 requires a separate scan doubler card

## Flicker Fixer (A2000/A500)

Some Zorro II cards (e.g., Flicker Fixer by MicroWay, Indivision ECS) scan-double the 15 kHz signal to 31 kHz for use with VGA monitors. These operate transparently — no BEAMCON0 programming needed.

## References

- ADCD 2.1 Hardware Manual — ECS display modes
- AmigaMail Vol. 2 — ECS multiscan articles
- NDK39: `graphics/modeid.h` — monitor mode IDs
- A3000 Technical Reference Manual — display timing chapter

## See Also

- [Video Signal & Timing](../common/video_timing.md) — BEAMCON0 theory, signal generation pipeline, genlock
- [Display Modes](../../08_graphics/display_modes.md) — ModeID system, DblPAL/DblNTSC mode selection
