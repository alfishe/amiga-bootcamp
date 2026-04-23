[← Home](../README.md) · [Graphics](README.md)

# Copper — Coprocessor Instructions and UCopList

## Overview

The **Copper** is a simple coprocessor in the Amiga custom chips that executes a list of instructions synchronised to the video beam. It can write to any custom chip register at any beam position, enabling per-scanline colour changes, split screens, and hardware-level display effects without CPU intervention.

---

## Instruction Format

The Copper has only three instructions, each 32 bits (one longword):

### MOVE — Write a Register

```
[register_offset (9 bits)] [value (16 bits)]
Bit layout: 0RRRRRRRR00000000 VVVVVVVVVVVVVVVV
```

- Register offset is relative to `$DFF000` (custom chip base)
- Only even registers can be written (bit 0 = 0)
- Example: `$0180, $0FFF` → write `$0FFF` to `COLOR00` (`$DFF180`)

### WAIT — Wait for Beam Position

```
[vpos (8 bits)] [hpos (7 bits)] [1] [vmask (7 bits)] [hmask (7 bits)] [0]
Bit layout: VVVVVVVVHHHHHH01 vvvvvvvvhhhhhhh0
```

- Pauses until the beam reaches at least the specified (vpos, hpos)
- Masks allow waiting on partial positions (e.g. any horizontal, specific vertical)

### SKIP — Conditional Skip

```
Same as WAIT but bit 0 of second word = 1
```

If the beam has already passed the specified position, skip the next instruction.

---

## Standard Copper Patterns

### Per-Scanline Colour Change (Rainbow)

```
WAIT   $2C01,$FFFE    ; wait for line $2C (44)
MOVE   $0180,$0F00    ; COLOR00 = red
WAIT   $2D01,$FFFE    ; wait for line $2D (45)
MOVE   $0180,$00F0    ; COLOR00 = green
WAIT   $2E01,$FFFE    ; wait for line $2E (46)
MOVE   $0180,$000F    ; COLOR00 = blue
...
WAIT   $FFDF,$FFFE    ; wait past line 255 (enables access to lines 256+)
WAIT   $FFFF,$FFFE    ; end-of-list (impossible position = halt)
```

### End of Copper List

```
$FFFF, $FFFE          ; WAIT for beam position $FFFF — never reached
```

This is the standard "stop" marker. The Copper loops back to the start on the next vertical blank.

---

## System Copper Lists

The OS manages copper lists through `GfxBase`:

| Pointer | Description |
|---|---|
| `GfxBase->copinit` | System initialisation copper list |
| `GfxBase->LOFlist` | Long-frame copper list (even fields) |
| `GfxBase->SHFlist` | Short-frame copper list (odd fields, interlace) |

---

## UCopList — User Copper Instructions

Applications can inject copper instructions into the system list via `UCopList`:

```c
struct UCopList *ucl = AllocMem(sizeof(struct UCopList), MEMF_PUBLIC|MEMF_CLEAR);

CINIT(ucl, 100);                    /* init, max 100 instructions */
CWAIT(ucl, 44, 0);                  /* wait for line 44 */
CMOVE(ucl, *((UWORD *)0xDFF180), 0x0F00); /* COLOR00 = red */
CWAIT(ucl, 100, 0);
CMOVE(ucl, *((UWORD *)0xDFF180), 0x000F); /* COLOR00 = blue */
CEND(ucl);                          /* end of list */

viewport->UCopIns = ucl;
RethinkDisplay();                   /* rebuild system copper list */
```

---

## Custom Chip Register Addresses (Copper-Relevant)

| Address | Name | Description |
|---|---|---|
| `$DFF180`–`$DFF1BE` | `COLOR00`–`COLOR31` | OCS/ECS palette (12-bit RGB) |
| `$DFF100` | `BPLCON0` | Bitplane control (depth, resolution) |
| `$DFF102` | `BPLCON1` | Scroll offsets |
| `$DFF104` | `BPLCON2` | Priority control |
| `$DFF08E` | `DIWSTRT` | Display window start |
| `$DFF090` | `DIWSTOP` | Display window stop |
| `$DFF092` | `DDFSTRT` | Data fetch start |
| `$DFF094` | `DDFSTOP` | Data fetch stop |
| `$DFF0E0`–`$DFF0FE` | `BPL1PT`–`BPL8PT` | Bitplane pointers |

---

## References

- HRM: *Amiga Hardware Reference Manual* — Copper chapter
- NDK39: `graphics/copper.h`, `graphics/gfxmacros.h`
- ADCD 2.1: `CINIT`, `CMOVE`, `CWAIT`, `CEND`
