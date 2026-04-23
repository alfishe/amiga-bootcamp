[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# AGA Chipset Internals — Alice & Lisa

## Alice (MOS 8374) — AGA Agnus

Alice is the successor to Super Agnus and is the DMA controller and Copper/Blitter engine for AGA machines.

### Key Enhancements over Super Agnus

**64-bit DMA fetch bus (FMODE):**
Alice can fetch 2 or 4 words per DMA cycle via the `FMODE` register ($DFF1FC). This dramatically increases the bandwidth available to the blitter and bitplane DMA.

**Extended bitplane depth:**
Alice supports up to **8 bitplanes** (256 colours), compared to OCS/ECS's 6-plane limit.

**BPLCON4:**
Alice adds `BPLCON4` to control bitplane bank selection — which 64-entry block of the 256-entry colour table is used by the bitplanes.

### ALICE_ID

Alice can be identified via `VPOSR`:
```asm
move.w  $DFF004, d0    ; VPOSR
lsr.w   #8, d0
```

| VPOSR[15:8] | Chip |
|---|---|
| $22 | Alice AGA (standard) |
| $23 | Alice AGA (some A4000 revisions) |

---

## Lisa (AGA Denise)

Lisa is the display chip successor to ECS Denise, providing 8-bit colour output (256 colour registers) and extended sprite capabilities.

### Key Enhancements over ECS Denise

**256 colour registers:**
Lisa provides COLOR00–COLOR255, each 24-bit (32-bit register with low byte unused).

**4 colour banks for bitplanes:**
`BPLCON4` selects which 64-register bank (0–3) the bitplanes use for lookup. This allows dual-playfield each using a different 64-colour palette.

**Sprite bank selection:**
`BPLCON3` bits select which colour bank sprite pairs use.

**Extended sprite width:**
Sprites can be 16 or 64 pixels wide in AGA mode.

**Lisa ID:**
Readable from `$DFF07C` (DENISEID):
```asm
move.w  $DFF07C, d0   ; DENISEID = $00F8 for AGA Lisa
```

---

## FMODE — DMA Fetch Width Register ($DFF1FC)

The most critical AGA-specific register. Controls the data bus width for blitter and bitplane DMA:

```
bits 15-14:  SPR_FMODE   — sprite fetch mode
bits 13-12:  BPL_FMODE   — bitplane fetch mode
bits  9-8:   BLT_FMODE   — blitter fetch mode

00 = 1× (16-bit, OCS/ECS compatible)
01 = 2× (32-bit)
10 = 4× (64-bit)
11 = reserved
```

**Setting full 64-bit blitter mode:**
```asm
move.w  #$00C0, $DFF1FC   ; FMODE: BLT_FMODE=11 (64-bit)
; Also set BPL and SPR modes as needed
```

> [!CAUTION]
> Writing FMODE on OCS/ECS machines writes to the `LISAID` location (read-only) — no hardware damage, but the read-back value is incorrect. Always verify AGA presence before writing FMODE.

---

## DMA Bandwidth with FMODE

| FMODE | Bus width | Blitter speed | Bitplane DMA |
|---|---|---|---|
| 1× (OCS compat) | 16-bit | 1× | 1× |
| 2× | 32-bit | 2× | 2× |
| 4× | 64-bit | 4× | 4× |

At 4× mode, the AGA blitter can fill/copy at ~70 MB/s theoretical on a 7 MHz bus.

---

## BPLCON0 Extended Bits (AGA)

In AGA mode, `BPLCON0` bit 4 (`ECSENA`) must be **1** to enable AGA features. Additional BPU bit (bit 4 of the count) allows 7 and 8 planes:

```
bits 14-12: BPU2-0 — lower 3 bits of bitplane count
bit   4:    BPU3   — MSB of bitplane count (AGA: allows 7, 8 planes)
```

To use 8 bitplanes (256 colours):
```asm
move.w  #$9411, BPLCON0+custom  ; HIRES=1 (if needed), BPU=8 (BPU3=1, BPU2-0=000), ECSENA=1
```

---

## References

- ADCD 2.1 Hardware Manual — AGA chapter
- NDK39: `hardware/custom.h` — struct Custom (with AGA extensions)
- Commodore A1200 Technical Reference Manual — Alice/Lisa section
- AmigaMail Vol. 2 — AGA programming articles
