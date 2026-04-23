[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Copper — What It Is, How It Works, and Programming Guide

## What Is the Copper?

The **Copper** (Co-Processor) is one of the most distinctive pieces of hardware in any computer ever built. It is a tiny, ultra-simple programmable DMA engine that executes a program — called a **copper list** — in perfect synchronisation with the video beam as it sweeps across the screen.

The Copper watches the beam position and can **write any value to any custom chip register at any specific screen position**. This single capability enables an astonishing range of visual effects.

### Why Does It Matter?

On a conventional computer, changing display parameters (colours, scroll positions, resolutions) requires the CPU to execute code at precisely the right moment. This is fragile, wastes CPU time, and is limited by interrupt latency.

The Copper does this **automatically, for free, with perfect timing** — every single frame, without any CPU involvement at all.

---

## Copper in the System Architecture

### Block Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHIP RAM (up to 2MB)                         │
│  ┌──────────────┐   ┌──────────────┐  ┌───────────────────────────┐ │
│  │ Copper List  │   │ Bitplane Data│  │ Sprite Data               │ │
│  │ (MOVE/WAIT/  │   │ (screen      │  │ (hardware sprite          │ │
│  │  SKIP words) │   │  pixels)     │  │  images)                  │ │
│  └──────┬───────┘   └──────┬───────┘  └──────────┬────────────────┘ │
└─────────┼──────────────────┼─────────────────────┼──────────────────┘
          │ DMA read         │ DMA read            │ DMA read
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGNUS / ALICE  (DMA Controller)                  │
│                                                                     │
│  ┌────────────┐    ┌──────────────┐    ┌───────────────────────┐    │
│  │   COPPER   │    │  Bitplane    │    │   Sprite DMA          │    │
│  │   Engine   │    │  DMA Engine  │    │   Engine              │    │
│  │            │    │              │    │                       │    │
│  │ • Fetches  │    │ Fetches 1-8  │    │ Fetches sprite        │    │
│  │   copper   │    │ planes per   │    │ data for 8 sprites    │    │
│  │   list via │    │ line from    │    │ per line              │    │
│  │   DMA      │    │ BPLxPT       │    │                       │    │
│  │ • Compares │    │ pointers     │    │                       │    │
│  │   beam pos │    │              │    │                       │    │
│  │ • Writes   │    │              │    │                       │    │
│  │   to regs  │    │              │    │                       │    │
│  └─────┬──────┘    └──────┬───────┘    └───────────┬───────────┘    │
│        │                  │                        │                │
│  ┌─────┴──────────────────┴────────────────────────┴─────────┐      │
│  │              BEAM COUNTER (V count, H count)              │      │
│  │    Increments every colour clock, resets each frame       │      │
│  │    PAL: 312 lines × 227 clocks   NTSC: 262 × 227          │      │
│  └───────────────────────────────────────────────────────────┘      │
└──────────┬─────────────────────────────────────────────────────────┘
           │ register writes ($DFF000–$DFF1FE)
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DENISE / LISA  (Video Encoder)                   │
│                                                                     │
│  Receives bitplane data + sprite data + colour register values      │
│  Composites them into a final pixel stream:                         │
│                                                                     │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Bitplane   │  │ Sprite   │  │ Colour   │  │ Playfield        │   │
│  │ Decode     │→ │ Priority │→ │ Palette  │→ │ Priority &       │   │
│  │ (planar→   │  │ Merge    │  │ Lookup   │  │ Genlock Control  │   │
│  │  index)    │  │          │  │ (32/256) │  │                  │   │
│  └────────────┘  └──────────┘  └──────────┘  └────────┬─────────┘   │
└───────────────────────────────────────────────────────┬─────────────┘
                                                        │
                                                        ▼
                                                  ┌────────────┐
                                                  │  RGB / DAC │
                                                  │  → Monitor │
                                                  └────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          M68K CPU                                   │
│                                                                     │
│  • Can read/write the SAME custom registers as the Copper           │
│  • Can modify the copper list in Chip RAM at any time               │
│  • Shares the DMA bus with Copper (Agnus arbitrates)                │
│  • CPU is STALLED when DMA bus is busy (Chip RAM access only)       │
│  • Fast RAM access is NOT affected by DMA contention                │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Interactions

**Copper ↔ Chip RAM:**
The Copper fetches its program (the copper list) from Chip RAM via DMA. It reads one instruction (2 words = 4 bytes) every 4 colour clocks. The copper list **must** reside in Chip RAM — it cannot be in Fast RAM because only Chip RAM is DMA-accessible.

**Copper ↔ Custom Registers:**
When the Copper executes a MOVE instruction, it writes directly to a custom chip register (`$DFF000`–`$DFF1FE`). This is the exact same register space the CPU writes to. The Copper can set colours, bitplane pointers, sprite pointers, display window, scroll offsets, DMA control, and audio parameters.

**Copper ↔ Beam Counter:**
The Copper continuously compares the current beam position (V count, H count) against WAIT instructions. When the beam reaches or passes the specified position, execution continues. This is a hardware comparator — no polling loop, no interrupt latency.

**Copper ↔ CPU:**
- They share the DMA bus. Agnus arbitrates: DMA engines get priority, CPU gets remaining cycles
- The CPU can modify copper list words in Chip RAM; changes take effect on the next frame (or immediately if the Copper hasn't read that instruction yet)
- The CPU can set `COP1LC`/`COP2LC` to change which copper list runs
- The CPU can strobe `COPJMP1`/`COPJMP2` to restart the Copper mid-frame
- The CPU is **not interrupted** by Copper activity — they are fully independent

**Copper ↔ Video Output:**
The Copper doesn't produce video directly. It modifies the registers that Denise/Lisa uses to produce video. By changing registers at specific beam positions, the Copper indirectly controls what appears on every scanline.

**Copper ↔ Blitter:**
A WAIT instruction with bit 15 of the mask word cleared becomes a "blitter-finished WAIT" — the Copper pauses until both the beam position is reached AND the blitter is idle. This coordinates copper list execution with blitter operations.

---

## What the Copper Can Do

| Effect | How | Used In |
|---|---|---|
| **Per-line colour changes** | WAIT for line, MOVE colour register | Gradient skies, rainbow bars |
| **Split screens** | Change bitplane pointers mid-frame | Status bar + scrolling playfield |
| **Parallax scrolling** | Change BPLCON1 (scroll offset) at different lines | Multi-layer side-scrollers |
| **Resolution changes** | Change BPLCON0 mid-frame | HiRes menu + LoRes game area |
| **Sprite multiplexing** | Repoint sprite DMA pointers after sprite finishes | More than 8 sprites per frame |
| **Palette animation** | Modify colour registers each frame | Cycling colours, water shimmer |
| **Display window tricks** | Change DIWSTRT/DIWSTOP | Overscan, letterbox |
| **Interlace tricks** | Toggle LOF bit | Custom interlace effects |

### What the Copper Cannot Do

| Limitation | Detail |
|---|---|
| No computation | Cannot add, subtract, compare, branch, or loop |
| No memory read | Can only WRITE to registers, never read |
| Write-only to custom regs | Cannot write to CPU memory, CIA, or Fast RAM |
| Limited register set | Protected registers ($000–$03E) need `COPCON` unlock |
| No sub-pixel timing | Horizontal resolution is 4 colour clocks (~8 low-res pixels) |
| Vertical wrapping | V counter wraps at 255; PAL lines 256+ need two WAITs |

---

## Instruction Set

The Copper has exactly **3 instructions**. Each is 32 bits (two 16-bit words):

### MOVE — Write Value to Register

```
Word 1: 0RRRRRRR RR000000    R = register offset ($040–$1FE, even)
Word 2: DDDDDDDD DDDDDDDD    D = 16-bit data to write

Example: Set COLOR00 ($180) to bright red ($0F00):
  dc.w  $0180, $0F00
```

The register address in word 1 is the offset from `$DFF000`. Bit 0 of word 1 is always 0 (this distinguishes MOVE from WAIT/SKIP).

### WAIT — Wait for Beam Position

```
Word 1: VVVVVVVV HHHHHHHH    V = vertical beam (8 bits), H = horizontal
                               Bit 0 = 1 (marks this as WAIT, not MOVE)
Word 2: vvvvvvvv hhhhhhhm    v,h = mask bits, m = 0 for WAIT
                               (bit 0 of word 2 = 0 distinguishes from SKIP)

Example: Wait for line 100 ($64), any horizontal position:
  dc.w  $6401, $FFFE
```

The mask controls which beam position bits are compared. `$FFFE` means "match all bits" (standard). You can mask horizontal bits to wait for a specific column.

### SKIP — Conditional Skip

```
Same format as WAIT, but bit 0 of word 2 = 1.
If beam ≥ specified position, skip the next instruction.

Example: Skip next if beam is past line 200:
  dc.w  $C801, $FFFF    ; SKIP if V ≥ $C8
  dc.w  $0180, $0F00    ; this MOVE is skipped if condition met
```

### End of List

```
  dc.w  $FFFF, $FFFE    ; WAIT for impossible position (V=$FF, H=$FF)
                          ; Copper halts until next frame
```

---

## Your First Copper List

Here's the simplest possible copper list — it changes the background colour at line 128:

```asm
    SECTION copperlist,DATA_C    ; *** MUST be in Chip RAM! ***

MyCopperList:
    ; Top half: blue background
    dc.w    $0180, $005F        ; MOVE COLOR00 = blue

    ; Wait for middle of screen
    dc.w    $8001, $FFFE        ; WAIT line 128

    ; Bottom half: red background
    dc.w    $0180, $0F00        ; MOVE COLOR00 = red

    ; End of list
    dc.w    $FFFF, $FFFE        ; WAIT forever
```

To activate it:
```asm
    lea     $DFF000,a5
    move.l  #MyCopperList,$080(a5)   ; COP1LCH = pointer to our list
    move.w  d0,$088(a5)              ; COPJMP1 strobe = restart copper
    move.w  #$8280,$096(a5)          ; DMACON: enable Copper + Master DMA
```

---

## Rainbow Gradient (Colour Per Scanline)

```asm
RainbowCopper:
    dc.w    $2C01,$FFFE         ; WAIT line 44 (first visible PAL line)
    dc.w    $0180,$0F00         ; red
    dc.w    $2D01,$FFFE         ; line 45
    dc.w    $0180,$0E10
    dc.w    $2E01,$FFFE         ; line 46
    dc.w    $0180,$0D20
    dc.w    $2F01,$FFFE         ; line 47
    dc.w    $0180,$0C30
    dc.w    $3001,$FFFE         ; line 48
    dc.w    $0180,$0B40
    dc.w    $3101,$FFFE         ; line 49
    dc.w    $0180,$0A50
    dc.w    $3201,$FFFE         ; line 50
    dc.w    $0180,$0960
    ; ... continue for each line ...
    dc.w    $FFFF,$FFFE
```

This produces a smooth colour gradient down the screen — **zero CPU cost**.

---

## Parallax Scrolling (Per-Layer Scroll Speed)

```asm
ParallaxCopper:
    ; Sky layer (no scroll)
    dc.w    $0102,$0000         ; BPLCON1 = 0 (no shift)

    ; Wait for horizon
    dc.w    $6001,$FFFE         ; WAIT line 96

    ; Hills layer (scroll slow)
    dc.w    $0102,$0022         ; BPLCON1 = shift 2 pixels

    ; Wait for ground
    dc.w    $A001,$FFFE         ; WAIT line 160

    ; Ground layer (scroll fast)
    dc.w    $0102,$0066         ; BPLCON1 = shift 6 pixels

    dc.w    $FFFF,$FFFE
```

Each frame, a VBlank interrupt updates the scroll values in the copper list. The CPU just modifies 3 words — the Copper handles all the per-line register changes.

---

## Sprite Multiplexing

The Amiga has 8 hardware sprites, but the Copper can repoint them mid-frame for more:

```asm
    ; Sprite 0 shows character A at Y=50
    dc.w    $3001,$FFFE         ; WAIT before sprite starts
    dc.w    $0120,SprDataA>>16  ; SPR0PTH
    dc.w    $0122,SprDataA      ; SPR0PTL

    ; After sprite A finishes (Y=66), reuse for character B at Y=120
    dc.w    $7801,$FFFE         ; WAIT line 120
    dc.w    $0120,SprDataB>>16  ; SPR0PTH = new sprite data
    dc.w    $0122,SprDataB      ; SPR0PTL

    ; After character B finishes, reuse for character C...
    dc.w    $A001,$FFFE
    dc.w    $0120,SprDataC>>16
    dc.w    $0122,SprDataC
```

This gives you **24+ sprites** on screen (8 physical × 3+ reuses per frame).

---

## System-Friendly Copper (OS API)

If your program coexists with Workbench, use `graphics.library`:

```c
struct UCopList *ucl = AllocMem(sizeof(struct UCopList), MEMF_CLEAR);

CINIT(ucl, 50);                          /* init, max 50 instructions */
CWAIT(ucl, 0, 0);                         /* wait top of screen */
CMOVE(ucl, custom.color[0], 0x005F);     /* COLOR00 = blue */
CWAIT(ucl, 128, 0);                       /* wait line 128 */
CMOVE(ucl, custom.color[0], 0x0F00);     /* COLOR00 = red */
CEND(ucl);                                /* end */

viewport->UCopIns = ucl;
RethinkDisplay();                         /* merge into system copper list */
```

The OS inserts your instructions into its own copper list, interleaved with its own display management.

---

## AGA Copper Enhancements

AGA (Alice chip) keeps the same 3-instruction Copper but gains access to the **extended AGA registers**:

| AGA Feature | Copper Can Set |
|---|---|
| 256-colour palette | `COLOR00–COLOR255` via BPLCON3 bank select |
| Extended sprites | 64-colour sprites via palette banks |
| FMODE | DMA fetch width (but careful — affects in-progress DMA) |
| BPLCON3/BPLCON4 | AGA-specific bitplane/sprite control |

### AGA Palette via Copper

AGA has 256 colours but still only 32 colour registers visible at a time. To load all 256 colours, the Copper uses BPLCON3 to select palette banks:

```asm
    ; Load colours 0–31 (bank 0)
    dc.w    $0106,$0000         ; BPLCON3: bank 0
    dc.w    $0180,$0000         ; COLOR00
    dc.w    $0182,$0111         ; COLOR01
    ; ... all 32 colours ...

    ; Switch to bank 1 (colours 32–63)
    dc.w    $0106,$2000         ; BPLCON3: bank 1
    dc.w    $0180,$0222         ; COLOR32
    dc.w    $0182,$0333         ; COLOR33
    ; ... etc for all 8 banks ...
```

---

## Copper Timing

| Parameter | Value |
|---|---|
| Instruction time | 4 colour clocks (= 8 lo-res pixels = ~1.12 µs) |
| Max instructions per line | ~112 (NTSC) / ~114 (PAL) |
| Horizontal resolution | 4 colour clocks (~8 lo-res pixels) |
| Vertical range | 0–255 (wraps; use double-WAIT for PAL lines 256+) |
| PAL visible lines | 44–300 (256 visible) |
| NTSC visible lines | 44–244 (200 visible) |

---

## References

- HRM: *Copper* chapter — authoritative register descriptions
- `08_graphics/copper.md` — graphics.library UCopList API
- `08_graphics/copper_programming.md` — additional examples
- `01_hardware/ocs_a500/copper.md` — OCS-level register reference
