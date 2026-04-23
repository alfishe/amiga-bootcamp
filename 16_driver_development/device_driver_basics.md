[← Home](../README.md) · [Driver Development](README.md)

# Exec Device Driver Framework

## Overview

An Amiga **device** is a shared library with additional I/O semantics. Devices handle hardware or protocol communication via `IORequest` messages. Understanding this framework is essential before writing any specific driver (network, graphics, audio).

---

## Device vs Library

| Feature | Library | Device |
|---|---|---|
| Base structure | `struct Library` | `struct Device` (extends Library) |
| Entry points | `Open`, `Close`, `Expunge`, LVO functions | `Open`, `Close`, `Expunge` + `BeginIO`, `AbortIO` |
| Communication | Direct function calls | `IORequest` messages via `DoIO`/`SendIO` |
| Concurrency | Caller's task context | Can have own task/interrupt context |

---

## Minimal Device Structure

```c
/* mydevice.h */
struct MyDevBase {
    struct Device   md_Device;       /* MUST be first */
    struct Library *md_SysBase;
    struct Library *md_DOSBase;
    /* ... device-specific state ... */
};
```

---

## Device Function Table

Every device must provide exactly these entry points in its function vector:

```c
/* Function table (same as library, plus BeginIO/AbortIO): */
static const APTR funcTable[] = {
    (APTR) DevOpen,       /* -6  (standard library Open) */
    (APTR) DevClose,      /* -12 (standard library Close) */
    (APTR) DevExpunge,    /* -18 (standard library Expunge) */
    (APTR) DevReserved,   /* -24 (reserved, must return 0) */
    (APTR) DevBeginIO,    /* -30 (start I/O operation) */
    (APTR) DevAbortIO,    /* -36 (abort pending I/O) */
    (APTR) -1             /* end marker */
};
```

---

## DevOpen

```c
LONG DevOpen(struct IORequest *ioreq, ULONG unit, ULONG flags,
             struct MyDevBase *base)
{
    /* Initialise per-unit state if needed */
    struct MyUnit *u = &base->md_Units[unit];
    
    ioreq->io_Device = (struct Device *)base;
    ioreq->io_Unit   = (struct Unit *)u;
    ioreq->io_Error  = 0;
    
    base->md_Device.dd_Library.lib_OpenCnt++;
    u->mu_OpenCnt++;
    
    return 0;  /* success */
}
```

---

## DevBeginIO — The Core

```c
void DevBeginIO(struct IORequest *ioreq, struct MyDevBase *base)
{
    struct IOStdReq *ios = (struct IOStdReq *)ioreq;
    
    ios->io_Error = 0;
    
    switch (ios->io_Command) {
        case CMD_READ:
            /* Handle synchronously or queue for async */
            if (!(ios->io_Flags & IOF_QUICK)) {
                /* Queue request — reply later via ReplyMsg */
                AddTail(&unit->mu_ReadQueue, &ios->io_Message.mn_Node);
                ios->io_Flags &= ~IOF_QUICK;
                return;  /* do NOT ReplyMsg yet */
            }
            /* ... do sync read ... */
            break;
            
        case CMD_WRITE:
            /* ... */
            break;
            
        default:
            ios->io_Error = IOERR_NOCMD;
            break;
    }
    
    /* Complete the request: */
    if (!(ios->io_Flags & IOF_QUICK)) {
        ReplyMsg(&ios->io_Message);
    }
}
```

---

## DevAbortIO

```c
LONG DevAbortIO(struct IORequest *ioreq, struct MyDevBase *base)
{
    /* Remove from pending queue if found */
    Forbid();
    Remove(&ioreq->io_Message.mn_Node);
    Permit();
    
    ioreq->io_Error = IOERR_ABORTED;
    ReplyMsg(&ioreq->io_Message);
    return 0;
}
```

---

## IOF_QUICK — Synchronous Fast Path

The `IOF_QUICK` flag is critical:
- Caller sets `IOF_QUICK` in `ioreq->io_Flags`
- If device completes immediately, it leaves `IOF_QUICK` set → caller knows it's done (no `WaitIO` needed)
- If device queues the request, it **clears** `IOF_QUICK` → caller must `WaitIO`

```c
/* Caller pattern (DoIO does this internally): */
ioreq->io_Flags |= IOF_QUICK;
BeginIO(ioreq);
if (!(ioreq->io_Flags & IOF_QUICK))
    WaitIO(ioreq);
```

---

## RomTag for Device

```c
static struct Resident romtag = {
    RTC_MATCHWORD,
    &romtag,
    &endskip,
    RTF_AUTOINIT,
    1,                  /* version */
    NT_DEVICE,          /* ← not NT_LIBRARY */
    0,                  /* priority */
    "mydevice.device",
    "mydevice 1.0",
    &initTable
};
```

---

## References

- NDK39: `exec/devices.h`, `exec/io.h`
- ADCD 2.1: `DoIO`, `SendIO`, `WaitIO`, `AbortIO`
- RKRM: *Amiga ROM Kernel Reference Manual: Devices* — device driver chapter
