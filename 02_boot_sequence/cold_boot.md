[← Home](../README.md) · [Boot Sequence](README.md)

# Cold Boot — Power-On to Kickstart

## Overview

When the Amiga powers on or is reset (Ctrl-Amiga-Amiga), the 68000 CPU begins execution from the ROM. The boot process progresses from raw hardware init through to a fully running AmigaOS desktop in approximately 3–8 seconds.

---

## Hardware Initialisation (Pre-ROM)

### 1. CPU Reset Vector

The 68000 reads two longwords from address `$000000`:
```
$000000: Initial SSP (Supervisor Stack Pointer)
$000004: Initial PC (Program Counter) → ROM entry point
```

On Amiga, these locations map to Kickstart ROM at `$FC0000` (256 KB) or `$F80000` (512 KB). The ROM image contains:
- Word 0–1: SSP value (typically `$000400`)
- Word 2–3: PC value → ROM entry point

### 2. ROM Checksum

First code executed: compute checksum of entire ROM. If it fails → **red screen of death** (solid red background, no further boot).

```
Checksum: simple 32-bit additive checksum of all ROM longwords.
Result must equal $FFFFFFFF (complement to zero).
The last longword of the ROM is the complement value.
```

### 3. Chip Register Reset

```
- Write $7FFF to INTENA ($DFF09A) — disable all interrupts
- Write $7FFF to INTREQ ($DFF09C) — clear all pending interrupts
- Write $7FFF to DMACON ($DFF096) — disable all DMA
- CIA chips: reset timer, serial, port registers
```

### 4. Memory Detection

The ROM probes for available memory:
```
1. Test Chip RAM at $000000 by writing test patterns
2. Size Chip RAM: 256 KB, 512 KB, 1 MB, or 2 MB
3. Probe for Fast RAM at $C00000 (Ranger), $200000 (Slow/Ranger)
4. Probe for Zorro II auto-config space at $E80000
5. Probe for 32-bit fast RAM at $07000000+ (Zorro III)
```

### 5. Display Diagnostic Colours

During boot, the background colour indicates progress:

| Colour | Stage |
|---|---|
| Dark grey | ROM checksum passed |
| Light grey | Chip RAM sized |
| White | ExecBase initialised |
| Green flash | DOS boot starting |
| **Red** | ROM checksum fail |
| **Yellow** | Chip RAM test fail |
| **Blue** | Alert (Guru Meditation) |

---

## ROM Layout

### 256 KB ROM (Kickstart 1.x)

```
$FC0000–$FFFFFF  (256 KB)
  $FC0000: Reset vectors (SSP + PC)
  $FC0008: ROM header (version, checksum)
  ...
  $FC0020: First resident module (exec.library)
  ...
  $FFFFFC: Checksum complement word
```

### 512 KB ROM (Kickstart 2.0+)

```
$F80000–$FFFFFF  (512 KB)
  $F80000: Reset vectors
  $F80008: ROM header
  ...
  $F80020: exec.library resident tag
  ...
  $FFFFFC: Checksum complement
```

---

## References

- RKRM: *Hardware Reference Manual* — reset chapter
