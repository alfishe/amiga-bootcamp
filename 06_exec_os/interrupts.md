[← Home](../README.md) · [Exec Kernel](README.md)

# Interrupts — Levels, INTENA, AddIntServer, CIA Interrupts

## Overview

AmigaOS supports 7 hardware interrupt levels (68k IPL0–IPL6) plus a software interrupt mechanism. Custom chip interrupts are filtered through the `INTENA` / `INTREQ` registers; CIA-generated interrupts arrive on level 2 (CIA-A) and level 6 (CIA-B).

---

## Interrupt Priority Levels

| IPL | Source | AmigaOS Use |
|---|---|---|
| 1 | TBE, DSKBLK, SOFTINT | Software interrupts (`SoftInt`) |
| 2 | PORTS (CIA-A) | Keyboard, timer, parallel, floppy motor |
| 3 | COPER, VERTB, BLIT | Copper, vertical blank, blitter |
| 4 | AUD0–AUD3 | Audio DMA completion |
| 5 | RBF, DSKSYNC | Serial receive, disk sync |
| 6 | EXTER (CIA-B) | External interrupts, CIA-B timers, TOD |
| 7 | NMI | Non-maskable (unused on stock Amiga) |

---

## Custom Chip Interrupt Registers

| Register | Address | Description |
|---|---|---|
| `INTENAR` | `$DFF01C` | Interrupt enable status (read) |
| `INTENA` | `$DFF09A` | Interrupt enable set/clear (write) |
| `INTREQR` | `$DFF01E` | Interrupt request status (read) |
| `INTREQ` | `$DFF09C` | Interrupt request clear/set (write) |

### INTENA / INTREQ Bit Map

| Bit | Constant | Source |
|---|---|---|
| 0 | `INTF_TBE` | Serial transmit buffer empty |
| 1 | `INTF_DSKBLK` | Disk DMA block complete |
| 2 | `INTF_SOFTINT` | Software interrupt |
| 3 | `INTF_PORTS` | CIA-A interrupt (level 2) |
| 4 | `INTF_COPER` | Copper interrupt |
| 5 | `INTF_VERTB` | Vertical blank |
| 6 | `INTF_BLIT` | Blitter interrupt |
| 7 | `INTF_AUD0` | Audio channel 0 |
| 8 | `INTF_AUD1` | Audio channel 1 |
| 9 | `INTF_AUD2` | Audio channel 2 |
| 10 | `INTF_AUD3` | Audio channel 3 |
| 11 | `INTF_RBF` | Serial receive buffer full |
| 12 | `INTF_DSKSYNC` | Disk sync word match |
| 13 | `INTF_EXTER` | CIA-B / external interrupt |
| 14 | `INTF_INTEN` | Master interrupt enable bit |

To enable vertical blank: write `$C005` to `INTENA` (bit 14 set = enable, bit 5 = VERTB).
To clear vertical blank request: write `$0020` to `INTREQ`.

---

## Adding an Interrupt Server

```c
struct Interrupt myVBL = {
    { NULL, NULL, NT_INTERRUPT, 0, "My VBL" },
    NULL,        /* is_Data (passed to handler) */
    myVBLHandler /* is_Code */
};

AddIntServer(INTB_VERTB, &myVBL);  /* INTB_VERTB = 5 */
/* ... run ... */
RemIntServer(INTB_VERTB, &myVBL);  /* always remove before exit */
```

### Interrupt Handler Rules

- Handler is called at interrupt level — **no OS calls that Wait()**
- D0–D1, A0–A1 may be trashed; all others preserved
- Return D0 = 0 if you did not handle it (pass to next server)
- Return D0 ≠ 0 if you handled it (stop server chain)

Handler signature:
```asm
myVBLHandler:
    ; A1 = is_Data pointer (from struct Interrupt)
    ; do fast work only
    MOVEQ  #1, D0      ; handled — stop chain
    RTS
```

---

## CIA Interrupts

CIA-A (at `$BFEC01`) generates level 2 interrupts. CIA-B (at `$BFD000`) generates level 6. Each CIA has an ICR (Interrupt Control Register) with 5 sources:

| Bit | Source |
|---|---|
| 0 | Timer A underflow |
| 1 | Timer B underflow |
| 2 | TOD alarm |
| 3 | Serial register full |
| 4 | Flag pin / FLG |

CIA interrupts are serviced via AddIntServer on `INTB_PORTS` (level 2, CIA-A) or `INTB_EXTER` (level 6, CIA-B).

---

## Disable / Enable vs Forbid / Permit

| Function | Effect | Scope |
|---|---|---|
| `Forbid()` | Disables task switching | Task-level (interrupts still run) |
| `Permit()` | Re-enables task switching | Reverses `Forbid()` |
| `Disable()` | Masks all hardware interrupts | Hardware + task switching |
| `Enable()` | Unmasks hardware interrupts | Reverses `Disable()` |

> [!CAUTION]
> `Disable()` / `Enable()` can be held for only a few microseconds — never do I/O or complex operations inside a `Disable()` section.

---

## References

- NDK39: `hardware/intbits.h`, `hardware/cia.h`
- ADCD 2.1: `AddIntServer`, `RemIntServer`, `SetIntVector`, `Disable`, `Forbid`
- [cia_chips.md](../01_hardware/common/cia_chips.md) — CIA timer and ICR details
- [custom_registers.md](../01_hardware/ocs_a500/custom_registers.md) — INTENA/INTREQ register listing
