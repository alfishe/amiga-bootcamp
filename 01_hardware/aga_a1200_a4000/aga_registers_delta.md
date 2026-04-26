[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Register Deltas vs ECS

## New Registers

### FMODE — $DFF1FC (AGA only)

DMA fetch mode — see [chipset_aga.md](chipset_aga.md) for full description.

### BPLCON4 — $DFF10C (AGA only)

Bitplane and sprite color bank selection:

```
bits 15-8:  BPLAM7-0  — Bitplane XOR pattern (AGA color bank XOR)
bits  7-4:  ESPRM7-4  — Even sprite color bank (bits 7:4 of color reg index)
bits  3-0:  OSPRM7-4  — Odd sprite color bank
```

**Bitplane bank select via BPLAM:**
- BPLAM provides an XOR mask applied to the 8-bit color index before palette lookup
- BPLAM = $00 → use COLOR00–COLOR63 (bank 0)
- BPLAM = $40 → use COLOR64–COLOR127 (bank 1)
- BPLAM = $80 → use COLOR128–COLOR191 (bank 2)
- BPLAM = $C0 → use COLOR192–COLOR255 (bank 3)

### COLOR00–COLOR255 — $DFF180–$DFF3BE (AGA)

AGA extends the color table from 32 registers (OCS/ECS) to **256 registers**.

Each AGA color register is 32 bits (accessed as two word writes via BPLCON3 latch):

```asm
; Write 24-bit color to COLOR00:
; First write sets high nibble, second sets low nibble
move.w  #$0000, BPLCON3+custom      ; set LACE=0, select low color word
move.w  #$0FFF, COLOR00+custom      ; write $RGB (high 12 bits)
bset    #9, BPLCON3_shadow           ; set LOCT (low nibble enable)
move.w  #$0FFF, COLOR00+custom      ; write low nibble of each channel
```

The standard `LoadRGB32()` and `LoadRGB4()` graphics library calls manage this transparently.

## Changed Registers

### BPLCON2 — $DFF104 (AGA extended)

```
bits 14-9:  KILLEHB  — kill EHB mode (AGA replaces EHB with 256 color)
bit    6:   RDRAM    — read bitplane data from RAM (not registered in Lisa)
bits   5-3: PF2PRI   — playfield 2 priority
bits   2-0: PF1PRI   — playfield 1 priority + sprite priority
```

### BPLCON3 — $DFF106 (AGA extended from ECS)

Additional AGA bits:
```
bit 9:    LOCT  — low color write enable (for 24-bit color access)
bit 3:    BRDSPRT — sprites visible in border
```

## AGA-Specific BPLCON0 Bits

See [chipset_aga.md](chipset_aga.md) — bit 4 is the MSB of the bitplane count for 7/8-plane modes.

## Color Register Access — Low Nibble Protocol

Writing 24-bit color to AGA registers requires two steps per color:

1. **Write high nibble** (standard): `COLOR00 = $0RGB` (bits [11:0] = R[3:0], G[3:0], B[3:0])
2. **Set LOCT** in BPLCON3 (bit 9)
3. **Write low nibble**: `COLOR00 = $0rgb` (bits [11:0] = R[3:0], G[3:0], B[3:0], these are the low 4 bits)

This two-write sequence gives 8 bits per channel (R[7:0], G[7:0], B[7:0]) = 24-bit color.

`LoadRGB32()` does this automatically:
```c
/* AGA 32-bit color table format:
   Count, then pairs: [color_index, 0x00RRGGBB] */
ULONG color_table[] = {
    32,   0,         /* 32 colors starting at index 0 */
    0x00FF0000,      /* COLOR00 = red */
    0x0000FF00,      /* COLOR01 = green */
    /* ... */
    ~0UL             /* terminator */
};
LoadRGB32(vp, color_table);
```

## References

- ADCD 2.1 Hardware Manual — AGA register appendix
- NDK39: `hardware/custom.h`, `graphics/view.h`
- Commodore A1200/A4000 Technical Reference Manuals
- AmigaMail Vol. 2 — AGA color programming
