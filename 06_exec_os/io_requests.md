[← Home](../README.md) · [Exec Kernel](README.md)

# IO Requests — IORequest, DoIO, SendIO, CheckIO, AbortIO

## Overview

AmigaOS device I/O uses a **message-based** asynchronous protocol. Every device operation is described by an `IORequest` structure sent to a device's command port. The device processes it (synchronously or in the background) and replies when done.

---

## Structures

```c
/* exec/io.h — NDK39 */

struct IORequest {
    struct Message io_Message;  /* embedded Message (has MsgPort reply port) */
    struct Device *io_Device;   /* filled by OpenDevice */
    struct Unit   *io_Unit;     /* filled by OpenDevice */
    UWORD          io_Command;  /* CMD_READ, CMD_WRITE, TD_FORMAT, ... */
    UBYTE          io_Flags;    /* IOF_QUICK = attempt synchronous fast path */
    BYTE           io_Error;    /* result: 0 = success, negative = error code */
};

struct IOStdReq {               /* extended version with data fields */
    struct IORequest io_Request;
    ULONG  io_Actual;           /* actual bytes transferred */
    ULONG  io_Length;           /* requested byte count */
    APTR   io_Data;             /* data buffer pointer */
    ULONG  io_Offset;           /* byte offset (for random-access devices) */
};
```

---

## Standard Command Codes

```c
/* exec/io.h */
#define CMD_INVALID   0   /* not a valid command */
#define CMD_RESET     1   /* reset the device/unit to initial state */
#define CMD_READ      2   /* read io_Length bytes into io_Data from io_Offset */
#define CMD_WRITE     3   /* write io_Length bytes from io_Data at io_Offset */
#define CMD_UPDATE    4   /* flush write cache to media */
#define CMD_CLEAR     5   /* discard device read buffers */
#define CMD_STOP      6   /* suspend device operation */
#define CMD_START     7   /* resume device operation */
#define CMD_FLUSH     8   /* abort all pending requests */
#define CMD_NONSTD    9   /* first device-specific command number */
```

Device-specific commands start at `CMD_NONSTD` (9). Example: trackdisk uses `TD_FORMAT` (10), `TD_MOTOR` (11), `TD_SEEK` (12).

---

## Error Codes (`io_Error`)

```c
/* exec/errors.h — NDK39 */
#define IOERR_OPENFAIL   -1   /* device/unit could not be opened */
#define IOERR_ABORTED    -2   /* request was aborted via AbortIO */
#define IOERR_NOCMD      -3   /* unknown command */
#define IOERR_BADLENGTH  -4   /* io_Length invalid for this command */
#define IOERR_BADADDRESS -5   /* io_Data not aligned or accessible */
#define IOERR_UNITBUSY   -6   /* unit in use, cannot complete */
#define IOERR_SELFTEST   -7   /* hardware self-test failed */
```

---

## Opening a Device

```c
struct IOStdReq *ior = CreateStdIO(reply_port);   /* alloc + fill reply port */
if (OpenDevice("trackdisk.device", unit, (struct IORequest *)ior, 0) != 0) {
    /* open failed — ior->io_Error set */
}
```

Or manually:
```c
struct IOStdReq *ior = AllocMem(sizeof(struct IOStdReq), MEMF_PUBLIC|MEMF_CLEAR);
ior->io_Message.mn_ReplyPort = my_reply_port;
ior->io_Message.mn_Length    = sizeof(struct IOStdReq);
OpenDevice("audio.device", 0, (struct IORequest *)ior, 0);
```

---

## Synchronous I/O: `DoIO`

Blocks the calling task until the device completes the request:

```c
ior->io_Command = CMD_READ;
ior->io_Data    = buffer;
ior->io_Length  = 512;
ior->io_Offset  = 0;
LONG err = DoIO((struct IORequest *)ior);
/* io_Actual = bytes actually read; io_Error = error code */
```

---

## Asynchronous I/O: `SendIO` + `WaitIO`

```c
/* Queue the request — returns immediately: */
SendIO((struct IORequest *)ior);

/* Do other work while device operates... */

/* Block until this specific request completes: */
WaitIO((struct IORequest *)ior);
err = ior->io_Error;
```

### Poll without blocking: `CheckIO`

```c
/* Returns non-NULL if request is done (removed from device queue): */
if (CheckIO((struct IORequest *)ior)) {
    WaitIO((struct IORequest *)ior);  /* must still call WaitIO to dequeue reply */
}
```

---

## Aborting a Request: `AbortIO`

```c
AbortIO((struct IORequest *)ior);   /* ask device to cancel */
WaitIO((struct IORequest *)ior);    /* wait for confirmation */
/* io_Error will be IOERR_ABORTED (-2) */
```

---

## Closing a Device

```c
CloseDevice((struct IORequest *)ior);
DeleteStdIO(ior);   /* or FreeMem */
```

---

## References

- NDK39: `exec/io.h`, `exec/errors.h`
- ADCD 2.1: `OpenDevice`, `CloseDevice`, `DoIO`, `SendIO`, `WaitIO`, `CheckIO`, `AbortIO`
- `10_devices/` — per-device command codes and structures
- *Amiga ROM Kernel Reference Manual: Exec* — I/O requests chapter
