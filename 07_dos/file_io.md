[← Home](../README.md) · [AmigaDOS](README.md)

# File I/O — Open, Close, Read, Write, Seek, Async I/O

## Overview

AmigaDOS file I/O is synchronous from the caller's perspective — each call blocks until the filesystem handler completes the operation. All functions use `BPTR` file handles and communicate errors via `IoErr()`. Internally, every I/O call is translated into a DosPacket sent to the filesystem handler process (see [packet_system.md](packet_system.md)).

---

## Core Functions

| LVO | Function | Registers | Returns |
|---|---|---|---|
| −30 | `Open(name, mode)` | D1=name, D2=mode | D0=BPTR handle (0=fail) |
| −36 | `Close(fh)` | D1=handle | D0=BOOL |
| −42 | `Read(fh, buf, len)` | D1=handle, D2=buf, D3=len | D0=actual bytes (−1=error) |
| −48 | `Write(fh, buf, len)` | D1=handle, D2=buf, D3=len | D0=actual bytes (−1=error) |
| −66 | `Seek(fh, pos, mode)` | D1=handle, D2=pos, D3=mode | D0=old position (−1=error) |
| −330 | `FRead(fh, buf, bsize, n)` | D1–D4 | D0=blocks read (buffered) |
| −336 | `FWrite(fh, buf, bsize, n)` | D1–D4 | D0=blocks written (buffered) |
| −348 | `FGets(fh, buf, len)` | D1–D3 | D0=buf or NULL |
| −354 | `FPuts(fh, str)` | D1–D2 | D0=0 or EOF |
| −360 | `Flush(fh)` | D1=handle | D0=BOOL |
| −366 | `SetVBuf(fh, buf, type, size)` | D1–D4 | D0=0 or −1 |

---

## Access Modes

```c
/* dos/dos.h — NDK39 */
#define MODE_READWRITE  1004   /* open existing, read+write */
#define MODE_OLDFILE    1005   /* open existing, read only */
#define MODE_NEWFILE    1006   /* create new (truncate if exists) */
```

| Mode | If file exists | If file doesn't exist |
|---|---|---|
| `MODE_OLDFILE` | Opens for reading | Fails — `IoErr() = ERROR_OBJECT_NOT_FOUND` |
| `MODE_NEWFILE` | Truncates to 0, opens for writing | Creates new file |
| `MODE_READWRITE` | Opens at current size, read+write | Creates new file |

---

## Seek Modes

```c
#define OFFSET_BEGINNING  -1   /* from start of file */
#define OFFSET_CURRENT     0   /* from current position */
#define OFFSET_END         1   /* from end of file */
```

> **Note**: `Seek()` returns the **old position** (before seeking), not the new one. To get file size: `Seek(fh, 0, OFFSET_END)` then `size = Seek(fh, 0, OFFSET_BEGINNING)`.

---

## File Handle Structure

The returned handle is a BPTR to a `struct FileHandle`:

```c
/* dos/dosextens.h */
struct FileHandle {
    struct Message *fh_Link;        /* +$00: exec message for reply */
    struct MsgPort *fh_Interactive;  /* +$04: non-NULL if console device */
    struct MsgPort *fh_Type;        /* +$08: handler process MsgPort */
    BPTR    fh_Buf;                 /* +$0C: I/O buffer (BPTR) */
    LONG    fh_Pos;                 /* +$10: current position in buffer */
    LONG    fh_End;                 /* +$14: end of valid data in buffer */
    LONG    fh_Funcs;               /* +$18: unused (was BCPL function) */
    LONG    fh_Func2;               /* +$1C: unused */
    LONG    fh_Func3;               /* +$20: unused */
    LONG    fh_Args;                /* +$24: FH_Arg1 — passed to handler */
    BPTR    fh_Arg2;                /* +$28: handler-specific */
};
/* sizeof(struct FileHandle) = 44 bytes ($2C) */
```

```c
/* To access as a C pointer: */
struct FileHandle *fhp = BADDR(handle);  /* BADDR = (ptr << 2) */

/* Check if interactive (console): */
if (IsInteractive(fh))
    Printf("Connected to a console\n");
```

### I/O Buffering

AmigaDOS uses **per-handle buffering** (OS 2.0+). Default buffer is 512 bytes. Control with `SetVBuf()`:

```c
/* Make a file fully buffered with 8 KB buffer: */
SetVBuf(fh, NULL, BUF_FULL, 8192);

/* Line-buffered (flush on newline — useful for consoles): */
SetVBuf(fh, NULL, BUF_LINE, 1024);

/* Unbuffered (every write goes to handler immediately): */
SetVBuf(fh, NULL, BUF_NONE, 0);

/* Manually flush: */
Flush(fh);
```

| Buffer Type | Constant | Behaviour |
|---|---|---|
| `BUF_FULL` | 1 | Flush when buffer fills |
| `BUF_LINE` | 0 | Flush on newline or buffer full |
| `BUF_NONE` | −1 | No buffering — direct I/O |

---

## Standard I/O Handles

```c
/* Get the current process's stdin/stdout/stderr: */
BPTR in  = Input();    /* stdin — from CLI or WB */
BPTR out = Output();   /* stdout */
BPTR err = ErrorOutput(); /* stderr (OS 3.0+ only) */

/* Write to stdout: */
FPuts(Output(), "Hello from AmigaDOS\n");

/* Printf — formatted output to stdout: */
Printf("Count: %ld, Name: %s\n", count, name);
/* Note: Printf uses %ld (not %d) — AmigaDOS always uses LONG */
```

> [!IMPORTANT]
> AmigaDOS `Printf` uses `%ld` for integers, not `%d`. The `%d` format is undefined. This is a common bug source when porting from Unix/ANSI C.

---

## File Information — ExamineFH, ExAll

```c
/* Get file metadata from a handle: */
struct FileInfoBlock *fib = AllocDosObject(DOS_FIB, NULL);
if (ExamineFH(fh, fib))
{
    Printf("Name: %s\n", fib->fib_FileName);
    Printf("Size: %ld\n", fib->fib_Size);
    Printf("Type: %ld\n", fib->fib_DirEntryType);
    /* > 0 = directory, < 0 = file */
}
FreeDosObject(DOS_FIB, fib);
```

### FileInfoBlock Structure

```c
struct FileInfoBlock {
    LONG   fib_DiskKey;           /* block number on disk */
    LONG   fib_DirEntryType;     /* >0=dir, <0=file */
    char   fib_FileName[108];    /* null-terminated name */
    LONG   fib_Protection;       /* RWED protection bits */
    LONG   fib_EntryType;        /* same as DirEntryType */
    LONG   fib_Size;             /* file size in bytes */
    LONG   fib_NumBlocks;        /* blocks consumed */
    struct DateStamp fib_Date;   /* modification date */
    char   fib_Comment[80];      /* file comment string */
    UWORD  fib_OwnerUID;         /* owner (multiuser) */
    UWORD  fib_OwnerGID;         /* group */
};
```

---

## Practical Patterns

### Copy a File

```c
BOOL CopyFile(CONST_STRPTR src, CONST_STRPTR dst)
{
    BPTR in = Open(src, MODE_OLDFILE);
    if (!in) return FALSE;

    BPTR out = Open(dst, MODE_NEWFILE);
    if (!out) { Close(in); return FALSE; }

    UBYTE buf[4096];
    LONG n;
    while ((n = Read(in, buf, sizeof(buf))) > 0)
    {
        if (Write(out, buf, n) != n)
        {
            Close(in); Close(out);
            return FALSE;  /* write error */
        }
    }

    Close(out);
    Close(in);
    return (n == 0);  /* 0=EOF=success, -1=error */
}
```

### Determine File Size

```c
LONG GetFileSize(BPTR fh)
{
    LONG oldpos = Seek(fh, 0, OFFSET_END);    /* seek to end */
    LONG size   = Seek(fh, oldpos, OFFSET_BEGINNING); /* seek back */
    return size;
}
/* Or with ExamineFH (no seeking needed): */
struct FileInfoBlock fib;
ExamineFH(fh, &fib);
LONG size = fib.fib_Size;
```

### Read Entire File into Memory

```c
APTR LoadFileToRAM(CONST_STRPTR path, ULONG *sizeOut)
{
    BPTR fh = Open(path, MODE_OLDFILE);
    if (!fh) return NULL;

    /* Get size */
    Seek(fh, 0, OFFSET_END);
    LONG size = Seek(fh, 0, OFFSET_BEGINNING);

    APTR buf = AllocVec(size, MEMF_ANY);
    if (buf)
    {
        if (Read(fh, buf, size) != size)
        {
            FreeVec(buf);
            buf = NULL;
        }
    }
    Close(fh);
    *sizeOut = size;
    return buf;
}
```

---

## Error Checking

```c
LONG err = IoErr();   /* returns last DOS error code */

/* Human-readable error message: */
PrintFault(err, "Operation failed");
/* Output: "Operation failed: object not found" */

/* Or get error string into buffer: */
Fault(err, "Error", buf, sizeof(buf));
```

### Common Error Codes

| Code | Constant | Meaning |
|---|---|---|
| 103 | `ERROR_NO_FREE_STORE` | Out of memory |
| 202 | `ERROR_OBJECT_IN_USE` | File is locked by another process |
| 203 | `ERROR_OBJECT_EXISTS` | File already exists |
| 204 | `ERROR_DIR_NOT_FOUND` | Path component not found |
| 205 | `ERROR_OBJECT_NOT_FOUND` | File not found |
| 209 | `ERROR_ACTION_NOT_KNOWN` | Handler doesn't support this action |
| 210 | `ERROR_INVALID_COMPONENT_NAME` | Bad filename character |
| 212 | `ERROR_OBJECT_WRONG_TYPE` | Expected file, got directory (or vice versa) |
| 214 | `ERROR_DISK_FULL` | No space on volume |
| 216 | `ERROR_DELETE_PROTECTED` | File has delete-protection bit |
| 218 | `ERROR_WRITE_PROTECTED` | Disk is write-protected |
| 219 | `ERROR_SEEK_ERROR` | Invalid seek position |
| 221 | `ERROR_DISK_FULL` | Volume full |
| 225 | `ERROR_NOT_A_DOS_DISK` | Unrecognised filesystem |
| 232 | `ERROR_NO_MORE_ENTRIES` | ExNext — end of directory |

---

## References

- NDK39: `dos/dos.h`, `dos/dosextens.h`, `dos/stdio.h`
- ADCD 2.1: `Open`, `Close`, `Read`, `Write`, `Seek`, `SetVBuf`, `FRead`
- [error_handling.md](error_handling.md) — full error code list
- [packet_system.md](packet_system.md) — how I/O translates to handler packets
