[← Home](../README.md) · [Devices](README.md)

# trackdisk.device — Floppy Disk I/O

## Overview

`trackdisk.device` provides raw sector I/O for Amiga floppy drives. Each drive is a unit (0–3). The device operates on 512-byte sectors, 11 sectors per track (880 KB DD disks) or 22 per track (1760 KB HD).

---

## Opening

```c
struct IOExtTD *tdreq = (struct IOExtTD *)
    CreateIORequest(port, sizeof(struct IOExtTD));
OpenDevice("trackdisk.device", 0, (struct IORequest *)tdreq, 0);
```

---

## Commands

| Code | Constant | Description |
|---|---|---|
| 2 | `CMD_READ` | Read sectors |
| 3 | `CMD_WRITE` | Write sectors |
| 4 | `CMD_UPDATE` | Flush write buffer to disk |
| 9 | `TD_MOTOR` | Turn motor on/off |
| 10 | `TD_FORMAT` | Low-level format track |
| 11 | `TD_SEEK` | Move head to track |
| 12 | `TD_REMOVE` | Notify on disk change |
| 13 | `TD_CHANGENUM` | Get disk change count |
| 14 | `TD_CHANGESTATE` | Check if disk present |
| 15 | `TD_PROTSTATUS` | Check write-protect |
| 16 | `TD_RAWREAD` | Read raw MFM data |
| 17 | `TD_RAWWRITE` | Write raw MFM data |
| 18 | `TD_GETDRIVETYPE` | Get drive type |
| 19 | `TD_GETNUMTRACKS` | Get total tracks |
| 20 | `TD_ADDCHANGEINT` | Add disk change interrupt |
| 21 | `TD_REMCHANGEINT` | Remove disk change interrupt |

---

## Reading a Sector

```c
UBYTE buf[512];
tdreq->iotd_Req.io_Command = CMD_READ;
tdreq->iotd_Req.io_Data    = buf;
tdreq->iotd_Req.io_Length  = 512;
tdreq->iotd_Req.io_Offset  = 0;   /* byte offset = sector * 512 */
DoIO((struct IORequest *)tdreq);
```

---

## Disk Geometry

| Parameter | DD (880 KB) | HD (1760 KB) |
|---|---|---|
| Heads | 2 | 2 |
| Cylinders | 80 | 80 |
| Sectors/track | 11 | 22 |
| Bytes/sector | 512 | 512 |
| Total sectors | 1760 | 3520 |

Byte offset = `(cylinder * 2 + head) * sectors_per_track * 512 + sector * 512`

---

## References

- NDK39: `devices/trackdisk.h`
- ADCD 2.1: trackdisk.device autodocs
