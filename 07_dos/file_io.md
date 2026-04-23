[← Home](../README.md) · [AmigaDOS](README.md)

# File I/O — Open, Close, Read, Write, Seek

## Overview

AmigaDOS file I/O is synchronous from the caller's perspective. All functions use `BPTR` file handles and communicate errors via `IoErr()`.

---

## Core Functions

| LVO | Function | Registers | Returns |
|---|---|---|---|
| −30 | `Open(name, mode)` | D1=name, D2=mode | D0=BPTR handle (0=fail) |
| −36 | `Close(fh)` | D1=handle | D0=BOOL |
| −42 | `Read(fh, buf, len)` | D1=handle, D2=buf, D3=len | D0=actual bytes (−1=error) |
| −48 | `Write(fh, buf, len)` | D1=handle, D2=buf, D3=len | D0=actual bytes (−1=error) |
| −66 | `Seek(fh, pos, mode)` | D1=handle, D2=pos, D3=mode | D0=old position (−1=error) |

---

## Access Modes

```c
/* dos/dos.h — NDK39 */
#define MODE_READWRITE  1004   /* open existing, read+write */
#define MODE_OLDFILE    1005   /* open existing, read only */
#define MODE_NEWFILE    1006   /* create new (truncate if exists) */
```

---

## Seek Modes

```c
#define OFFSET_BEGINNING  -1   /* from start of file */
#define OFFSET_CURRENT     0   /* from current position */
#define OFFSET_END         1   /* from end of file */
```

---

## File Handle (BPTR)

The returned handle is a BPTR to a `struct FileHandle`:

```c
struct FileHandle {
    struct Message *fh_Link;
    struct MsgPort *fh_Interactive; /* non-NULL if console */
    struct MsgPort *fh_Type;       /* handler process port */
    BPTR   fh_Buf;                 /* I/O buffer (BPTR) */
    LONG   fh_Pos;                 /* current position in buffer */
    LONG   fh_End;                 /* end of valid data in buffer */
    LONG   fh_Funcs;               /* unused */
    LONG   fh_Func2;               /* unused */
    LONG   fh_Func3;               /* unused */
    LONG   fh_Args;                /* packet args */
    BPTR   fh_Arg2;
};
```

To access as a C pointer: `struct FileHandle *fh = BADDR(handle);`

---

## Usage Example

```c
BPTR fh = Open("RAM:test.txt", MODE_NEWFILE);
if (fh) {
    Write(fh, "Hello Amiga\n", 12);
    Close(fh);
}

fh = Open("RAM:test.txt", MODE_OLDFILE);
if (fh) {
    UBYTE buf[64];
    LONG n = Read(fh, buf, sizeof(buf));
    if (n > 0) Write(Output(), buf, n);  /* echo to stdout */
    Close(fh);
} else {
    PrintFault(IoErr(), "Open failed");
}
```

---

## Error Checking

```c
LONG err = IoErr();   /* LVO −66 — returns last DOS error code */
/* Common codes: */
#define ERROR_OBJECT_NOT_FOUND    205
#define ERROR_OBJECT_EXISTS       203
#define ERROR_DISK_FULL           221
#define ERROR_SEEK_ERROR          219
```

---

## References

- NDK39: `dos/dos.h`, `dos/dosextens.h`
- `07_dos/error_handling.md` — full error code list
- ADCD 2.1: `Open`, `Close`, `Read`, `Write`, `Seek`
