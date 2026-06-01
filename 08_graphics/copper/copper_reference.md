[← Home](../../README.md) · [Graphics](../README.md) · [Copper](README.md)

# Copper ISA — Complete Reference Manual

## Overview

The **Copper** (Co-Processor) is a tiny DMA-driven programmable engine inside the Agnus chip (OCS/ECS) or Alice chip (AGA). It executes a program — called a **copper list** — from Chip RAM in perfect synchronization with the video beam. Its sole capability is writing 16-bit values to custom chip registers at precise beam positions.

Despite having only **3 instructions** and no arithmetic, branching, or memory read capability, the Copper is the single most important piece of custom hardware for visual effects. Every per-scanline color change, split screen, parallax scroll, and sprite multiplex on the Amiga traces back to the Copper.

### What the Copper Can Do

| Capability | Mechanism | Typical Use |
|---|---|---|
| Per-line color changes | WAIT for line, MOVE to COLORxx | Gradient skies, rainbow bars, water effects |
| Split-screen displays | Change bitplane pointers mid-frame | Status bar + scrolling game area |
| Parallax scrolling | Change BPLCON1 scroll offset per region | Multi-layer side-scrollers |
| Resolution mixing | Change BPLCON0 mid-frame | HiRes title bar + LoRes gameplay |
| Sprite multiplexing | Repoint sprite DMA pointers after sprite ends | 24+ sprites using 8 physical slots |
| Palette animation | CPU modifies copper list MOVE data each frame | Cycling water, fire, lava |
| Display window shaping | Change DIWSTRT/DIWSTOP mid-frame | Overscan, borders, letterbox |
| DMA scheduling | Toggle bitplane/sprite DMA enable per line | Hide artifacts during setup |
| Audio control | Write to AUDxVOL, AUDxPER registers | Copper-driven music players |
| Self-modification | Copper writes to COP1LC, DMACON | Copper re-points itself mid-frame |

### What the Copper Cannot Do

| Limitation | Detail |
|---|---|
| No arithmetic | Cannot add, subtract, multiply, or compare values |
| No branching or loops | Executes linearly top-to-bottom; no jumps or calls |
| No memory read | Can only WRITE to registers — cannot read anything |
| No CPU memory access | Writes only to custom chip registers (`$DFF000`+), not RAM or CIA |
| No sub-pixel timing | Horizontal resolution: 2 color clocks per WAIT step (~4 lo-res pixels) |
| V counter wraps at 255 | PAL lines 256–311 require a double-WAIT trick |
| Chip RAM only | The copper list itself must reside in Chip RAM (DMA-accessible) |
| No interrupt generation | Copper cannot cause CPU interrupts directly |

### Where the Copper Lives

The Copper is part of the Agnus (OCS/ECS) or Alice (AGA) chip, which also contains the DMA controller and beam counter. The Copper fetches its program via DMA from Chip RAM, compares beam positions using a hardware comparator, and writes directly to the custom chip register space that Denise (OCS/ECS) or Lisa (AGA) reads for video generation.

```
 CHIP RAM
  ┌──────────────────┐
  │  Copper List     │── DMA fetch ──→  COPPER ENGINE  ── register write ──→  DENISE/LISA
  │  (MOVE/WAIT/     │                 (inside Agnus/     (to $DFF000+)       (video output)
  │   SKIP words)    │                  Alice)
  └──────────────────┘       ↑
                             │
                        BEAM COUNTER
                     (V count, H count)
```

---

## Instruction Set Reference

The Copper has exactly **3 instructions**. Every instruction is exactly **32 bits** (two 16-bit words). The Copper fetches one instruction over 2 DMA cycles (2 color clocks).

Instruction dispatch is determined by the low bits of word 1:

| Word 1 bit 0 | Word 2 bit 0 | Instruction |
|---|---|---|
| 0 | — | **MOVE** (register write) |
| 1 | 0 | **WAIT** (wait for beam position) |
| 1 | 1 | **SKIP** (conditional skip) |

### MOVE — Write Value to Register

Writes a 16-bit value to a custom chip register.

```
Word 1 bit layout:
 15                8 7                 0
 ┌──────────────────┬──────────────────┐
 │ 0 0 0 0 0 0 0 R  │ R R R R R R R 0  │   R = register offset (bits 8-1)
 └──────────────────┴──────────────────┘

Word 2 bit layout:
 15                                  0
 ┌────────────────────────────────────┐
 │ D D D D D D D D D D D D D D D D    │   D = 16-bit data value
 └────────────────────────────────────┘
```

**Constraints:**
- Register offset is relative to `$DFF000` (custom chip base)
- The register address must be **even** (bit 0 of word 1 is always 0 — this is how the hardware distinguishes MOVE from WAIT/SKIP)
- Usable register range: `$040`–`$1FE` by default
- Registers `$000`–`$03E` are **protected** by the `COPCON` register (see Section 4)
- When `COPCON.CDANG = 1`, the Copper can also write to `$000`–`$03E` (dangerous — includes blitter registers, DMA control, copper pointers)

**Execution time:** 2 DMA cycles (2 color clocks)

**Examples:**
```asm
    dc.w    $0180, $0F00        ; MOVE  $0F00 → COLOR00 ($DFF180)
    dc.w    $0100, $1200        ; MOVE  $1200 → BPLCON0 ($DFF100)
    dc.w    $0E0,  $0000        ; MOVE  $0000 → BPL1PTH ($DFF0E0)
    dc.w    $0E2,  $8000        ; MOVE  $8000 → BPL1PTL ($DFF0E2)
```

### WAIT — Wait for Beam Position

Stalls the Copper until the video beam reaches (or has passed) a specified position, optionally also waiting for the blitter to finish.

```
Word 1 bit layout:
  Bits 15–8  → VP7–VP0 : vertical position (8 bits)
  Bits  7–1  → HP6–HP0 : horizontal position (7 bits)
  Bit   0    → always 1 : identifies WAIT/SKIP instruction

Word 2 bit layout (WAIT):
  Bit  15    → BFD      : blitter-finished-done (0 = also wait for blitter)
  Bits 14–8  → VE6–VE0  : vertical compare enable (7-bit mask)
  Bits  7–1  → HE6–HE0  : horizontal compare enable (7-bit mask)
  Bit   0    → always 0 : identifies WAIT (1 for SKIP)

  Bit budget: 8+7+1 = 16 (word 1) · 1+7+7+1 = 16 (word 2)
```

**How WAIT works:**

The Copper compares the current beam position against the WAIT position using the mask. For each bit position, if the mask bit is 1, the corresponding beam bit must match (or exceed) the WAIT value. If the mask bit is 0, that bit is "don't care."

Formally: the Copper stalls until `(beam_VH & mask) >= (wait_VH & mask)`.

> [!NOTE]
> The comparison is **greater than or equal**, not exact match. Once the beam passes the WAIT position, the Copper continues immediately. This means a WAIT for a position the beam has already passed does **not** stall — execution continues at once.

**Blitter-wait flag (bit 15 of word 2):**
- If bit 15 = **1** (standard): wait only for beam position. This is the normal case — `$FFFE` has bit 15 set.
- If bit 15 = **0**: wait for beam position **AND** the blitter to finish. The Copper stalls until both conditions are met. Use this to coordinate copper operations with blitter completion.

**Standard mask:** `$FFFE` — all bits compared (bit 0 always 0 for WAIT).

**Execution time:** 2 DMA cycles (2 color clocks) once the position is reached. While stalled, the Copper consumes no DMA cycles — they are available to the CPU and other DMA channels.

**Examples:**
```asm
    ; Wait for line 100, any horizontal position
    dc.w    $6401, $FFFE        ; WAIT V=$64(100), H=$01, full mask

    ; Wait for line 50, horizontal position $40 (mid-scanline)
    dc.w    $3241, $FFFE        ; WAIT V=$32(50), H=$40

    ; Wait for line 200 AND blitter finished
    dc.w    $C801, $7FFE        ; WAIT V=$C8(200), blitter-wait bit = 0

    ; Wait for any line (don't care V), no blitter-wait
    dc.w    $0001, $80FE        ; WAIT V=0, H=1, V-mask=0 (don't care V)
                                ; bit 15=1 (no blitter-wait), VE=0000000, HE=1111111
```

### SKIP — Conditional Skip

Conditionally skips the next instruction if the beam has reached or passed a specified position.

```
Word 1:  identical to WAIT format
Word 2:  identical to WAIT format except bit 0 = 1

The only difference from WAIT:
  - WAIT: word 2 bit 0 = 0
  - SKIP: word 2 bit 0 = 1
```

**How SKIP works:**

1. The Copper evaluates the beam position comparison (same logic as WAIT)
2. If the beam position matches (same `>= masked position` test), the **next instruction is skipped**
3. If the beam has NOT reached the position, the next instruction executes normally

SKIP is primarily used for **double-buffered copper lists** — two lists that alternate between frames using SKIP to select which half runs on even vs. odd fields.

**Execution time:** 2 DMA cycles (2 color clocks).

**Example:**
```asm
    ; If beam is past line 200, skip the color change
    dc.w    $C801, $FFFF        ; SKIP if V >= $C8(200)
    dc.w    $0180, $0F00        ; this MOVE is skipped when condition is true
```

### End-of-List Sentinel

```asm
    dc.w    $FFFF, $FFFE        ; WAIT V=$FF, H=$FF
                                ; Beam can never reach this position
                                ; Copper halts until next vertical blank
```

When the Copper encounters this instruction, it halts permanently. The WAIT position (V=`$FF`, H field=`$7F` = H counter `$FE`) is beyond the scanline length (~`$E2` for PAL, ~`$DA` for NTSC), so the beam can never reach it. When V wraps from `$FF` to `$00`, the condition fails permanently. At the next vertical blank, the Copper automatically restarts from `COP1LC` (or `COP2LC` for interlace odd fields).

---

## Beam Position Encoding

The Copper tracks the video beam using a vertical counter (V) and horizontal counter (H).

### Vertical Counter (V)

- **8-bit counter** (bits 15–8 of WAIT/SKIP word 1)
- Range: `$00`–`$FF` (0–255)
- Increments once per scanline
- **Wraps at 255** — this is the Copper's most important limitation for PAL systems

| System | Total Lines | Copper-Addressable | Visible Lines | Lines > 255? |
|---|---|---|---|---|
| PAL | 312 | 0–255 (wraps) | 44–300 | Lines 256–311 need double-WAIT |
| NTSC | 262 | 0–255 (full range) | 44–244 | No — fits in 8 bits |
| NTSC (non-interlaced) | 263 | 0–255 | 44–244 | Line 263 is never addressed |

### PAL Lines > 255: The Double-WAIT Trick

PAL has 312 lines, but the Copper's V counter wraps at 256. To access lines 256–311:

```asm
    ; To wait for PAL line 260 (V=$104):
    dc.w    $FF01, $FFFE        ; First WAIT: stall at V=$FF (255)
    dc.w    $0401, $FFFE        ; Second WAIT: V=$04 (260-256=4)
    ; Copper is now at PAL line 260
```

The first WAIT stalls at V=$FF (end of the 0–255 range). When V wraps to 0, the second WAIT catches the target line. The intermediate WAIT is mandatory — without it, the Copper would execute subsequent MOVEs immediately because V=4 was "already passed."

The standard pattern for accessing the lower PAL border:
```asm
    dc.w    $FFDF, $FFFE        ; WAIT V=$FF — end of first pass
    dc.w    $2C01, $FFFE        ; WAIT V=$2C(44) — wrapped to line 300
```

### Horizontal Counter (H)

- **7 bits** (bits 7–1 of WAIT/SKIP word 1, bit 0 is always 1 for WAIT/SKIP)
- Range: H counter `$02`–`$E2` (even values only, since only 7 bits are compared)
- Resolution: **2 color clocks per step** (approximately 4 lo-res pixels)
- A full PAL scanline is ~227 color clocks (~454 lo-res pixels)

The H counter value (even, `$00`–`$E2`) is stored directly in bits 7–1 of word 1. Bit 0 is always 1 for WAIT/SKIP. Since H counter values are always even (bit 0 = 0), the low bit is available as the instruction type marker.

Encoding: `word1[7:0] = H_counter | 1`

The hardware compares bits 7–1 of the WAIT position against bits 7–1 of the beam H counter. The WAIT triggers when `beam_H[7:1] >= wait_H[7:1]`.

```asm
    ; Wait for H counter $38 (color clock 56):
    dc.w    $0139, $FFFE        ; WAIT V=$01, H=$38 → word1 = ($01<<8) | $38 | 1 = $0139

    ; Wait for H counter $E0 (color clock 224, mid-scanline):
    dc.w    $01E1, $FFFE        ; WAIT V=$01, H=$E0 → word1 = ($01<<8) | $E0 | 1 = $01E1
```

### AGA Extended Horizontal Position

AGA adds the **BPC** (Beam Position Count) bit in the `FMODE` register. When set, the Copper uses 8-bit horizontal positions instead of 7-bit, doubling the horizontal WAIT resolution. This allows precise positioning within a HiRes or SuperHiRes scanline.

---

## Copper Control Registers

These registers control the Copper itself. They are accessed by the CPU (or by the Copper via MOVE if `COPCON.CDANG` is set).

### Register Map

| Address | Name | Type | Description |
|---|---|---|---|
| `$DFF080` | `COP1LCH` | R/W | Copper list 1 pointer, high word |
| `$DFF082` | `COP1LCL` | R/W | Copper list 1 pointer, low word |
| `$DFF084` | `COP2LCH` | R/W | Copper list 2 pointer, high word |
| `$DFF086` | `COP2LCL` | R/W | Copper list 2 pointer, low word |
| `$DFF088` | `COPJMP1` | Strobe | Restart Copper from COP1LC (any write) |
| `$DFF08A` | `COPJMP2` | Strobe | Restart Copper from COP2LC (any write) |
| `$DFF02E` | `COPCON` | R/W | Copper configuration |
| `$DFF096` | `DMACON` | R/W | DMA control (bit 7 = COPEN) |

### COPCON ($DFF02E)

```
 15                              1 0
 ┌─────────────────────────────────┬───┐
 │                             CDANG│ 0 │
 └─────────────────────────────────┴───┘

Bit 1 (CDANG — Copper Danger):
  0 = Copper cannot write to registers $000–$03E (default, safe)
  1 = Copper CAN write to registers $000–$03E (dangerous!)
```

Protected register range (`$000`–`$03E`) includes:
- Blitter registers (`BLTCON0`, `BLTCON1`, `BLTAFWM`, `BLTALWM`, `BLTxPT`, `BLTSIZE`)
- DMA control (`DMACON`)
- Copper pointers (`COP1LC`, `COP2LC`, `COPJMP1`, `COPJMP2`)
- Interrupt control (`INTENA`, `INTREQ`)
- Audio registers (`AUDxVOL`, `AUDxPER`)

Setting `CDANG = 1` allows the Copper to modify any of these — including itself. This is used for:
- **Copper self-modification**: Copper writes a new `COP1LC` value, then hits `COPJMP1` to jump to a different list mid-frame
- **Copper audio**: Copper writes to `AUDxPER`/`AUDxVOL` for timed audio effects
- **Copper DMA control**: Copper toggles `DMACON` bits to enable/disable other DMA channels

> [!WARNING]
> A buggy copper list with `CDANG=1` can corrupt blitter state, disable DMA, or crash the system. Always keep `CDANG=0` unless you specifically need it.

### DMACON ($DFF096)

```
 15  14 13   9 8     6 5     0
 ┌───┬──────┬───────┬───────┐
 │SET│ rsvd │ DMAEN │ COPEN │ other DMA bits...
 └───┴──────┴───────┴───────┘

Bit 15 (SET):
  0 = Clear the specified bits
  1 = Set the specified bits

Bit 9 (DMAEN):
  Master DMA enable — all DMA is disabled when this is 0

Bit 7 (COPEN):
  Copper DMA enable — when 0, the Copper stops fetching instructions
```

The standard pattern to enable the Copper:
```asm
    move.w  #$8280, $DFF096     ; DMACON: SET(1) | DMAEN(1) | COPEN(1)
                                ; $8000=SET, $0200=DMAEN, $0080=COPEN
```

### COP1LC / COP2LC

These 32-bit registers (split into high and low words) point to the copper list in Chip RAM:

- **COP1LC**: Used for non-interlaced frames and even fields (long frame)
- **COP2LC**: Used for odd fields in interlace mode (short frame)

The Copper reads from `COP1LC` at vertical blank, or from `COP2LC` for interlace odd fields.

### COPJMP1 / COPJMP2

These are **strobe** registers — writing any value to them causes an immediate action:

- `COPJMP1`: Restart the Copper, fetching from `COP1LC`
- `COPJMP2`: Restart the Copper, fetching from `COP2LC`

The Copper restarts from the beginning of the specified list on the next DMA cycle. Writing `COPJMP1` mid-frame is the standard technique for copper list switching.

> [!IMPORTANT]
> `COPJMP1`/`COPJMP2` take effect immediately — there is no synchronization with the beam. If you write them at an unpredictable time, the Copper may execute instructions at the wrong beam position. Use `WaitTOF()` or a VBlank interrupt to synchronize.

### Starting the Copper (Bare Metal)

```asm
    lea     $DFF000, a5             ; custom chip base

    ; Load copper list pointer
    move.l  #MyCopperList, d0
    move.l  d0, $080(a5)            ; COP1LCH:COP1LCL (32-bit write)

    ; Enable Copper DMA
    move.w  #$8280, $096(a5)        ; DMACON: SET | DMAEN | COPEN

    ; Strobe restart (optional if loading before DMA enabled)
    move.w  #0, $088(a5)            ; COPJMP1 — restart now
```

### Stopping the Copper

```asm
    ; Method 1: Disable Copper DMA
    move.w  #$0080, $DFF096         ; DMACON: clear COPEN (no SET bit)

    ; Method 2: End-of-list sentinel in copper list
    ; dc.w $FFFF, $FFFE  — Copper halts until next VBlank

    ; Method 3: Point to an empty list (just $FFFF,$FFFE)
    move.l  #EmptyList, $DFF080     ; COP1LC = empty list
    move.w  #0, $DFF088             ; COPJMP1 — restart on empty list
```

---

## Copper List Structure

### Format

A copper list is a contiguous array of 32-bit instructions in **Chip RAM**. Each instruction is two 16-bit words stored sequentially. The list is terminated by the end-of-list sentinel (`$FFFF,$FFFE`).

```asm
MyCopperList:
    dc.w    $0180, $0000        ; MOVE COLOR00 = black
    dc.w    $2C01, $FFFE        ; WAIT line 44
    dc.w    $0180, $0F00        ; MOVE COLOR00 = red
    dc.w    $FFFF, $FFFE        ; END
```

**Requirements:**
- Must reside in **Chip RAM** (DMA can only reach Chip RAM)
- Must be word-aligned (even address)
- Must be terminated with `$FFFF,$FFFE`
- Must not be modified while the Copper is reading it (or use double-buffering)

### Dual Copper Lists (Interlace)

The Amiga supports two copper list pointers for interlaced display:

| Register | Field | Used When |
|---|---|---|
| `COP1LC` | Long frame (even field) | Non-interlaced, or every other frame in interlace |
| `COP2LC` | Short frame (odd field) | Interlace odd fields only |

In non-interlaced mode, only `COP1LC` is used. The Copper restarts from `COP1LC` every vertical blank.

In interlace mode, the Copper alternates: `COP1LC` for even fields, `COP2LC` for odd fields. This allows different copper instructions for the two interlace fields.

### System Copper Lists (AmigaOS)

When AmigaOS is running, `graphics.library` builds and manages the copper list. The relevant `GfxBase` fields:

| Pointer | Description |
|---|---|
| `GfxBase->copinit` | System initialization copper list (set up during `InitArea()`) |
| `GfxBase->LOFlist` | Long-frame copper list (even fields) |
| `GfxBase->SHFlist` | Short-frame copper list (odd fields, interlace) |

The OS copper list contains:
1. Bitplane pointer setup (all BPLxPT registers)
2. Sprite pointer setup (all SPRxPT registers)
3. Display window registers (DIWSTRT/DIWSTOP, DDFSTRT/DDFSTOP)
4. Bitplane control (BPLCON0/1/2)
5. Color registers (COLOR00–COLOR31)
6. Any user copper instructions (from `UCopList`)

User code adds instructions via the `UCopList` mechanism (see Section 9).

### SKIP-Based Double Buffering

The SKIP instruction enables two copper lists to coexist in one memory block:

```asm
DoubleBuffer:
    ; Skip-list header: if beam >= $FF, skip first instruction
    dc.w    $FF01, $FFFF        ; SKIP if V >= $FF (i.e., second pass)
    dc.w    $0180, $0F00        ; Skipped on 2nd pass: COLOR00 = red (1st pass)

    ; If we get here, beam < $FF (first pass)
    dc.w    $0180, $00F0        ; COLOR00 = green (2nd pass, after V wraps)

    dc.w    $FF01, $FFFE        ; WAIT V=$FF
    dc.w    $0101, $FFFE        ; WAIT V=$01 (wrapped)
    dc.w    $0180, $000F        ; COLOR00 = blue (post-wrap)

    dc.w    $FFFF, $FFFE        ; END
```

### Mid-Frame Copper List Swap

The CPU can switch copper lists mid-frame by writing to `COP1LC` and then strobing `COPJMP1`:

```asm
    ; In a VBlank interrupt:
    move.l  #Frame0Copper, $DFF080   ; COP1LC = frame 0 list
    ; Frame 0 runs...

    ; Later, in a copper interrupt or timer:
    move.l  #Frame1Copper, $DFF080   ; COP1LC = frame 1 list
    move.w  #0, $DFF088              ; COPJMP1 — switch immediately
```

This is the basis of copper-animation techniques: the CPU prepares multiple copper lists and switches between them each frame.

---

## Timing and DMA Budget

### Instruction Timing

| Instruction | DMA Cycles | Color Clocks | Lo-Res Pixels | Notes |
|---|---|---|---|---|
| MOVE | 2 | 2 | ~4 | Writes one register |
| WAIT (position reached) | 2 | 2 | ~4 | Continues immediately |
| WAIT (stalled) | 0 | 0 | 0 | Consumes no DMA while waiting |
| SKIP | 2 | 2 | ~4 | Always takes 2 cycles |
| WAIT + MOVE pair | 4 | 4 | ~8 | The basic effect unit |

### DMA Slots Per Scanline

A PAL scanline has approximately **227 color clocks** (454 lo-res pixels). These are divided among all DMA channels:

| DMA Consumer | Slots Per Line | Notes |
|---|---|---|
| Bitplane DMA | 1–8 × data_fetch_width | Depends on resolution and depth |
| Sprite DMA | 0–8 × 2 words | 2 words per visible sprite per line |
| Audio DMA | 0–4 × 1 word | One word per active channel per line |
| Copper DMA | remaining slots | Shares with CPU for bus access |
| CPU | remaining slots | Gets whatever DMA doesn't use |

### Calculating Copper Bandwidth

The number of copper MOVEs per scanline depends on how much DMA bandwidth the display consumes:

**LoRes, 4 bitplanes, 8 sprites, 4 audio channels:**
```
Total slots:       227 color clocks (PAL)
Bitplane DMA:      -80  (4 planes × 20 words × 2 cycles/word, approx)
Sprite DMA:        -16  (8 sprites × 2 words)
Audio DMA:         -8   (4 channels × 2 words)
Refresh:           -18  (DRAM refresh)
───────────────────────
Copper available:  ~105 slots = ~52 MOVE instructions
```

**HiRes, 6 bitplanes, no sprites, no audio:**
```
Total slots:       227 color clocks (PAL)
Bitplane DMA:      -160 (6 planes × ~27 words × 2 cycles)
Refresh:           -18
───────────────────────
Copper available:  ~49 slots = ~24 MOVE instructions
```

**Maximum copper bandwidth (no display, no sprites):**
```
Total slots:       227
Refresh:           -18
───────────────────────
Copper available:  ~209 slots = ~104 MOVE instructions
```

> [!TIP]
> The practical rule of thumb: with a typical 4-bitplane display and sprites, you get roughly **50–60 color register writes per scanline**. This is enough for smooth gradients and moderate effects, but not for chunky-pixel rendering (which needs hundreds).

### Blitter-Nasty Interaction

The `BLTPRI` bit in `DMACON` ("blitter nasty mode") gives the blitter **absolute priority** over all other DMA, including the Copper. When `BLTPRI` is set:

- The Copper is **starved** during blitter operations — it cannot fetch instructions
- Copper WAITs may expire late, causing effects to appear at the wrong beam position
- This produces visible glitches in copper-dependent effects

**Recommendation:** Never combine `BLTPRI` with active copper effects. If you must use both, complete all blitter operations before the copper list section that depends on timing.

### OCS vs ECS vs AGA Timing

The Copper timing is identical across all Amiga chipsets:

| Parameter | OCS | ECS | AGA |
|---|---|---|---|
| Cycles per instruction | 4 color clocks | 4 color clocks | 4 color clocks |
| H resolution (standard) | 7-bit | 7-bit | 7-bit (8-bit with BPC) |
| V counter range | 0–255 | 0–255 | 0–255 |
| Max MOVEs/line (PAL) | ~104 | ~104 | ~104 |
| Blitter-wait in WAIT | Yes | Yes | Yes |

---

## Register Reference — Copper-Writable Targets

The Copper can write to any register in the `$DFF000`–`$DFF1FE` range (offsets `$000`–`$1FE`), with the following restrictions:
- Offsets `$000`–`$03E` require `COPCON.CDANG = 1` (protected range)
- Offsets must be **even** (bit 0 = 0)
- Writes are 16-bit only

### Color Registers

| Address | Name | Bits | Description |
|---|---|---|---|
| `$DFF180` | `COLOR00` | 12 (OCS/ECS), 24 (AGA) | Background color |
| `$DFF182` | `COLOR01` | 12/24 | Palette entry 1 |
| `$DFF184` | `COLOR02` | 12/24 | Palette entry 2 |
| ... | ... | ... | ... |
| `$DFF1BE` | `COLOR31` | 12/24 | Palette entry 31 |
| `$DFF1C0`–`DFF1FE` | `COLOR32`–`COLOR255` | 24 (AGA only) | AGA extended palette, accessed via BPLCON3 bank select |

OCS/ECS format: `$0RGB` (4 bits per component, 12-bit color)
AGA format: `$00RR GGGB BBBB` (8 bits per component, 24-bit color, written as two 16-bit writes via `BPLCON3`)

### Bitplane Control

| Address | Name | Description |
|---|---|---|
| `$DFF100` | `BPLCON0` | Bitplane control: depth (0–6), HIRES, HIRES/double, interlace, color-on |
| `$DFF102` | `BPLCON1` | Horizontal scroll offset (PF1 in low nibble, PF2 in high nibble) |
| `$DFF104` | `BPLCON2` | Playfield priority, sprite/clipping control |
| `$DFF106` | `BPLCON3` | AGA: palette bank select, sprite palette bank, extended features |
| `$DFF108` | `BPL1MOD` | Modulo for odd bitplanes (1, 3, 5, 7) — bytes to skip per line |
| `$DFF10A` | `BPL2MOD` | Modulo for even bitplanes (2, 4, 6, 8) |

### Bitplane Pointers

| Address | Name | Description |
|---|---|---|
| `$DFF0E0` | `BPL1PTH` | Bitplane 1 pointer, high word |
| `$DFF0E2` | `BPL1PTL` | Bitplane 1 pointer, low word |
| `$DFF0E4` | `BPL2PTH` | Bitplane 2 pointer, high word |
| `$DFF0E6` | `BPL2PTL` | Bitplane 2 pointer, low word |
| ... | ... | ... |
| `$DFF0EC` | `BPL4PTH` | Bitplane 4 pointer, high word (OCS max for useful ops) |
| `$DFF0EE` | `BPL4PTL` | Bitplane 4 pointer, low word |
| `$DFF0F0`–`$DFF0FE` | `BPL5PT`–`BPL8PT` | Bitplane 5–8 pointers (ECS/AGA 6-plane, AGA 8-plane) |

Each bitplane pointer requires two MOVE instructions (high word, then low word). To change bitplane pointers mid-frame (for split screen or page flip), all plane pointers must be updated:

```asm
    dc.w    $0E0, Bitplane2>>16    ; BPL1PTH
    dc.w    $0E2, Bitplane2&$FFFF  ; BPL1PTL
    dc.w    $0E4, Bitplane2B>>16   ; BPL2PTH
    dc.w    $0E6, Bitplane2B&$FFFF ; BPL2PTL
```

### Sprite Pointers and Control

| Address | Name | Description |
|---|---|---|
| `$DFF120` | `SPR0PTH` | Sprite 0 pointer, high word |
| `$DFF122` | `SPR0PTL` | Sprite 0 pointer, low word |
| `$DFF124` | `SPR1PTH` | Sprite 1 pointer, high word |
| `$DFF126` | `SPR1PTL` | Sprite 1 pointer, low word |
| ... | ... | ... |
| `$DFF13C` | `SPR7PTH` | Sprite 7 pointer, high word |
| `$DFF13E` | `SPR7PTL` | Sprite 7 pointer, low word |

Sprite position/control registers are written by the Copper to reposition sprites mid-frame for multiplexing:

| Address | Name | Description |
|---|---|---|
| `$DFF140` | `SPR0POS` | Sprite 0 start position (V,H) |
| `$DFF142` | `SPR0CTL` | Sprite 0 control (attach, size, V stop) |

### Display Window

| Address | Name | Description |
|---|---|---|
| `$DFF08E` | `DIWSTRT` | Display window start (V<<8|H, high nibbles only) |
| `$DFF090` | `DIWSTOP` | Display window stop (encoded: stored as `$2C81` for PAL bottom-right) |
| `$DFF092` | `DDFSTRT` | Data fetch start (determines left edge of pixel data) |
| `$DFF094` | `DDFSTOP` | Data fetch stop (determines right edge of pixel data) |

### Audio Registers (Protected — COPCON Required)

| Address | Name | Description |
|---|---|---|
| `$DFF0A0` | `AUD0LCH` | Audio channel 0 location, high word |
| `$DFF0A2` | `AUD0LCL` | Audio channel 0 location, low word |
| `$DFF0A4` | `AUD0LEN` | Audio channel 0 length (words) |
| `$DFF0A6` | `AUD0PER` | Audio channel 0 period (clocks per sample) |
| `$DFF0A8` | `AUD0VOL` | Audio channel 0 volume (0–64) |
| `$DFF0B0`–`$DFF0B8` | `AUD1xx` | Audio channel 1 |
| `$DFF0C0`–`$DFF0C8` | `AUD2xx` | Audio channel 2 |
| `$DFF0D0`–`$DFF0D8` | `AUD3xx` | Audio channel 3 |

The Copper can drive audio by writing period and volume values at timed intervals. This is the basis of "copper music" — simple melodies or sound effects generated entirely by copper lists with no CPU involvement.

### DMA Control (Protected — COPCON Required)

| Address | Name | Bits | Description |
|---|---|---|---|
| `$DFF096` | `DMACON` | 15 (SET), 9 (DMAEN), 8 (BPLEN), 7 (COPEN), 6 (BLTEN), 5 (SPREN), 4 (DSKEN), 3–0 (AUDxEN) | DMA enable/disable |

The Copper can write to `DMACON` to enable or disable any DMA channel — including itself. This is used to temporarily disable bitplane or sprite DMA in specific screen regions.

### Copper Control (Protected — COPCON Required)

| Address | Name | Description |
|---|---|---|
| `$DFF080`–`$DFF086` | `COP1LC`, `COP2LC` | Copper list pointers |
| `$DFF088`, `$DFF08A` | `COPJMP1`, `COPJMP2` | Copper restart strobes |

The Copper can re-point itself to a different list mid-frame. This is done by: (1) writing the new address to `COP1LC`, then (2) writing to `COPJMP1` to trigger the restart.

---

## OCS vs ECS vs AGA Differences

The Copper hardware is essentially unchanged across all three chipset generations. The instruction set, timing, and register access are identical. The differences are in what **target registers** are available.

| Feature | OCS | ECS | AGA |
|---|---|---|---|
| Instructions | MOVE, WAIT, SKIP | Same | Same |
| Instruction size | 32 bits (2 words) | Same | Same |
| V counter bits | 8 (0–255) | Same | Same |
| H counter bits | 7 (default) | Same | 7 default, **8 with BPC** |
| Color registers | 32 (`COLOR00`–`COLOR31`) | Same | 256 (`COLOR00`–`COLOR255`, bank-selected) |
| Color depth | 12-bit (`$0RGB`) | Same | **24-bit** (8 bits per component) |
| Max bitplanes | 6 (5 useful for playfield) | 6 | **8** |
| BPLCON0 features | LoRes, HiRes | + SuperHiRes | + SuperHiRes, 8-plane |
| BPLCON3 | Does not exist | Does not exist | Palette bank, sprite banks |
| BPLCON4 | Does not exist | Does not exist | Sprite palette XOR mask |
| FMODE | Does not exist | Does not exist | DMA fetch mode, BPC bit |
| COPCON protection | Yes | Same | Same |
| Blitter-wait bit | Yes | Same | Same |

### AGA-Specific Copper Techniques

**256-color palette loading:** AGA has 256 color registers but only 32 are visible at a time. Use `BPLCON3` to select which bank of 32 the `COLORxx` registers map to. AGA colors are 24-bit (8 bits per RGB component) and require two 16-bit writes per register, controlled by the `LOCT` bit in `BPLCON3`:

```asm
    ; Load AGA COLOR00 with 24-bit value $112233
    ; First write: upper 12 bits via BPLCON3 LOCT=1
    dc.w    $0106, $0004         ; BPLCON3: bank 0, LOCT=1 (upper nibbles)
    dc.w    $0180, $0112         ; COLOR00 upper: R=$11, G=$12 → write $0112

    ; Second write: lower 12 bits via BPLCON3 LOCT=0
    dc.w    $0106, $0000         ; BPLCON3: bank 0, LOCT=0 (lower nibbles)
    dc.w    $0180, $0233         ; COLOR00 lower: G=$2, B=$33 → write $0233

    ; Switch to bank 1 (colors 32–63)
    dc.w    $0106, $0200         ; BPLCON3: bank 1
    ; ... repeat for bank 1 colors ...
```

**Extended horizontal resolution:** Set `FMODE.BPC = 1` to enable 8-bit horizontal WAIT positions, giving twice the precision for mid-scanline effects.

> [!NOTE]
> ECS makes **no changes** to the Copper itself. The only ECS display enhancements (SuperHiRes, productivity modes) affect `BPLCON0` and `BEAMCON0`, which the Copper can write to, but the Copper engine is identical to OCS.

---

## Programming Models

### Model 1: Bare Metal (System Takeover)

For games and demos that take over the entire machine. No OS, no `graphics.library` — direct hardware access.

```asm
    ; 1. Ensure copper list is in Chip RAM
    SECTION copper, DATA_C

MyCopper:
    dc.w    $0100, $1200        ; BPLCON0: 1 bitplane, color on
    dc.w    $0092, $0038        ; DDFSTRT
    dc.w    $0094, $00D0        ; DDFSTOP
    dc.w    $008E, $2C81        ; DIWSTRT
    dc.w    $0090, $F4C1        ; DIWSTOP (PAL overscan)
    dc.w    $0180, $0000        ; COLOR00 = black
    dc.w    $FFFF, $FFFE        ; END

    SECTION code, CODE

start:
    move.l  4.w, a6             ; SysBase
    lea     $DFF000, a5         ; custom chips

    ; Suppress OS display
    move.l  #$0000, $080(a5)   ; COP1LC = NULL (point to safe list)
    move.w  #0, $088(a5)        ; COPJMP1

    ; Load our copper list
    move.l  #MyCopper, $080(a5)
    move.w  #$8280, $096(a5)    ; DMACON: SET | DMAEN | COPEN
    move.w  #0, $088(a5)        ; COPJMP1 — activate

    ; Wait for mouse click to exit
.wait:
    btst    #6, $BFE001
    bne.s   .wait

    ; Restore system (simplified)
    move.l  $4.w, a6
    jsr     -$108(a6)           ; Permit()
    rts
```

### Model 2: OS-Friendly (UCopList)

For applications that coexist with Workbench. Uses `graphics.library` to inject copper instructions into the system copper list.

```c
#include <exec/types.h>
#include <graphics/gfx.h>
#include <graphics/gfxmacros.h>
#include <graphics/copper.h>
#include <intuition/intuition.h>

void install_copper(struct ViewPort *vp) {
    struct UCopList *ucl;

    ucl = (struct UCopList *)AllocMem(sizeof(struct UCopList), MEMF_PUBLIC | MEMF_CLEAR);
    if (!ucl) return;

    CINIT(ucl, 100);                          /* init, max 100 instructions */
    CWAIT(ucl, 0, 0);                          /* wait for top of display */
    CMOVE(ucl, custom.color[0], 0x005F);      /* COLOR00 = blue */
    CWAIT(ucl, 128, 0);                        /* wait for line 128 */
    CMOVE(ucl, custom.color[0], 0x0F00);      /* COLOR00 = red */
    CEND(ucl);                                 /* end of user list */

    vp->UCopIns = ucl;
    RethinkDisplay();                          /* rebuild system copper list */
}

void remove_copper(struct ViewPort *vp) {
    vp->UCopIns = NULL;
    RethinkDisplay();
    FreeVPortCopLists(vp);
}
```

### Model 3: Self-Modifying Copper Lists

The CPU modifies the MOVE data words in the copper list each frame for animation. Since the Copper reads from Chip RAM via DMA, changes to the copper list take effect on the next frame (or immediately if the Copper hasn't read that instruction yet).

```asm
    ; Copper list with a placeholder for animated color
AnimCopper:
    dc.w    $2C01, $FFFE
ColorMove:                          ; <-- CPU patches this word
    dc.w    $0180, $0000        ; COLOR00 = (will be overwritten)
    dc.w    $FFFF, $FFFE

    ; In VBlank interrupt:
    lea     ColorMove+2, a0     ; address of the data word
    move.w  d0, (a0)            ; update COLOR00 value
    ; Copper reads new value on next frame
```

This is the technique used for color cycling (water, fire, lava), sine-wave copper bars, and any effect where the copper list pattern stays the same but register values change.

---

## Common Patterns & Recipes

### Rainbow Gradient (Color Per Scanline)

```asm
RainbowCopper:
    dc.w    $2C01, $FFFE        ; WAIT line 44 (first visible PAL)
    dc.w    $0180, $0F00        ; red
    dc.w    $2D01, $FFFE        ; line 45
    dc.w    $0180, $0E10        ; red-orange
    dc.w    $2E01, $FFFE        ; line 46
    dc.w    $0180, $0D20        ; orange
    dc.w    $2F01, $FFFE        ; line 47
    dc.w    $0180, $0C30        ; yellow-orange
    dc.w    $3001, $FFFE        ; line 48
    dc.w    $0180, $0B40        ; yellow
    ; ... continue for each line ...
    dc.w    $FFFF, $FFFE
```

### Split Screen (Two Display Modes)

```asm
SplitCopper:
    ; Top half: LoRes 4-bitplane display
    dc.w    $0100, $1200        ; BPLCON0: 4 planes, LoRes
    dc.w    $008E, $2C81        ; DIWSTRT
    dc.w    $0090, $2CC1        ; DIWSTOP (first half)
    dc.w    $0180, $000F        ; COLOR00 = blue

    ; Switch at line 128
    dc.w    $8001, $FFFE        ; WAIT line 128

    ; Bottom half: HiRes 2-bitplane display
    dc.w    $0100, $8200        ; BPLCON0: 2 planes, HiRes
    dc.w    $008E, $2C81        ; DIWSTRT
    dc.w    $0090, $F4C1        ; DIWSTOP (extended)
    dc.w    $0180, $0F00        ; COLOR00 = red

    dc.w    $FFFF, $FFFE
```

### Status Bar + Scrolling Playfield

```asm
StatusBarCopper:
    ; Top: static status bar (lines 44–59)
    dc.w    $0100, $5200        ; BPLCON0: 5 planes
    dc.w    $0E0, StatusBPL1>>16 ; bitplane pointers for status bar
    dc.w    $0E2, StatusBPL1
    dc.w    $0E4, StatusBPL2>>16
    dc.w    $0E6, StatusBPL2
    ; ... more planes ...

    ; Switch to scrolling playfield at line 60
    dc.w    $3C01, $FFFE        ; WAIT line 60
    dc.w    $0E0, PlayBPL1>>16  ; bitplane pointers for playfield
    dc.w    $0E2, PlayBPL1
    dc.w    $0E4, PlayBPL2>>16
    dc.w    $0E6, PlayBPL2
    dc.w    $0102, $0000        ; BPLCON1: scroll offset (CPU updates this)

    dc.w    $FFFF, $FFFE
```

### Sprite Multiplexing

```asm
MuxCopper:
    ; Sprite 0 at Y=50–65
    dc.w    $3201, $FFFE        ; WAIT line 50
    dc.w    $0120, SprtA>>16    ; SPR0PTH
    dc.w    $0122, SprtA        ; SPR0PTL

    ; After sprite ends at Y=66, reuse at Y=100–115
    dc.w    $6401, $FFFE        ; WAIT line 100
    dc.w    $0120, SprtB>>16    ; SPR0PTH = new data
    dc.w    $0122, SprtB        ; SPR0PTL

    ; Third reuse at Y=150–165
    dc.w    $9601, $FFFE        ; WAIT line 150
    dc.w    $0120, SprtC>>16
    dc.w    $0122, SprtC

    dc.w    $FFFF, $FFFE
```

### Blitter Coordination

```asm
BlitWaitCopper:
    ; Kick off a blit at line 50
    dc.w    $3201, $FFFE        ; WAIT line 50
    ; (CPU sets up blitter registers before this line)

    ; Wait for blitter to finish before changing display
    dc.w    $5001, $7FFE        ; WAIT line 80 AND blitter done (bit 15=0)
    dc.w    $0180, $0F00        ; COLOR00 = red (only after blit completes)

    dc.w    $FFFF, $FFFE
```

---

## Debugging & Common Pitfalls

### 1. Copper List Not in Chip RAM

**Symptom:** Copper appears to do nothing. No register writes happen.
**Cause:** The copper list was allocated in Fast RAM or BSS that linked to Fast RAM. DMA can only reach Chip RAM.
**Fix:** Use `MEMF_CHIP` when allocating, or use `SECTION data,DATA_C` in assembly.

### 2. WAIT for a Position Already Passed

**Symptom:** Copper executes MOVEs immediately, ignoring the WAIT.
**Cause:** WAIT uses `>=` comparison. If the beam has already passed the WAIT position when the Copper evaluates it, execution continues immediately.
**Fix:** Ensure WAIT positions are monotonically increasing. Never WAIT backwards. Use the double-WAIT trick for PAL lines > 255.

### 3. V Counter Wrapping at 255

**Symptom:** Effects on PAL lines 256+ don't appear or appear at wrong position.
**Cause:** The 8-bit V counter wraps from 255 to 0, not to 256.
**Fix:** Use the double-WAIT pattern:
```asm
    dc.w    $FF01, $FFFE        ; WAIT V=$FF (stall at end of 0–255 range)
    dc.w    $xx01, $FFFE        ; WAIT V=target-256 (now in the wrapped range)
```

### 4. Odd Register Address in MOVE

**Symptom:** MOVE writes to the wrong register or no effect.
**Cause:** Bit 0 of word 1 must be 0 for MOVE. If set, the hardware interprets it as WAIT/SKIP.
**Fix:** Always use even register offsets. `$DFF181` (COLOR01 + 1) is not a valid Copper target — use `$DFF182` (COLOR02).

### 5. Copper List Exceeds Scanline DMA Budget

**Symptom:** Effects appear shifted down the screen, or some MOVEs don't execute.
**Cause:** Too many copper instructions per scanline. The Copper runs out of DMA slots and catches up on the next line.
**Fix:** Reduce the number of MOVEs per line. With a 4-bitplane display, limit to ~50 MOVEs per line. Use the timing calculations in Section 6.

### 6. Blitter-Nasty Starvation

**Symptom:** Copper effects jitter or appear at wrong positions when blitter is active.
**Cause:** `BLTPRI` (DMACON bit 10) gives the blitter absolute priority, starving the Copper.
**Fix:** Don't use `BLTPRI` with copper effects. Complete blitter operations before timed copper sections.

### 7. Copper Disables Itself

**Symptom:** Copper stops mid-frame. All subsequent effects disappear.
**Cause:** A MOVE to `DMACON` with `COPEN` clear bit (and SET bit) disables Copper DMA.
**Fix:** When writing to `DMACON` from the Copper, always include the `COPEN` bit ($0080) in the SET word:
```asm
    ; Correct: toggle bitplane DMA without killing Copper
    dc.w    $096, $8210         ; DMACON: SET | DMAEN | BPLEN (enable bitplanes)
    ; Wrong: accidentally clears COPEN
    dc.w    $096, $8200         ; DMACON: SET | DMAEN — but no COPEN!
```

### 8. Modifying Copper List During Execution

**Symptom:** Random visual glitches, effects appearing on wrong lines.
**Cause:** CPU modifies copper list words that the Copper is currently reading or has already cached.
**Fix:** Modify copper list data during VBlank (after `WaitTOF()`) or use double-buffered lists.

---

## References

- **HRM:** *Amiga Hardware Reference Manual*, 3rd Edition — Chapter 6: The Copper
- **NDK 3.9:** `hardware/custom.h` (register definitions), `graphics/copper.h` (CINIT/CMOVE/CWAIT/CEND macros)
- **ADCD 2.1:** `graphics.library` autodocs — `UCopList`, `CINIT`, `CMOVE`, `CWAIT`, `CEND`

### Cross-References

- [Copper Quick Reference](copper.md) — instruction encoding and UCopList API at a glance
- [Copper Programming](copper_programming.md) — tutorial with step-by-step examples
- [OCS Copper](../../01_hardware/ocs_a500/copper.md) — OCS hardware register reference
- [AGA Copper](../../01_hardware/aga_a1200_a4000/aga_copper.md) — AGA enhancements and extended palette
- [Copper Effects](../../17_demoscene/copper_effects.md) — demoscene techniques: bars, gradients, sine cycling
- [Video Timing](../../01_hardware/common/video_timing.md) — beam counters, scanline anatomy, PAL/NTSC differences
- [DMA Architecture](../../01_hardware/common/dma_architecture.md) — DMA slot allocation, bus arbitration
- [Sprites](../sprites.md) — sprite DMA, multiplexing, attached sprites
- [Views](../views.md) — View/ViewPort/ColorMap pipeline (OS copper list integration)

### External Resources

- **Scoopex Amiga Hardware Programming** (Photon) — [YouTube: Copper tutorials](https://www.youtube.com/playlist?list=PLc3ltHgmiidpK-s0eP5hTKJnjdTHz0_bW)
- **coppershade.org** — [Articles on Copper techniques](http://coppershade.org/articles/)
- **Amiga Hardware Reference Manual** — [HRM at Archive.org](https://archive.org/details/amiga-hardware-reference-manual-3rd-edition)
