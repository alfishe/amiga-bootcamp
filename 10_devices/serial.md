[← Home](../README.md) · [Devices](README.md)

# serial.device — UART and RS-232 Communication

## Overview

`serial.device` provides access to the Amiga's built-in UART (Universal Asynchronous Receiver/Transmitter) for RS-232 serial communication. The hardware UART is implemented using **CIA-B** shift registers and custom chip DMA. Serial I/O is fundamental for debugging (serial console), modem communication, MIDI, and inter-machine networking.

---

## Hardware

### Serial Port Pins (DB-25)

| Pin | Signal | Direction | Description |
|---|---|---|---|
| 2 | TxD | Output | Transmit data |
| 3 | RxD | Input | Receive data |
| 4 | RTS | Output | Request to send (active low) |
| 5 | CTS | Input | Clear to send (active low) |
| 6 | DSR | Input | Data set ready |
| 7 | GND | — | Signal ground |
| 8 | CD | Input | Carrier detect |
| 20 | DTR | Output | Data terminal ready |

### Custom Chip Registers

| Register | Address | Description |
|---|---|---|
| `SERDAT` | `$DFF030` | Serial data write (transmit) — 9 bits: stop bit + 8 data |
| `SERDATR` | `$DFF018` | Serial data read (receive) — status + received byte |
| `SERPER` | `$DFF032` | Serial period (baud rate divider) |
| `ADKCON` | `$DFF09E` | UARTBRK bit for break signal |

### Baud Rate Calculation

```c
/* SERPER value = (system_clock / baud_rate) - 1 */
/* PAL system clock for serial = 3,546,895 Hz */
/* NTSC = 3,579,545 Hz */

#define SERIAL_CLOCK_PAL   3546895
#define SERIAL_CLOCK_NTSC  3579545

UWORD serper_from_baud(ULONG baud, BOOL isPAL) {
    return (isPAL ? SERIAL_CLOCK_PAL : SERIAL_CLOCK_NTSC) / baud - 1;
}
```

| Baud Rate | SERPER (PAL) | SERPER (NTSC) |
|---|---|---|
| 1200 | 2955 | 2982 |
| 2400 | 1477 | 1491 |
| 9600 | 368 | 372 |
| 19200 | 184 | 185 |
| 31250 (MIDI) | 112 | 113 |
| 57600 | 60 | 61 |
| 115200 | 29 | 30 |

---

## Using serial.device

### Open and Configure

```c
struct MsgPort *serialPort = CreateMsgPort();
struct IOExtSer *serialReq = (struct IOExtSer *)
    CreateIORequest(serialPort, sizeof(struct IOExtSer));

/* Open serial.device unit 0: */
BYTE err = OpenDevice("serial.device", 0,
                       (struct IORequest *)serialReq, 0);

/* Configure: */
serialReq->io_SerFlags  = SERF_SHARED | SERF_XDISABLED;
serialReq->io_Baud      = 9600;
serialReq->io_ReadLen   = 8;     /* 8 data bits */
serialReq->io_WriteLen  = 8;
serialReq->io_StopBits  = 1;
serialReq->io_RBufLen   = 4096;  /* receive buffer size */
serialReq->IOSer.io_Command = SDCMD_SETPARAMS;
DoIO((struct IORequest *)serialReq);
```

### Write Data

```c
serialReq->IOSer.io_Command = CMD_WRITE;
serialReq->IOSer.io_Data    = "Hello Serial\r\n";
serialReq->IOSer.io_Length  = 14;
DoIO((struct IORequest *)serialReq);
```

### Read Data

```c
/* Check how many bytes are waiting: */
serialReq->IOSer.io_Command = SDCMD_QUERY;
DoIO((struct IORequest *)serialReq);
ULONG waiting = serialReq->IOSer.io_Actual;

if (waiting > 0) {
    serialReq->IOSer.io_Command = CMD_READ;
    serialReq->IOSer.io_Data    = buffer;
    serialReq->IOSer.io_Length  = waiting;
    DoIO((struct IORequest *)serialReq);
    /* buffer now contains received data */
}
```

### Serial Debugging

Many developers use a null-modem cable to a terminal for kernel debugging:

```c
/* Kprintf — ROM debug output via serial (ROMTags/exec): */
/* This bypasses serial.device entirely — writes directly to SERDAT */
void KPrintF(const char *fmt, ...);  /* available in debug ROMs */

/* Sushi/Sashimi — capture serial debug output on another Amiga */
```

---

## References

- NDK39: `devices/serial.h`
- HRM: *Amiga Hardware Reference Manual* — Serial Port chapter
- ADCD 2.1: serial.device autodocs
