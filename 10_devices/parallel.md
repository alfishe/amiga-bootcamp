[← Home](../README.md) · [Devices](README.md)

# parallel.device — Centronics Parallel Port

## Overview

`parallel.device` provides I/O for the Amiga's Centronics-compatible parallel port, used primarily for printers.

---

## Opening

```c
struct IOExtPar *par = (struct IOExtPar *)
    CreateIORequest(port, sizeof(struct IOExtPar));
OpenDevice("parallel.device", 0, (struct IORequest *)par, 0);
```

---

## Commands

| Code | Constant | Description |
|---|---|---|
| 2 | `CMD_READ` | Read bytes (if bidirectional) |
| 3 | `CMD_WRITE` | Write bytes |
| 5 | `CMD_CLEAR` | Clear buffers |
| 8 | `CMD_FLUSH` | Abort pending |
| 9 | `PDCMD_QUERY` | Get status |
| 10 | `PDCMD_SETPARAMS` | Set parameters |

---

## References

- NDK39: `devices/parallel.h`
