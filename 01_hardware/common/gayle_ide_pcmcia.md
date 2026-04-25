[← Home](../../README.md) · [Hardware](../README.md) · [Common](../common/)

# Gayle — IDE & PCMCIA Controller

## Overview

**Gayle** is Commodore's custom gate-array chip providing **ATA/IDE** hard drive and **PCMCIA Type II** card slot interfaces. It appears in two models with different silicon revisions:

| Model | Gayle ID | IDE | PCMCIA | Notes |
|---|---|---|---|---|
| **A600** | `$D0` | Yes (ECS system) | Yes | First Gayle implementation |
| **A1200** | `$D1` | Yes (AGA system) | Yes | Different byte-lane mapping |

The **CD32** does *not* have Gayle — its storage is handled by [Akiko](../aga_a1200_a4000/akiko_cd32.md).

The **A4000** uses a different IDE interface (directly on the motherboard, no Gayle chip).

## Gayle Identification

The Gayle ID register shifts one bit per read access:

```asm
    move.b  $DA8000, d0     ; Read Gayle ID byte
    ; d0 = $D0 → A600 Gayle
    ; d0 = $D1 → A1200 Gayle
```

```c
#define GAYLE_ID_ADDR  0xDA8000

volatile UBYTE *gayle_id = (UBYTE *)GAYLE_ID_ADDR;
UBYTE id_byte = *gayle_id;
/* $D0 = A600, $D1 = A1200 */
```

On machines without Gayle (A500, A2000, A3000, A4000, CD32), reading `$DA8000` returns bus noise — always check before assuming Gayle is present.

---

## Gayle Register Map

| Address | Register | R/W | Description |
|---|---|---|---|
| `$DA8000` | `GAYLE_ID` | R | Chip ID (shifts on each read access) |
| `$DA9000` | `GAYLE_INT_STATUS` | RW | Interrupt status (IDE + PCMCIA) |
| `$DA9004` | `GAYLE_INT_ENABLE` | RW | Interrupt enable mask |
| `$DA9008` | `GAYLE_CONTROL` | RW | Control register (PCMCIA power, wait states) |

---

## IDE Interface

### Register Maps — A600 vs A1200

The IDE registers are at base `$DA0000` on both models. The critical difference is **byte-lane mapping**: the A1200 places 8-bit ATA registers on **odd byte offsets** within each 4-byte window, while the A600 uses even offsets.

#### A600 IDE Registers

| Address | ATA Register | R/W |
|---|---|---|
| `$DA0000` | Data (16-bit) | RW |
| `$DA0004` | Error (R) / Features (W) | RW |
| `$DA0008` | Sector Count | RW |
| `$DA000C` | Sector Number (LBA 7:0) | RW |
| `$DA0010` | Cylinder Low (LBA 15:8) | RW |
| `$DA0014` | Cylinder High (LBA 23:16) | RW |
| `$DA0018` | Drive/Head (LBA 27:24) | RW |
| `$DA001C` | Status (R) / Command (W) | RW |
| `$DA101C` | Alternate Status / Device Control | RW |

#### A1200 IDE Registers

| Address | ATA Register | R/W |
|---|---|---|
| `$DA0000` | Data (16-bit) | RW |
| `$DA0005` | Error (R) / Features (W) | RW |
| `$DA0009` | Sector Count | RW |
| `$DA000D` | Sector Number (LBA 7:0) | RW |
| `$DA0011` | Cylinder Low (LBA 15:8) | RW |
| `$DA0015` | Cylinder High (LBA 23:16) | RW |
| `$DA0019` | Drive/Head (LBA 27:24) | RW |
| `$DA001D` | Status (R) / Command (W) | RW |
| `$DA101D` | Alternate Status / Device Control | RW |

> [!IMPORTANT]
> The A1200 byte-lane offset (+1 from A600) is because Gayle maps 8-bit ATA registers on the **odd byte lane** of the 16-bit Amiga bus. IDE drivers must account for this — a single driver cannot blindly use the same offsets for both machines. Check the Gayle ID first.

### PIO Data Transfer

IDE data transfers use 16-bit word access to the Data register:

```asm
; Read one sector (512 bytes = 256 words) from IDE
; a0 = destination buffer

    lea     $DA0000, a1         ; IDE data register
    move.w  #255, d0            ; 256 words
.read_loop:
    move.w  (a1), (a0)+         ; read word from IDE → buffer
    dbf     d0, .read_loop
```

---

## PCMCIA Interface

Both A600 and A1200 support a **Type II PCMCIA** (PC Card) slot:

| Address Range | Type | Description |
|---|---|---|
| `$600000`–`$9FFFFF` | Attribute memory | Card CIS (Card Information Structure) |
| `$A00000`–`$A3FFFF` | Common memory | Data / I/O window |
| `$A40000`–`$A7FFFF` | Common memory (cont.) | Extended data area |

### Card Insertion Sequence

1. Card insertion triggers `GAYLE_IRQ_CD` (card detect interrupt)
2. Software reads CIS from attribute memory at `$600000` to identify card type
3. Parse `CONFIG` tuple for card configuration
4. For **ATA cards** (CompactFlash in PCMCIA adapter): configure as IDE device
5. For **network/modem cards**: use card-specific I/O mapping
6. For **SRAM cards**: map as block device (up to 4 MB)

---

## Interrupt Handling

### Interrupt Routing

Gayle routes all its interrupts through **CIA-A** `/FLG` pin → `CIAICRF_FLG` → CPU **IPL 6** (INT6).

### Interrupt Status Bits

```c
/* $DA9000 GAYLE_INT_STATUS — read to check, write 0 to clear */
#define GAYLE_IRQ_IDE    (1<<7)  /* IDE drive interrupt (A1200) */
                                  /* bit 6 on A600 */
#define GAYLE_IRQ_CARD   (1<<6)  /* PCMCIA card interrupt */
#define GAYLE_IRQ_BVD1   (1<<5)  /* PCMCIA battery voltage detect 1 */
#define GAYLE_IRQ_BVD2   (1<<4)  /* PCMCIA battery voltage detect 2 */
#define GAYLE_IRQ_WP     (1<<3)  /* PCMCIA write protect */
#define GAYLE_IRQ_CD     (1<<2)  /* PCMCIA card detect */
```

> [!WARNING]
> The IDE interrupt bit position differs between A600 and A1200 Gayle revisions. Always check the Gayle ID register before masking interrupt bits.

### Interrupt Service Routine

```asm
; Gayle ISR (INT6 handler)
gayle_isr:
    move.b  $DA9000, d0         ; read GAYLE_INT_STATUS
    btst    #7, d0              ; IDE interrupt? (A1200)
    beq.s   .check_pcmcia
    
    ; Handle IDE interrupt
    move.b  $DA001D, d1         ; read ATA status to clear INTRQ
    bclr    #7, $DA9000         ; clear Gayle IDE IRQ
    bra.s   .done
    
.check_pcmcia:
    btst    #6, d0              ; PCMCIA interrupt?
    beq.s   .done
    ; Handle PCMCIA...
    bclr    #6, $DA9000         ; clear PCMCIA IRQ
    
.done:
    rte
```

---

## PCMCIA Power Control

Gayle controls PCMCIA card power (5V standard; 3.3V on A1200 rev 1D+):

```c
/* $DA9008 GAYLE_CONTROL bits */
#define GAYLE_POW   (1<<7)  /* PCMCIA power on/off */
#define GAYLE_WS    (1<<6)  /* Wait states for PCMCIA access */
```

---

## AmigaOS IDE Access

AmigaOS accesses Gayle IDE through the standard device driver stack:

```
Application → dos.library → File System Handler → scsi.device / ata.device → Gayle IDE
```

Applications never access Gayle registers directly:

```c
/* Standard file access — no direct Gayle interaction */
BPTR fh = Open("DH0:myfile", MODE_NEWFILE);
Write(fh, data, length);
Close(fh);
```

The A600 uses `scsi.device` from Kickstart ROM. The A1200 uses `ata.device` (also called `ide.device` in some OS versions) which includes A1200-specific byte-lane handling.

---

## References

- Commodore A600 Technical Reference Manual — Gayle chapter
- Commodore A1200 Technical Reference Manual — Gayle chapter
- NDK39: community-documented Gayle registers (no official header)
- ADCD 2.1: `scsi.device` / `ata.device` Autodocs
- [Big Book of Amiga Hardware](https://bigbookofamigahardware.com/) — Gayle pinout and board photos

## See Also

- [Akiko — CD32 Custom Chip](../aga_a1200_a4000/akiko_cd32.md) — CD32 uses Akiko instead of Gayle
- [Gary — A3000 System Controller](../ecs_a600_a3000/gary_system_controller.md) — A3000 bus controller (no IDE)
- [CIA Chips](cia_chips.md) — Gayle routes interrupts through CIA-A
- [Memory Types](memory_types.md) — IDE storage as expansion path
