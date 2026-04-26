[← Home](../README.md) · [Exec Kernel](README.md)

# Library Vectors — JMP Table, LVOs, MakeFunctions, SetFunction

## Overview

Every AmigaOS library exposes its functions via a **JMP table** at negative offsets from the library base. This document covers the structure of the table, how LVOs (Library Vector Offsets) are assigned, and how to create or patch one programmatically. Understanding the JMP table is essential for both library development and reverse engineering.

---

## JMP Table Structure

```
Address              Content            Description
─────────────────────────────────────────────────────────
lib_base - N×6:     4EF9 XXXXXXXX      JMP <absolute>  ← function N
...
lib_base - 30:      4EF9 XXXXXXXX      JMP FirstUserFunc
lib_base - 24:      4EF9 XXXXXXXX      JMP Reserved
lib_base - 18:      4EF9 XXXXXXXX      JMP Expunge
lib_base - 12:      4EF9 XXXXXXXX      JMP Close
lib_base -  6:      4EF9 XXXXXXXX      JMP Open
─────────────────────────────────────────────────────────
lib_base +  0:      struct Library      ← OpenLibrary returns this
lib_base + PosSize: (end)
```

Each slot is exactly **6 bytes**: opcode `$4EF9` (JMP abs.l) + 4-byte target address.

### Calling Convention

```c
/* C — compiler generates: */
result = LibraryFunction(args);
/* Internally: */
/*   MOVEA.L LibBase,A6        ; load library base into A6 */
/*   JSR     LVO(A6)           ; jump to base+LVO → hits JMP instruction */
/*   ; JMP redirects to actual function */
```

```asm
; Assembly — explicit:
    MOVEA.L  _DOSBase,A6
    JSR      -30(A6)           ; LVO -30 = first user function
```

---

## LVO Formula

```
LVO = −6 × slot_index

where slot_index counts from 1 (Open) upward:
  Open         = slot 1 → LVO = −6
  Close        = slot 2 → LVO = −12
  Expunge      = slot 3 → LVO = −18
  Reserved     = slot 4 → LVO = −24
  First user   = slot 5 → LVO = −30
  Second user  = slot 6 → LVO = −36
  ...
```

### From .fd Files

```
##base _DOSBase
##bias 30
##public
Open(name,accessMode)(D1/D2)
Close(file)(D1)
Read(file,buffer,length)(D1/D2/D3)
```

`##bias 30` means the first user function has LVO `−30`. Each subsequent function adds `−6`.

| Function | .fd Position | LVO |
|---|---|---|
| `Open` | 1st after bias | −30 |
| `Close` | 2nd | −36 |
| `Read` | 3rd | −42 |
| `Write` | 4th | −48 |

---

## Standard Vectors (Slots 1–4)

Every library must implement these four vectors:

| Slot | LVO | Function | Purpose |
|---|---|---|---|
| 1 | −6 | `Open` | Called by `OpenLibrary()` — increment open count, init per-opener state |
| 2 | −12 | `Close` | Called by `CloseLibrary()` — decrement open count, cleanup |
| 3 | −18 | `Expunge` | Called to unload — free resources if `OpenCnt == 0` |
| 4 | −24 | `Reserved` | Must exist — returns NULL. Reserved for future use |

---

## MakeFunctions — Building a JMP Table

```c
ULONG MakeFunctions(APTR target, APTR funcArray, APTR funcDispBase);
/* LVO -420 */
```

Writes JMP instructions into the negative offset area of `target`:

```c
/* funcArray: NULL-terminated table of function pointers */
APTR myFuncs[] = {
    LibOpen,
    LibClose,
    LibExpunge,
    LibReserved,
    MyFunc1,
    MyFunc2,
    (APTR)-1        /* terminator */
};

MakeFunctions(libBase, myFuncs, NULL);
/* Writes: JMP LibOpen at base-6, JMP LibClose at base-12, etc. */
```

### Assembly Example

```asm
_LibFuncTable:
    dc.l  _LibOpen       ; slot 1 → LVO -6
    dc.l  _LibClose      ; slot 2 → LVO -12
    dc.l  _LibExpunge    ; slot 3 → LVO -18
    dc.l  _LibNull       ; slot 4 → LVO -24 (Reserved)
    dc.l  _MyFunc1       ; slot 5 → LVO -30
    dc.l  _MyFunc2       ; slot 6 → LVO -36
    dc.l  -1             ; terminator

LibInit:
    LEA   _LibFuncTable(PC),A0
    MOVEA.L  A6,A1          ; library base
    MOVEQ    #0,D0          ; funcDispBase = 0 (absolute addresses)
    MOVEA.L  4.W,A6
    JSR      -420(A6)       ; MakeFunctions
```

---

## SetFunction — Patching a Single Slot

```c
APTR SetFunction(struct Library *library, LONG funcOffset, APTR newFunction);
/* LVO -420 */
/* Returns: old function pointer */
```

This is the primary mechanism for **system patching** — replacing a library function with your own:

```c
/* Hook dos.library Write() */
typedef LONG (*WriteFunc)(BPTR file, APTR buf, LONG len);

WriteFunc oldWrite;
oldWrite = (WriteFunc)SetFunction(
    (struct Library *)DOSBase,
    -48,              /* LVO for Write */
    (APTR)MyWriteHook
);

/* Your hook: */
LONG __saveds MyWriteHook(
    BPTR file __asm("d1"),
    APTR buf  __asm("d2"),
    LONG len  __asm("d3"))
{
    /* Log the write, then call original */
    LogWrite(file, len);
    return oldWrite(file, buf, len);
}

/* Restore on cleanup: */
SetFunction((struct Library *)DOSBase, -48, (APTR)oldWrite);
```

### SetFunction Gotchas

| Issue | Details |
|---|---|
| **Not atomic** | Between SetFunction calls, another task may see inconsistent state |
| **Checksum invalidation** | SetFunction sets `LIBF_CHANGED` — must call `SumLibrary()` |
| **Multiple patchers** | If two programs patch the same LVO, unpatching in wrong order breaks the chain |
| **ROM functions** | SetFunction works even on ROM libraries — the JMP table is in RAM |
| **Caching on 040/060** | Must flush instruction cache after patching |

---

## Checksum Maintenance

```c
/* After modifying the JMP table: */
SumLibrary((struct Library *)myLib);   /* LVO -426 */
```

If `LIBF_SUMUSED` is set, exec verifies the checksum periodically. Patching without updating the checksum triggers a "Library checksum failure" alert.

---

## MakeLibrary — One-Shot Library Creation

```c
struct Library *MakeLibrary(
    APTR funcArray,      /* function pointer table */
    APTR structInit,     /* InitStruct data table */
    APTR initFunc,       /* init function (receives lib base in D0) */
    ULONG dataSize,      /* size of library base struct */
    BPTR segList          /* segment list (for expunge) */
);   /* LVO -84 */
```

This combines allocation, JMP table construction, data initialization, and init-function calling into one operation. Used by `RTF_AUTOINIT` modules and direct library creation.

---

## Reverse Engineering: Viewing Vectors in IDA Pro

1. Navigate to `lib_base − 6` (first standard vector = `Open`)
2. Each 6-byte group: opcode `$4EF9` + 4-byte absolute address
3. Press `C` to disassemble if not auto-detected
4. Follow the 4-byte address to the actual function body
5. Name each function using the `.fd` file as reference
6. The `.fd` bias tells you which LVO maps to which function name

### Reconstructing the Full Vector Table

```python
# Python script for reading JMP table from binary
import struct

def dump_vectors(rom_data, lib_base, num_vectors):
    for i in range(1, num_vectors + 1):
        offset = lib_base - (i * 6)
        opcode, target = struct.unpack('>HI', rom_data[offset:offset+6])
        if opcode == 0x4EF9:  # JMP abs.l
            print(f"  LVO -{i*6:4d}: JMP ${target:08X}")
```

---

## References

- NDK39: `exec/execbase.h`, `exec/libraries.h`
- ADCD 2.1: `MakeFunctions`, `MakeLibrary`, `SetFunction`, `SumLibrary`
- See also: [Library System](library_system.md) — open/close/expunge lifecycle
- See also: [LVO Table](../04_linking_and_libraries/lvo_table.md) — complete LVO reference tables
- See also: [SetFunction Patching](../05_reversing/dynamic/setfunction_patching.md) — trampoline patterns
- *Amiga ROM Kernel Reference Manual: Exec* — library vectors chapter
