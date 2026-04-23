[← Home](../../README.md) · [Hardware](../README.md) · [AGA](README.md)

# Gayle — A1200 IDE & PCMCIA

## Overview

The A1200 uses a different revision of **Gayle** than the A600. The A1200 Gayle integrates:
- **ATA/IDE interface** (for one hard drive + optional CD-ROM)
- **PCMCIA Type II** slot (for modems, network cards, RAM cards)
- **Interrupt routing** for both IDE and PCMCIA events

The A1200 Gayle is at a different base address layout than the A600 Gayle, and the byte-lane mapping differs from the A4000 IDE interface.

## Gayle ID

Read the Gayle ID by toggling read access to the ID register:
```c
#define GAYLE_ID_A1200  0xDA8000   /* read 8 bits, shifts on each access */

volatile UBYTE *gayle_id = (UBYTE *)0xDA8000;
UBYTE id_byte = *gayle_id;   /* returns $D0 (A600) or $D1 (A1200) */
```

## IDE Register Map (A1200)

The A1200 IDE registers are at `$DA0000`, but the byte lanes are **swapped** relative to standard AT/ATA convention — the 8-bit registers appear at odd byte offsets within each 4-byte window:

| A1200 Address | ATA Register | RW |
|---|---|---|
| $DA0000 | Data (16-bit) | RW |
| $DA0005 | Error (R) / Features (W) | RW |
| $DA0009 | Sector Count | RW |
| $DA000D | Sector Number (LBA 7:0) | RW |
| $DA0011 | Cylinder Low (LBA 15:8) | RW |
| $DA0015 | Cylinder High (LBA 23:16) | RW |
| $DA0019 | Drive/Head select (LBA 27:24) | RW |
| $DA001D | Status (R) / Command (W) | RW |
| $DA101D | Alternate Status (R) / Device Control (W) | RW |

> [!NOTE]
> The odd byte offset is because Gayle maps ATA registers on the **odd byte lane** of the 16-bit Amiga bus. Accessing `$DA0000+1` is the first register, not `$DA0000`. Many IDE drivers compensate with an offset of +1 or use a byte-swapped struct.

## Gayle Interrupt Register

```
$DA9000  GAYLE_INT_STATUS (read/write)
$DA9004  GAYLE_INT_ENABLE
```

```c
#define GAYLE_IRQ_IDE    (1<<7)  /* IDE interrupt pending */
#define GAYLE_IRQ_CARD   (1<<6)  /* PCMCIA interrupt */
#define GAYLE_IRQ_BVD1   (1<<5)
#define GAYLE_IRQ_BVD2   (1<<4)
#define GAYLE_IRQ_WP     (1<<3)  /* PCMCIA write protect */
#define GAYLE_IRQ_CD     (1<<2)  /* PCMCIA card detect */
```

Gayle routes its interrupt to **CIA-A /FLG** pin → CIAA ICR `CIAICRF_FLG` → CPU IPL 6.

Interrupt service routine must:
1. Check `GAYLE_INT_STATUS` to identify source (IDE or PCMCIA)
2. Clear the relevant bit by writing 0 to it
3. If IDE: read the ATA status register to clear the IDE INTRQ

## PCMCIA Interface (A1200)

The A1200 PCMCIA slot is at:

| Address | Content |
|---|---|
| $600000–$9FFFFF | PCMCIA attribute memory (card CIS) |
| $A00000–$A3FFFF | PCMCIA common memory (data) |

**Card detect sequence:**
1. A card insertion triggers `GAYLE_IRQ_CD` (bit 2)
2. Software reads CIS from attribute memory at $600000 to identify card type
3. For ATA cards: configure card mode via PCMCIA CIS `CONFIG` tuple
4. For network/modem cards: use the card's documented I/O mapping

## AmigaOS IDE Access

AmigaOS 3.1 includes `ata.device` (sometimes called `ide.device`) which drives the A1200 Gayle IDE internally. Applications never access Gayle registers directly — they go through dos.library → filesystem handler → ata.device.

```c
/* Standard path — no direct Gayle access needed: */
BPTR fh = Open("DH0:myfile", MODE_NEWFILE);
Write(fh, data, length);
Close(fh);
```

## References

- Commodore A1200 Technical Reference Manual — Gayle chapter (local archive)
- NDK39: (no official Gayle header — community documented)
- Amiga Hardware Reference (community supplement) — Gayle register map
- `scsi.device` / `ata.device` Autodocs on ADCD 2.1
