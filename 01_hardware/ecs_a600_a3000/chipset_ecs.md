[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# ECS Chipset Internals — Super Agnus & ECS Denise

## Super Agnus (MOS 8372A)

### Chip RAM Addressing

OCS Agnus could only generate 19-bit DMA addresses (512 KB) or 20-bit (1 MB with Fat Agnus). Super Agnus extends this to **21 bits**, addressing 2 MB of Chip RAM.

The revision of Super Agnus present determines the Chip RAM limit:

| Part | Chip RAM Max | Marking |
|---|---|---|
| 8372A rev 1 | 1 MB | AGNUS 8372A |
| 8372A rev 4+ | 2 MB | AGNUS 8372A (2MB) |

> [!NOTE]
> Software cannot assume 2 MB Chip RAM is available just because Super Agnus is present. The actual installed RAM amount must be checked via `AvailMem(MEMF_CHIP)`.

### Extended DMA Window

Super Agnus extends the bitplane DMA fetch window, allowing:
- Full overscan displays without copper tricks
- Access to the full 2 MB address range for all DMA channels

### AGNUS ID Register

Super Agnus provides an ID register readable via the `VPOSR` / `DIWSTRT` path. The chip revision can be read:

```asm
move.w  VPOSR+custom, d0    ; read VPOSR
lsr.w   #8, d0              ; shift to get Agnus ID in low byte
```

| VPOSR[15:8] | Chip | Notes |
|---|---|---|
| $00 | OCS Agnus 8367/8361 | Original |
| $10 | OCS Fat Agnus 8371 | 1 MB PAL |
| $20 | Super Agnus 8372A | ECS, 1 or 2 MB |
| $30 | Super Agnus 8372B | Some ECS |

---

## ECS Denise (MOS 8373)

### New Capabilities

ECS Denise adds to OCS Denise (8362):

1. **BPLCON3** — new control register for border color, sprite bank
2. **Sub-pixel scrolling** — additional scroll control bits
3. **Genlock extensions** — improved external sync handling
4. **Border blank** — BPLCON3 can blank the border area to color 0

### DENISEID — Revision Register

ECS Denise provides a self-identification register at `$DFF07C` (read only on ECS+):

```asm
move.w  $DFF07C, d0   ; read DENISEID
```

| Value | Chip |
|---|---|
| $FFFF | OCS Denise 8362 (register not present) |
| $00FC | ECS Denise 8373 |
| $00F8 | AGA Lisa |

---

## BPLCON3 — ECS Denise Extension

New register at `$DFF106` (ECS only, must not be written on OCS):

```
bit 15-13: BANK2-0    — sprite color bank (AGA: upper 4 bits of color reg)
bit 12-10: PF2OF2-0   — playfield 2 color offset (for dual playfield)
bit  9:    LOCT       — low color enable (AGA HAM8 mode)
bit  6:    BRDRBLNK   — border blank: forces border area to color 0
bit  5:    BRDNTRAN   — border not-transparent (disable border transparency)
bit  4:    ZDCLKEN     — horizontal/vertical count display
bit  3:    BRDSPRT    — sprites in border area enable
bit  2:    EXTBLKEN   — external blank signal
```

**Border blank use:**
```asm
move.w  #$0020, $DFF106   ; set BRDRBLNK — blank border area
```

---

## GfxBase ChipRevBits0 Flags

```c
/* graphics/gfxbase.h */
#define GFXB_BIG_BLITTER  0   /* ECS big blitter present */
#define GFXB_BLITTER_DMA  1
#define GFXB_HR_AGNUS     2   /* Super Agnus */
#define GFXB_HR_DENISE    3   /* ECS Denise */
#define GFXB_AA_ALICE     4   /* AGA Alice */
#define GFXB_AA_LISA      5   /* AGA Lisa */
```

Reading chipset type in C:
```c
UBYTE rev = GfxBase->ChipRevBits0;
BOOL is_ecs_agnus  = (rev & (1 << GFXB_HR_AGNUS)) != 0;
BOOL is_ecs_denise = (rev & (1 << GFXB_HR_DENISE)) != 0;
BOOL is_aga        = (rev & (1 << GFXB_AA_ALICE))  != 0;
```

## References

- ADCD 2.1 Hardware Manual — ECS registers, Super Agnus chapter
- NDK39: `graphics/gfxbase.h`
- AmigaMail Vol. 2 — ECS chipset programming articles
- *Amiga Hardware Reference Manual* 3rd ed. — Appendix F (ECS)
