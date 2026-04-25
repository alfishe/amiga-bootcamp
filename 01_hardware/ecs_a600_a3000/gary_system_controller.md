[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# Gary — A3000 System Controller

## Overview

**Gary** is the custom system controller chip in the Amiga 3000. It consolidates functions that are discrete ICs on the A2000 into a single gate array:

- **Bus controller**: Manages interaction between 68030/68882, chip bus, and Zorro III
- **Auto-config controller**: Runs Zorro expansion enumeration at boot
- **DMA arbitration**: Between 68030, custom chips, and Zorro III DMA masters
- **SCSI interface glue**: Works with the A3000's built-in WD33C93 SCSI controller
- **ROM decode**: Maps Kickstart ROM into the address space

Gary is not directly programmable by user software; its configuration is set by hardware strapping and the ROM initialisation sequence.

## Bus Arbitration

Gary manages three bus masters:

| Master | Priority | Description |
|---|---|---|
| Custom chips (DMA) | Highest | Agnus DMA for display, audio, disk — must never stall |
| 68030 CPU | Normal | Program execution |
| Zorro III cards | Lowest | Expansion bus-mastering DMA |

When a custom chip DMA cycle occurs, Gary holds the 68030 off the bus until the cycle completes. This is the fundamental source of "DMA contention" slowdown on all Amiga models.

## A3000 SCSI Integration

The A3000 includes a built-in **WD33C93A** SCSI controller. Gary provides the glue logic between the SCSI chip and the system bus:

| Feature | Details |
|---|---|
| SCSI chip | WD33C93A (SBIC) |
| DMA | SDMAC — dedicated SCSI DMA controller (separate from the CDTV-style DMAC) |
| Interface | A3000 uses a dedicated SDMAC chip, not the A2091-style DMAC |
| AmigaOS driver | `scsi.device` in Kickstart ROM |

> [!NOTE]
> The A3000's SDMAC is a different chip from the A2091/CDTV DMAC, despite both interfacing with WD33C93 SCSI controllers. The register layouts are incompatible.

## Machines Using Gary

| Model | Gary variant | Notes |
|---|---|---|
| A3000 | Original Gary | 68030, Zorro III, WD33C93 SCSI |
| A3000T | Gary (tower variant) | Same chip; tower form factor with more drive bays |

The A4000 does **not** use Gary — it uses a different system controller chip called **Ramsey** along with **Budgie** and **Buster** for bus management.

## References

- Commodore A3000 Technical Reference Manual
- ADCD 2.1 — Hardware Manual, A3000 chapter
- NDK39: hardware headers (community-documented Gary behaviour)

## See Also

- [Gayle — IDE & PCMCIA](../common/gayle_ide_pcmcia.md) — A600/A1200 storage controller (different chip, different function)
- [Zorro Bus](../common/zorro_bus.md) — Zorro II/III expansion managed by Gary
- [ECS Chipset](chipset_ecs.md) — Super Agnus + ECS Denise (A3000)
