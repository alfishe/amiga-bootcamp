[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# Paula — Serial Port

## Overview

**Paula** contains a hardware UART (Universal Asynchronous Receiver/Transmitter) for the Amiga's serial port. It is a simple, non-buffered serial interface — no FIFO, single transmit and single receive register.

The serial port operates at **RS-232 voltage levels** (via external level shifter on the A500/A1000). The A2000 and A3000 route through a MAX232 equivalent.

## Registers

| Register | Offset | Dir | Description |
|---|---|---|---|
| SERPER | $DFF032 | W | Serial period and word length |
| SERDAT | $DFF030 | W | Serial data transmit |
| SERDATR | $DFF018 | R | Serial data receive + status |

## SERPER — Baud Rate Configuration

```
bit 15:    LONG — 0 = 8-bit words, 1 = 9-bit words
bit 14-0:  Period — clock divider for baud rate
```

**Baud rate formula:**
```
Baud = System clock / (Period + 1)
```

| Baud Rate | PAL Period | NTSC Period |
|---|---|---|
| 300 | 11811 | 11929 |
| 1200 | 2952 | 2981 |
| 2400 | 1476 | 1490 |
| 4800 | 737 | 745 |
| 9600 | 368 | 372 |
| 19200 | 183 | 186 |
| 38400 | 91 | 92 |
| 115200 | 30 | 30 |

## SERDAT — Transmit

```
bit 15-11: Must be 1 (stop bits framing)
bit 10:    Stop bit
bit 9-0:   Data word (8 or 9 bits, MSB first relative to wire)
```

To transmit a byte (8-bit mode):
```asm
; Wait for TBE (transmit buffer empty) interrupt or poll
WaitTBE:
    btst    #0, SERDATR+1    ; TBE = bit 0 of SERDATR high byte... 
                              ; Actually check INTREQR bit TBE
    beq.s   WaitTBE

; Send byte $41 ('A'), 8-bit framing: $3C01 prefix + data
move.w  #($3FC0 | 0x41), SERDAT+custom
```

Correct framing for 8-bit word:
```
SERDAT = $3C00 | byte_value    ; bits[15:10] = %111111 (stop + start framing)
```

## SERDATR — Receive

```
bit 15: OVRUN — overrun error (data was not read before next byte arrived)
bit 14: RBF   — receive buffer full (data ready to read)
bit 13: TBE   — transmit buffer empty
bit 12: TSRE  — transmit shift register empty
bit 11: RXD   — current state of RXD pin
bit  9: STP   — stop bit of received word
bit 8-0: Data — received byte (8 or 9 bits)
```

Read a byte:
```c
/* Wait for RBF */
while (!(custom.serdatr & SERDATF_RBF))
    ;
UBYTE ch = custom.serdatr & 0xFF;

/* Acknowledge interrupt */
custom.intreq = INTF_RBF;
```

## Interrupt Sources

| Event | INTENA/INTREQ bit | IPL |
|---|---|---|
| TBE (transmit buffer empty) | bit 0 `INTF_TBE` | 1 |
| RBF (receive buffer full) | bit 11 `INTF_RBF` | 5 |

RBF fires at IPL 5 — relatively high priority, since the receive register has no FIFO and an overrun loses data.

## serial.device

AmigaOS provides `serial.device` for managed serial access:
- Supports baud rates, parity, stop bits, word length
- Provides buffered read/write via `IOExtSer` structure
- Handles `CMD_READ`, `CMD_WRITE`, `SDCMD_SETPARAMS`, `SDCMD_QUERY`
- Multiple opens are not supported — one opener at a time

```c
#include <devices/serial.h>

struct IOExtSer *ser_req; /* allocated IOExtSer */
OpenDevice("serial.device", 0, (struct IORequest *)ser_req, 0);

ser_req->io_Baud      = 9600;
ser_req->io_RBufLen   = 4096;
ser_req->IOSer.io_Command = SDCMD_SETPARAMS;
DoIO((struct IORequest *)ser_req);
```

## References

- ADCD 2.1 Hardware Manual — Paula serial section
- NDK39: `hardware/custom.h`, `devices/serial.h`
- Autodocs: serial.device — http://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node013E.html
