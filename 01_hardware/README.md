[← Home](../README.md)

# Hardware — Chipset Generation Overview

## Generation Comparison

| Feature | OCS | ECS | AGA |
|---|---|---|---|
| Agnus | 8361/8367 | 8372A (Super Agnus) | Alice (8374) |
| Denise | 8362 | 8373 (ECS Denise) | Lisa |
| Paula | 8364 | 8364 (unchanged) | 8364 (unchanged) |
| Max Chip RAM | 512 KB–1 MB | 1–2 MB | 2 MB |
| Colours (max normal) | 32 | 32 | 256 |
| HAM | 12-bit HAM (6bpp) | 12-bit HAM | 24-bit HAM8 (8bpp) |
| Sprites | 8 × 16px | 8 × 16px | 8 × 64px, 256 colours |
| Blitter bus | 16-bit | 16-bit | 64-bit (FMODE) |
| Display modes | NTSC/PAL | +Productivity, VGA | +Doublescan, 31kHz |
| Machines | A500/A1000/A2000/**CDTV** | A600/A3000/A500+ | A1200/A4000/A4000T/**CD32** |

---

## Custom Register Address Space

All chipset generations share the base address **$00DFF000** for custom registers. Registers are memory-mapped, mostly 16-bit wide.

```
$DFF000  BLTDDAT   Blitter destination early read
$DFF002  DMACONR   DMA control (read)
$DFF004  VPOSR     Vertical position (read, high)
...
$DFF180  COLOR00   Colour register 0
...
$DFF1FE  (last OCS/ECS register)
$DFF1FC  BEAMCON0  (ECS+) beam control
$DFF1FC+ (AGA extensions)
```

See [custom_registers_full.md](../references/custom_registers_full.md) for the complete table across all chipsets.

---

## Navigation

| Subfolder | Content |
|---|---|
| [common/](common/) | M68k CPU, address space layout, **memory types (Chip/Fast/Slow)**, CIA chips, Zorro bus, **Gayle IDE/PCMCIA** |
| [ocs_a500/](ocs_a500/) | OCS chipset — A500, **A1000 (WCS)**, **A2000 (Zorro II)**, **CDTV (CD-ROM, NVRAM, IR)** |
| [ecs_a600_a3000/](ecs_a600_a3000/) | ECS chipset — A600, A3000 (**Gary** system controller), A500+ |
| [aga_a1200_a4000/](aga_a1200_a4000/) | AGA chipset — A1200, A4000, **A4000T (SCSI)**, **CD32 (Akiko C2P, CD-ROM, NVRAM)** |

---

## References

- *Amiga Hardware Reference Manual* 3rd ed. — `Hardware_Manual_guide/` on ADCD 2.1
- ADCD 2.1: http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node0000.html
- AmigaMail Vol.2 — chipset programming articles
