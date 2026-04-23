[← Home](../README.md) · [Overview](README.md)

# Amiga Hardware Models Reference

## Model Specification Table

| Model | Year | CPU | MHz | Chipset | Chip RAM | ROM | Expansion |
|---|---|---|---|---|---|---|---|
| A1000 | 1985 | 68000 | 7.14 | OCS | 256 KB | 256 KB | Sidecar |
| A500 | 1987 | 68000 | 7.09 | OCS | 512 KB | 256 KB | Edge connector |
| A2000 | 1987 | 68000 | 7.14 | OCS/ECS | 512 KB–1 MB | 256/512 KB | Zorro II, ISA, CPU slot |
| A500+ | 1991 | 68000 | 7.09 | ECS | 1 MB | 512 KB | Edge connector |
| A600 | 1992 | 68000 | 7.09 | ECS | 1 MB | 512 KB | PCMCIA, IDE, trapdoor |
| A3000 | 1990 | 68030 | 16/25 | ECS | 1 MB | 512 KB | Zorro III, ISA, SCSI |
| A1200 | 1992 | 68020 | 14.18 | AGA | 2 MB | 512 KB | PCMCIA, IDE, trapdoor |
| A4000 | 1992 | 68030/040 | 25 | AGA | 2 MB | 512 KB | Zorro III, IDE |
| A4000T | 1994 | 68040/060 | 25 | AGA | 2 MB | 512 KB | Zorro III, SCSI |
| CD32 | 1993 | 68020 | 14.18 | AGA | 2 MB | 512 KB | SX-1, CD-ROM |

## CPU Feature Matrix

| CPU | Bus | Address | I-Cache | D-Cache | MMU | FPU |
|---|---|---|---|---|---|---|
| 68000 | 16-bit | 24-bit | — | — | — | External 68881 |
| 68020 | 32-bit | 32-bit | 256 B direct | — | External 68851 | External 68881/2 |
| 68030 | 32-bit | 32-bit | 256 B | 256 B | On-chip | External 68882 |
| 68040 | 32-bit | 32-bit | 4 KB 4-way | 4 KB 4-way | On-chip | On-chip (partial) |
| 68060 | 32-bit | 32-bit | 8 KB 4-way | 8 KB 4-way | On-chip | On-chip (partial) |

> [!NOTE]
> 68040 and 68060 have on-chip FPUs that omit transcendental instructions. AmigaOS provides `68040.library` and `68060.library` to trap the missing opcodes via Line-F emulation.

## Kickstart ROM Sizes

| OS Version | ROM Size | Part | Models |
|---|---|---|---|
| 1.2 / 1.3 | 256 KB | Single | A500, A2000 |
| 2.04 | 512 KB | Single | A500+, A600, A3000 |
| 3.0 / 3.1 | 512 KB | Single | A1200, A4000 |
| 3.1 | 512 KB + 512 KB Ext | Pair | A4000 (with ext ROM) |

## References

- Commodore *A1200 Technical Reference Manual* — `Documentation/A1200/` local archive
- Commodore *A4000 Technical Reference Manual* — `Documentation/A4000/` local archive
- ADCD 2.1 Hardware Manual: http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node0000.html
