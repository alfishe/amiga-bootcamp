[← Home](../README.md) · [Devices](README.md)

# serial.device — RS-232 Communication

## Overview

`serial.device` provides buffered RS-232 serial I/O through the Amiga's built-in 8520 CIA UART (active-high active sense).

---

## Opening

```c
struct IOExtSer *ser = (struct IOExtSer *)
    CreateIORequest(port, sizeof(struct IOExtSer));
OpenDevice("serial.device", 0, (struct IORequest *)ser, 0);
```

---

## Setting Parameters

```c
ser->io_CtlChar   = SER_DEFAULT_CTLCHAR;
ser->io_RBufLen   = 4096;       /* read buffer size */
ser->io_Baud      = 9600;
ser->io_ReadLen   = 8;          /* data bits */
ser->io_WriteLen  = 8;
ser->io_StopBits  = 1;
ser->io_SerFlags  = SERF_XDISABLED; /* no XON/XOFF */
ser->IOSer.io_Command = SDCMD_SETPARAMS;
DoIO((struct IORequest *)ser);
```

---

## Commands

| Code | Constant | Description |
|---|---|---|
| 2 | `CMD_READ` | Read bytes |
| 3 | `CMD_WRITE` | Write bytes |
| 5 | `CMD_CLEAR` | Clear buffers |
| 8 | `CMD_FLUSH` | Abort pending requests |
| 9 | `SDCMD_QUERY` | Get status (bytes in buffer, errors) |
| 10 | `SDCMD_BREAK` | Send break signal |
| 11 | `SDCMD_SETPARAMS` | Set baud/bits/parity/stop |

---

## References

- NDK39: `devices/serial.h`
- ADCD 2.1: serial.device autodocs
