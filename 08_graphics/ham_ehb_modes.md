[← Home](../README.md) · [Graphics](README.md)

# HAM and EHB — Special Display Modes

## Overview

The Amiga offers two unique display modes that squeeze many more colours from limited bitplane hardware: **EHB** (Extra Half-Brite) and **HAM** (Hold-And-Modify). These modes have no direct equivalent on other platforms and are critical for understanding Amiga graphics capability.

---

## EHB — Extra Half-Brite (OCS/ECS/AGA)

### How It Works

Uses **6 bitplanes** (64 possible values):
- Bitplane values 0–31: index into the 32-colour palette normally
- Bitplane values 32–63: display the colour from register (value − 32) at **half brightness** (all RGB components halved)

```
Bitplanes 0–4 → 5-bit colour index (0–31)
Bitplane 5    → "half brightness" flag
```

### Effective Result

- 32 programmer-defined colours + 32 fixed half-brightness versions = **64 colours**
- Zero additional palette RAM needed
- Useful for shadows and smooth gradients

### Enabling EHB

```c
/* In ViewPort ColorMap: */
/* Simply use 6 bitplanes with no HAM flag */
struct BitMap bm;
InitBitMap(&bm, 6, 320, 256);  /* 6 planes */
/* No EXTRA_HALFBRITE flag needed — it's automatic when depth=6 */
```

---

## HAM — Hold-And-Modify (OCS/ECS)

### How It Works

Uses **6 bitplanes**. Each pixel's 6 bits are interpreted as:

| Bits 5–4 | Meaning | Bits 3–0 |
|---|---|---|
| `00` | **SET** — index colour register | 4-bit palette index (0–15) |
| `01` | **MODIFY BLUE** — hold R,G; set B | New blue nibble |
| `10` | **MODIFY RED** — hold G,B; set R | New red nibble |
| `11` | **MODIFY GREEN** — hold R,B; set G | New green nibble |

### Effective Result

- Each pixel can set one of 16 base colours, OR modify one component of the previous pixel's colour
- Theoretical maximum: **4,096 colours** on screen simultaneously
- Practical result: colour fringing at sharp edges (each pixel depends on its left neighbour)

### OCS/ECS Limitations

- Only 16 base colours (SET mode uses 4 bits → 16 palette entries)
- Only 4-bit component modification → 16 levels per channel
- Total colour space: 12-bit (4096 colours)

---

## HAM8 — AGA Enhanced HAM

### How It Works

Uses **8 bitplanes**:

| Bits 7–6 | Meaning | Bits 5–0 |
|---|---|---|
| `00` | **SET** — index colour register | 6-bit palette index (0–63) |
| `01` | **MODIFY BLUE** | 6-bit blue value |
| `10` | **MODIFY RED** | 6-bit red value |
| `11` | **MODIFY GREEN** | 6-bit green value |

### Effective Result

- 64 base colours from the 256-entry palette
- 6-bit component modification → 64 levels per channel
- Total colour space: **18-bit** (262,144 colours)
- Significantly reduced fringing compared to HAM6

### HAM8 Memory Layout

```
8 bitplanes × 320 pixels × 256 lines = 81,920 bytes per plane × 8
= 655,360 bytes (640 KB) for a single HAM8 320×256 display
```

---

## Enabling HAM

```c
/* Via ViewPort: */
vp->Modes |= HAM;  /* HAMF flag in modes */

/* Via SA_ tags (Intuition screen): */
struct TagItem scrTags[] = {
    { SA_Width,      320 },
    { SA_Height,     256 },
    { SA_Depth,      6 },         /* 6 for HAM6, 8 for HAM8 */
    { SA_DisplayID,  HAM_KEY },   /* or SUPER_KEY|HAM for Super-HiRes HAM */
    { TAG_DONE, 0 }
};
```

---

## Comparison Table

| Feature | EHB | HAM6 | HAM8 |
|---|---|---|---|
| Bitplanes | 6 | 6 | 8 |
| Chipset | OCS/ECS/AGA | OCS/ECS/AGA | AGA only |
| Base palette | 32 | 16 | 64 |
| Max on-screen colours | 64 | 4,096 | 262,144 |
| Colour depth | 12-bit | 12-bit | 24-bit (via 18-bit HAM) |
| Fringing | None | Significant | Mild |
| Good for | GUI, sprites | Photos, static art | Photos, video stills |
| Bad for | — | Animation, scrolling | Memory-hungry |

---

## References

- HRM: *Display modes* chapter
- NDK39: `graphics/displayinfo.h` — `HAM_KEY`, `EXTRAHALFBRITE_KEY`
