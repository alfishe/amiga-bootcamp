[← Home](../README.md) · [AmigaDOS](README.md)

# Locks and Examine — Lock, UnLock, Examine, ExNext, ExAll

## Overview

AmigaDOS uses **locks** to reference files and directories. A lock is a BPTR to a `FileLock` structure. Locks provide exclusive or shared access and are used for directory scanning, attribute reading, and path resolution.

---

## Lock Types

```c
/* dos/dos.h */
#define SHARED_LOCK     -2   /* read-only; multiple readers allowed */
#define ACCESS_READ     SHARED_LOCK
#define EXCLUSIVE_LOCK  -1   /* read/write; only one holder */
#define ACCESS_WRITE    EXCLUSIVE_LOCK
```

---

## Core Functions

| LVO | Function | Registers | Returns |
|---|---|---|---|
| −84 | `Lock(name, mode)` | D1=name, D2=mode | D0=lock BPTR (0=fail) |
| −90 | `UnLock(lock)` | D1=lock | — |
| −96 | `DupLock(lock)` | D1=lock | D0=new lock |
| −102 | `Examine(lock, fib)` | D1=lock, D2=fib | D0=BOOL |
| −108 | `ExNext(lock, fib)` | D1=lock, D2=fib | D0=BOOL |
| −78 | `CurrentDir(lock)` | D1=lock | D0=old lock |
| −654 | `ExAll(lock, buf, size, type, ctrl)` | D1–D5 | D0=BOOL |

---

## struct FileInfoBlock

```c
/* dos/dos.h — NDK39 */
struct FileInfoBlock {
    LONG   fib_DiskKey;        /* handler-private key */
    LONG   fib_DirEntryType;   /* >0 = directory, <0 = file */
    char   fib_FileName[108];  /* null-terminated name */
    LONG   fib_Protection;     /* rwed bits */
    LONG   fib_EntryType;      /* same as DirEntryType */
    LONG   fib_Size;           /* file size in bytes */
    LONG   fib_NumBlocks;      /* blocks used */
    struct DateStamp fib_Date; /* modification date */
    char   fib_Comment[80];    /* file comment string */
    UWORD  fib_OwnerUID;
    UWORD  fib_OwnerGID;
    char   fib_Reserved[32];
};
```

> [!IMPORTANT]
> `FileInfoBlock` must be longword-aligned. Use `AllocDosObject(DOS_FIB, NULL)` on OS 2.0+ or `AllocMem(sizeof(struct FileInfoBlock), MEMF_PUBLIC)`.

---

## Protection Bits

```c
/* dos/dos.h */
#define FIBF_SCRIPT   (1<<6)   /* s — script (executable script) */
#define FIBF_PURE     (1<<5)   /* p — pure (re-entrant) */
#define FIBF_ARCHIVE  (1<<4)   /* a — archived */
#define FIBF_READ     (1<<3)   /* r — readable (0=allowed, 1=denied!) */
#define FIBF_WRITE    (1<<2)   /* w — writable */
#define FIBF_EXECUTE  (1<<1)   /* e — executable */
#define FIBF_DELETE   (1<<0)   /* d — deletable */
```

> [!WARNING]
> Amiga protection bits are **inverted** from Unix: bit SET means access is **denied**.

---

## Directory Scanning

```c
BPTR lock = Lock("SYS:", SHARED_LOCK);
struct FileInfoBlock *fib = AllocDosObject(DOS_FIB, NULL);

if (Examine(lock, fib)) {            /* read dir's own info */
    while (ExNext(lock, fib)) {       /* iterate entries */
        Printf("%-30s %8ld %s\n",
               fib->fib_FileName,
               fib->fib_Size,
               fib->fib_DirEntryType > 0 ? "(dir)" : "");
    }
    /* ExNext returns FALSE when done; IoErr() == ERROR_NO_MORE_ENTRIES */
}

FreeDosObject(DOS_FIB, fib);
UnLock(lock);
```

---

## ExAll (OS 2.0+) — Bulk Scan

```c
struct ExAllControl *eac = AllocDosObject(DOS_EXALLCONTROL, NULL);
UBYTE buf[4096];
BOOL more;

eac->eac_LastKey = 0;
do {
    more = ExAll(lock, buf, sizeof(buf), ED_NAME, eac);
    struct ExAllData *ead = (struct ExAllData *)buf;
    while (ead) {
        Printf("%s\n", ead->ed_Name);
        ead = ead->ed_Next;
    }
} while (more);
FreeDosObject(DOS_EXALLCONTROL, eac);
```

---

## References

- NDK39: `dos/dos.h`, `dos/dosextens.h`, `dos/exall.h`
- ADCD 2.1: `Lock`, `UnLock`, `Examine`, `ExNext`, `ExAll`
