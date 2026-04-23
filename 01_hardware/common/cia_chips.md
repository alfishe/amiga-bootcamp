[← Home](../../README.md) · [Hardware](../README.md)

# CIA Chips — 8520 MOS Technology

## Overview

The Amiga uses **two MOS 8520 CIA** (Complex Interface Adapter) chips, providing timers, parallel/serial I/O ports, a time-of-day clock, and interrupt generation. They are the primary source of hardware timing outside the vertical blank and audio DMA.

- **CIA-A** at `$BFE001` (even byte addresses)
- **CIA-B** at `$BFD000` (odd byte addresses)

Both CIAs are accessed via byte reads/writes; the 68000 byte-lane placement means CIA-A uses even offsets and CIA-B uses odd offsets on the 16-bit bus.

## Register Map

Each CIA has 16 registers, spaced 256 bytes apart in the Amiga address space:

| Offset | Register | CIA-A Function | CIA-B Function |
|---|---|---|---|
| $000 | PRA | Parallel port data (input) | Disk control outputs |
| $100 | PRB | Parallel port data (output) | Disk status inputs |
| $200 | DDRA | Port A direction (1=output) | Port A direction |
| $300 | DDRB | Port B direction | Port B direction |
| $400 | TALO | Timer A low byte | Timer A low byte |
| $500 | TAHI | Timer A high byte | Timer A high byte |
| $600 | TBLO | Timer B low byte | Timer B low byte |
| $700 | TBHI | Timer B high byte | Timer B high byte |
| $800 | TODLO | TOD clock low (1/60 s) | Disk position (latched) |
| $900 | TODMID | TOD clock mid | |
| $A00 | TODHI | TOD clock high | |
| $B00 | (unused) | — | — |
| $C00 | SDR | Serial data register | Serial data register |
| $D00 | ICR | Interrupt control | Interrupt control |
| $E00 | CRA | Control register A | Control register A |
| $F00 | CRB | Control register B | Control register B |

## CIA-A: $BFE001

CIA-A handles:

| Bit | Port A (PRA, read $BFE001) |
|---|---|
| 7 | `/FIR1` — joystick port 1 button |
| 6 | `/FIR0` — joystick port 0 button |
| 5 | `/RDY` — floppy ready |
| 4 | `/TK0` — track 0 sensor |
| 3 | `/WPRO` — write-protect |
| 2 | `/CHNG` — disk change |
| 1 | `/LED` — power LED (write: 0=bright) |
| 0 | `/OVL` — Chip RAM overlay (write during boot) |

Port B (PRB, $BFE101): Parallel port data lines D0–D7.

**CIA-A interrupts** appear on **CPU IPL level 2** via INTENA bit `INTB_EXTER` — actually CIA is on IPL 6.

## CIA-B: $BFD000

CIA-B handles floppy drive motor/selection and disk DMA sync:

| Bit | Port A (PRA, $BFD000) |
|---|---|
| 7 | `/MTR` — motor on/off |
| 6 | `/SEL3` — drive 3 select |
| 5 | `/SEL2` — drive 2 select |
| 4 | `/SEL1` — drive 1 select |
| 3 | `/SEL0` — drive 0 select |
| 2 | `/SIDE` — head side (0=upper) |
| 1 | `/DIR` — step direction |
| 0 | `/STEP` — step pulse |

Port B (PRB, $BFD100): Parallel port shadow (less commonly used on B).

**CIA-B interrupts** appear on **CPU IPL level 6**.

## Timers

Each CIA has two 16-bit countdown timers (Timer A and Timer B):

- Count from a loaded latch value down to zero
- Can be one-shot or continuous
- Clock sources: system clock (709 kHz PAL / 715 kHz NTSC), or Timer A output (for Timer B)
- Timer A can generate `SDR` baud rate for serial output

**Control Register A (CRA) bits:**
```
bit 0: START  — 1 = timer running
bit 1: PBON   — 1 = timer output on Port B bit 6
bit 2: OUTMODE — 0=pulse, 1=toggle
bit 3: RUNMODE — 0=continuous, 1=one-shot
bit 4: LOAD   — 1 = force load latch into counter
bit 5: INMODE — 0=clock, 1=count rising edges on CNT pin
bit 6: SPMODE — 0=SDR input, 1=SDR output
bit 7: TODIN  — 0=60 Hz TOD, 1=50 Hz TOD (PAL)
```

## Time-of-Day (TOD) Clock

24-bit counter, clocked at 60 Hz (NTSC) or 50 Hz (PAL):

- CIA-A TOD: used by OS as software clock
- TOD registers latch on read of TODHI — must read TODHI first, then TODMID, then TODLO
- `ciaa.ciatodhi` → `ciaa.ciatodmid` → `ciaa.ciatodlo`
- Set by writing TODHI → TODMID → TODLO (halts during write)

## Interrupt Control Register (ICR)

Write to enable interrupts, read to see which fired:

```c
/* Enable Timer A interrupt */
ciaa.ciaicr = CIAICRF_SETCLR | CIAICRF_TA;

/* On read: bits indicate which sources fired */
UBYTE icr = ciaa.ciaicr;
if (icr & CIAICRF_TA) { /* Timer A fired */ }
if (icr & CIAICRF_TB) { /* Timer B fired */ }
if (icr & CIAICRF_ALRM) { /* TOD alarm fired */ }
if (icr & CIAICRF_SP) { /* Serial register full/empty */ }
if (icr & CIAICRF_FLG) { /* /FLAG pin (index pulse on CIA-B) */ }
```

Write bit 7 (`CIAICRF_SETCLR`): 1 = set enable bits, 0 = clear enable bits.

## AmigaOS Timer Device Integration

AmigaOS's `timer.device` uses CIA timers internally:
- `UNIT_MICROHZ` — uses CIA-A Timer A for microsecond delays
- `UNIT_VBLANK` — uses vertical blank interrupt (not CIA)
- `UNIT_ECLOCK` — uses the E clock (709/715 kHz, same as CIA clock)

Direct CIA programming should be done with `ciaa`/`ciab` resource claims via `OpenResource("ciaa.resource")` — not by poking CIA registers directly.

## C Access via NDK Headers

```c
#include <hardware/cia.h>
#include <resources/cia.h>

/* CIA-A is at fixed address */
#define ciaa (*((volatile struct CIA *)0xBFE001))
#define ciab (*((volatile struct CIA *)0xBFD000))

/* struct CIA fields (hardware/cia.h): */
/* ciaa.ciapra, ciaa.ciaprb, ciaa.ciaicr, ciaa.ciacra, ... */
```

## References

- MOS Technology 6526/8520 datasheet
- ADCD 2.1 Hardware Manual — CIA chapter: http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/
- NDK39: `hardware/cia.h`, `resources/cia.h`
- Autodocs: `cia` resource — http://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node00C7.html
