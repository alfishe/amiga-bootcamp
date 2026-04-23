[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Recovering Data Structures

## Overview

Amiga executables use OS structures extensively — `ExecBase`, `Node`, `Process`, `IORequest`, etc. This document describes how to recover and annotate these structures in disassembly by matching field access patterns against NDK39 header offsets.

---

## The MOVE.L offset(An),Dm Pattern

Structure field accesses appear as:

```asm
MOVEA.L  _DOSBase, A6
MOVE.L   ($17A,A6), A0     ; SysBase->LibList at offset +0x17A
MOVE.L   (A0), A1           ; lh_Head
```

The key is the **base register** and **constant offset**. Match the offset against known structure definitions.

---

## Common Structures and Key Offsets

### `struct ExecBase` (at absolute address `$4`)

| Offset | Field | Type |
|---|---|---|
| +0 | `LibNode` | `struct Library` |
| +0x128 | `TaskReady` | `struct List` |
| +0x132 | `TaskWait` | `struct List` |
| +0x17A | `LibList` | `struct List` |
| +0x182 | `DeviceList` | `struct List` |
| +0x21E | `ChipRevBits0` | `UWORD` |
| +0x280 | `MemList` | `struct List` |

### `struct Node` (8 bytes)

| Offset | Field |
|---|---|
| +0 | `ln_Succ` (next node) |
| +4 | `ln_Pred` (prev node) |
| +8 | `ln_Type` (UBYTE) |
| +9 | `ln_Pri` (BYTE priority) |
| +10 | `ln_Name` (STRPTR) |

List traversal:
```asm
MOVEA.L  lh_Head, A0    ; first node
.loop:
    TST.L   (A0)        ; ln_Succ == NULL?
    BEQ.S   .done
    ; process node at A0
    MOVEA.L (A0), A0    ; A0 = ln_Succ
    BRA.S   .loop
```

### `struct Process` (extends `struct Task`)

| Offset | Field |
|---|---|
| +0 | `pr_Task` (struct Task) |
| +92 | `pr_MsgPort` |
| +128 | `pr_CLI` (BPTR, non-NULL if CLI) |
| +172 | `pr_SegList` (BPTR to segment list) |

Detection in disassembly:
```asm
MOVE.L  ($80,A4), D0    ; pr_CLI at offset +0x80
BEQ.S   .wb_launch      ; NULL = Workbench
```

### `struct IORequest` / `struct IOStdReq`

| Offset | Field |
|---|---|
| +0 | `io_Message` (struct Message) |
| +20 | `io_Device` |
| +24 | `io_Unit` |
| +28 | `io_Command` (UWORD) |
| +30 | `io_Flags` (UBYTE) |
| +32 | `io_Error` (BYTE) |
| +36 | `io_Length` (ULONG) |
| +40 | `io_Actual` (ULONG) |
| +44 | `io_Data` (APTR) |
| +48 | `io_Offset` (ULONG) |

---

## Annotating Structures in IDA Pro

### Define a structure type:

1. `View → Open Subviews → Local Types` → `Insert` → paste C struct definition
2. IDA parses the struct and creates a type entry
3. Navigate to the base register in disassembly
4. Press `T` (structure offset) on any `offset(An)` operand
5. Select the struct type → all accesses auto-annotated

### Import NDK39 headers:

Use `File → Load file → Parse C header file` → select `exec/execbase.h`, `exec/tasks.h`, etc. from NDK39.

---

## Exec Node Traversal Loops

A recurring pattern: walking the `LibList` or `DeviceList`:

```asm
; Annotated after struct recovery:
MOVEA.L  SysBase, A6
LEA      (LibList,A6), A0     ; &SysBase->LibList
MOVEA.L  (lh_Head,A0), A1    ; first lib node
.scan:
    MOVEA.L (ln_Succ,A1), A2 ; peek next
    TST.L   A2
    BEQ.S   .not_found
    ; compare ln_Name string
    MOVEA.L (ln_Name,A1), A0
    JSR     ___strcmp
    TST.L   D0
    BEQ.S   .found
    MOVEA.L A2, A1
    BRA.S   .scan
```

---

## References

- NDK39: `exec/execbase.h`, `exec/tasks.h`, `exec/nodes.h`, `exec/io.h`
- `06_exec_os/exec_base.md` — full ExecBase field listing
- `06_exec_os/lists_nodes.md` — MinList/List traversal
- IDA Pro: Structure subview, Local Types, T hotkey for struct offset
