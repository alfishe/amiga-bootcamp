[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# Gary & Gayle — System Controller Chips

## Gary (A3000)

**Gary** is the custom system controller chip in the A3000, combining functions that are discrete ICs on the A2000:

- **Bus controller**: Manages the interaction between 68030/68882, chip bus, and Zorro III
- **Auto-config controller**: Runs the Zorro expansion enumeration
- **DMA arbitration**: Between 68030, custom chips, and Zorro III DMA
- **SCSI interface glue**: Works with the A3000's built-in WD33C93 SCSI controller
- **ROM decode**: Maps Kickstart ROM into the address space

Gary is not directly programmable by user software; its configuration is set by hardware strapping and the ROM initialisation sequence.

## Gayle (A600 / A1200)

**Gayle** is the custom chip providing **IDE** and **PCMCIA** interface on the A600 and A1200. The A600 and A1200 use different Gayle revisions with different PCMCIA pinouts.

### Gayle Identification

```
A600 Gayle revision ID: read from $DA8000
A1200 Gayle revision ID: read from $DA8000
```

```asm
move.b  $DA8000, d0    ; Read Gayle ID byte
```

| Byte | Machine |
|---|---|
| $D0 | A600 Gayle |
| $D1 | A1200 Gayle (revision 1) |

### Gayle Register Map (A600/A1200)

| Address | Register | Description |
|---|---|---|
| $DA8000 | GAYLE_ID | Chip ID (read shifts bits) |
| $DA9000 | GAYLE_INT_STATUS | Interrupt status |
| $DA9004 | GAYLE_INT_ENABLE | Interrupt enable |
| $DA9008 | GAYLE_CONTROL | Control register |

### IDE Interface

The IDE interface via Gayle is at `$DA0000` (A1200) or `$DA0000` (A600):

| Offset | Register | Description |
|---|---|---|
| $DA0000 | DATA | IDE data register (16-bit) |
| $DA0004 | ERROR/FEATURE | Error (read) / Feature (write) |
| $DA0008 | SECTOR_COUNT | Sector count |
| $DA000C | SECTOR_NUMBER | Sector number (LBA 7:0) |
| $DA0010 | CYLINDER_LOW | Cylinder low (LBA 15:8) |
| $DA0014 | CYLINDER_HIGH | Cylinder high (LBA 23:16) |
| $DA0018 | DRIVE_HEAD | Drive/Head/LBA (LBA 27:24) |
| $DA001C | STATUS/COMMAND | Status (read) / Command (write) |
| $DA101C | ALT_STATUS | Alternate status (no interrupt clear) |
| $DA101C | DEVICE_CONTROL | Device control (write) |

> [!NOTE]
> On the A1200, IDE registers are byte-wide on odd addresses in a 16-bit window. The data register is 16-bit. This differs from standard PC IDE — byte lanes are swapped relative to x86 convention.

### PCMCIA Interface (A600/A1200)

The A600 and A1200 support a Type II PCMCIA (PC Card) slot:

| Address Range | Type | Description |
|---|---|---|
| $600000–$9FFFFF | Attribute memory | Card configuration (CIS access) |
| $A00000–$A3FFFF | Common memory | Modem/network card data |
| $A40000–$A7FFFF | Common memory (cont.) | |
| $600000 (Gayle) | Gayle attribute | Gayle own config space |

PCMCIA interrupt routing: Card interrupt → Gayle → CIA-A (`/FLG` pin) → CPU IPL 6.

### Gayle Interrupt Bits

```c
/* DA9000 GAYLE_INT_STATUS */
#define GAYLE_IRQ_IDE    (1<<6)  /* IDE drive interrupt */
#define GAYLE_IRQ_CARD   (1<<5)  /* PCMCIA card interrupt */
#define GAYLE_IRQ_BVD1   (1<<4)  /* PCMCIA battery voltage 1 */
#define GAYLE_IRQ_BVD2   (1<<3)  /* PCMCIA battery voltage 2 */
#define GAYLE_IRQ_WP     (1<<2)  /* PCMCIA write protect */
#define GAYLE_IRQ_CD     (1<<1)  /* PCMCIA card detect */
```

### Gayle Power Control

Gayle controls PCMCIA card power (5V / 3.3V on A1200 rev 1D+):
```c
/* GAYLE_CONTROL bits */
#define GAYLE_POW        (1<<7)  /* PCMCIA power on */
#define GAYLE_WS         (1<<6)  /* wait states for PCMCIA */
```

## AmigaOS IDE Access

AmigaOS accesses the Gayle IDE through the `scsi.device` or dedicated `ata.device` driver provided with OS 3.1+. Direct IDE programming is done in the filesystem handler (`trackdisk.device` replacement).

The standard path:
```
Application → dos.library → File System Handler → scsi.device → Gayle IDE
```

## References

- Commodore A600 Technical Reference Manual — Gayle chapter
- Commodore A1200 Technical Reference Manual — Gayle chapter
- ADCD 2.1 — `Devices_Manual_guide/` scsi.device
- NDK39: `hardware/gayle.h` (if present), community-documented Gayle registers
