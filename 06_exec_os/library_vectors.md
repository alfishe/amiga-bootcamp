[← Home](../README.md) · [Exec Kernel](README.md)

# Library Vectors — JMP Table, LVOs, MakeFunctions, SetFunction

## Overview

Every AmigaOS library exposes its functions via a **JMP table** at negative offsets from the library base. This document covers the structure of the table, how LVOs are assigned, and how to create or patch one programmatically.

---

## JMP Table Structure

```
Address              Content         Description
lib_base - N×6:     4EF9 XXXXXXXX   JMP <absolute address>  ← function N
...
lib_base - 24:      4EF9 XXXXXXXX   JMP Reserved
lib_base - 18:      4EF9 XXXXXXXX   JMP Expunge
lib_base - 12:      4EF9 XXXXXXXX   JMP Close
lib_base -  6:      4EF9 XXXXXXXX   JMP Open
lib_base +  0:      struct Library  ← pointer returned by OpenLibrary
```

Each slot is exactly **6 bytes**: opcode `$4EF9` (JMP abs.l) + 4-byte target address.

---

## LVO Formula

```
LVO = −6 × slot_index

where slot_index counts from 1 (Open) upward:
  Open     = slot 1 → LVO = −6
  Close    = slot 2 → LVO = −12
  Expunge  = slot 3 → LVO = −18
  Reserved = slot 4 → LVO = −24
  First user fn = slot 5 → LVO = −30
  Second user fn = slot 6 → LVO = −36
  ...
```

The `.fd` file `##bias` value is the positive LVO: `bias 30` → LVO `−30`.

---

## MakeFunctions — Building a JMP Table

`exec.library MakeFunctions()` fills in the JMP table from a function pointer array:

```c
ULONG MakeFunctions(APTR targetLib, APTR funcArray, APTR funcDispBase);
```

Typical usage in library `InitLib`:

```asm
; funcArray: table of function pointers, terminated by -1
_LibFuncTable:
    dc.l  _LibOpen
    dc.l  _LibClose
    dc.l  _LibExpunge
    dc.l  _LibNull        ; Reserved — returns NULL
    dc.l  _MyFunc1
    dc.l  _MyFunc2
    dc.l  -1              ; terminator

LibInit:
    LEA   _LibFuncTable(PC), A0
    MOVEA.L  A6, A1       ; library base (passed in A6 by exec)
    MOVEQ    #0, D0       ; funcDispBase = 0 (absolute addresses)
    MOVEA.L  4.W, A6
    JSR      (-420,A6)    ; MakeFunctions(A1, A0, D0)
```

`MakeFunctions` writes `JMP <ptr>` for each entry, filling the table downward from `lib_base − 6`.

---

## SetFunction — Patching a Single Slot

```c
APTR SetFunction(struct Library *library, LONG funcOffset, APTR newFunction);
```

- `funcOffset` is the negative LVO (e.g., `−30` for the first user function)
- Returns the old function pointer

```c
/* Hook dos.library Write() */
old_write = SetFunction((struct Library *)DOSBase, -48, my_write_hook);
```

See [setfunction_patching.md](../05_reversing/dynamic/setfunction_patching.md) for trampoline patterns.

---

## Checksum Maintenance

After `MakeFunctions` or `SetFunction`, exec updates `lib_Sum` via `SumLibrary`:

```c
SumLibrary((struct Library *)myLib);
```

If `LIBF_SUMUSED` is set, exec verifies the checksum at `CloseLibrary` time. Patching the JMP table without calling `SumLibrary` will trigger a checksum failure (alert box or guru).

---

## Viewing Vectors in IDA Pro

1. Navigate to `lib_base − 6` (first standard vector)
2. Each 6-byte group: opcode `4EF9` + 4-byte address
3. Press `C` to disassemble if not auto-detected
4. The 4-byte value is the actual function address — press `G` (Go to) to navigate
5. Name each function with the `.fd` file as reference

---

## References

- NDK39: `exec/execbase.h`, `exec/libraries.h`
- ADCD 2.1: `MakeFunctions`, `MakeLibrary`, `SetFunction`, `SumLibrary`
- [library_jmp_table.md](../05_reversing/static/library_jmp_table.md) — reconstruction workflow
- [lvo_table.md](../04_linking_and_libraries/lvo_table.md) — complete LVO reference tables
