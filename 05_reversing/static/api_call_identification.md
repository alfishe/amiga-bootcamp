[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Identifying OS API Calls in Disassembly

## Background: How AmigaOS Library Calls Work

Before diving into identification techniques, it helps to understand the mechanics from first principles.

### What is a Shared Library?

On AmigaOS, a **shared library** is a block of code loaded into RAM once and shared by every program that needs it. Programs don't link the OS code into their own executable — they call it indirectly at runtime. This keeps executables small and allows the OS to be upgraded without relinking every application.

Examples: `dos.library`, `graphics.library`, `intuition.library`.

### What is a Library Base?

When you open a library, exec returns a pointer to the **library base** — a `struct Library` that lives in RAM. Immediately *before* this pointer (at negative offsets) sits the **JMP table**: a sequence of `JMP <address>` instructions, one per library function.

```
Memory layout:

lib_base - 30:  JMP Open_impl        ← first user function
lib_base - 24:  JMP Reserved
lib_base - 18:  JMP Expunge
lib_base - 12:  JMP Close
lib_base -  6:  JMP Open (standard)
lib_base +  0:  struct Library       ← pointer returned by OpenLibrary()
lib_base +  N:  private library data
```

Every program that wants to call `dos.library Open()` stores the library base somewhere and calls `JSR -30(A6)`, where A6 holds the library base.

---

## What is an LVO?

**LVO** stands for **Library Vector Offset**. It is the negative byte offset from the library base to a specific function's JMP table slot.

The formula is:
```
LVO = −6 × (slot_index + 1)

slot 0 (Open standard):  −6
slot 1 (Close standard): −12
slot 2 (Expunge):        −18
slot 3 (Reserved):       −24
slot 4 (first user fn):  −30   ← dos.library Open()
slot 5:                  −36   ← dos.library Close()
...
```

So `JSR -30(A6)` means "call the function at LVO −30 in the library whose base is in A6." Every unique LVO in every library maps to exactly one function.

### Why Negative Offsets?

The JMP table grows **downward** in memory from the library base. Using negative offsets means programs only need to store a single pointer (the library base) and derive all function entry points from it with a constant displacement. This is the same trick used by C++ vtables.

---

## What is an .fd File?

**`.fd` files** (Function Descriptor files) are part of the Amiga NDK (Native Developer Kit). They are simple text files that declare every public function in a library: its name, argument registers, and LVO (called the **bias** in `.fd` terminology).

### Example: `dos_lib.fd` (excerpt)

```
##base _DOSBase
##bias 30
##public
Open(name,accessMode)(d1,d2)
##bias 36
Close(file)(d1)
##bias 42
Read(file,buffer,length)(d1,d2,d3)
##bias 48
Write(file,buffer,length)(d1,d2,d3)
##bias 54
Input()(-)
##bias 60
Output()(-)
##bias 138
Delay(timeout)(d1)
```

Reading this:
- `##base _DOSBase` — the global variable that holds the library base
- `##bias 30` — the **positive** bias; the actual call offset is `−30`
- `Open(name,accessMode)(d1,d2)` — function name, argument names, and the registers each argument goes in

So `##bias 30` means LVO `−30`. When you see `JSR (-30,A6)` in disassembly and A6 holds `DOSBase`, that is `dos.library Open()`.

### Where are .fd files?

In the NDK39 distribution at:
```
NDK39/
  fd/
    dos_lib.fd
    exec_lib.fd
    graphics_lib.fd
    intuition_lib.fd
    ...
```

They are plain text — open any with a text editor.

---

## The Canonical Call Pattern

Every AmigaOS library call in disassembly looks like this:

```asm
MOVEA.L  (_DOSBase).L, A6    ; (1) load the library base into A6
JSR      (-30,A6)            ; (2) call function at LVO -30 = Open()
; D0 now contains the return value
```

Sometimes the base is loaded once and reused:
```asm
MOVEA.L  (_DOSBase).L, A6
JSR      (-30,A6)     ; Open
...
; A6 still holds DOSBase — no reload needed
JSR      (-48,A6)     ; Write
```

And for `exec.library`, programs often use the fixed address `$4` directly:
```asm
MOVEA.L  4.W, A6             ; exec.library base is always at $4
MOVEQ    #40, D0             ; minimum version
LEA      _str_dos(PC), A1    ; "dos.library"
JSR      (-552,A6)           ; exec.library OpenLibrary(A1,D0)
MOVE.L   D0, _DOSBase        ; save result for later
```

---

## Step-by-Step: Tracing OS Calls in IDA Pro

### Step 1 — Find OpenLibrary calls at startup

Search for `JSR (-552,A6)` — that is always `exec.library OpenLibrary`. The instruction immediately before it loads A1 with a library name string.

```asm
LEA      (_str_dos).L, A1     ; → xref this to see "dos.library"
MOVEQ    #40, D0
MOVEA.L  4.W, A6
JSR      (-552,A6)            ; OpenLibrary("dos.library", 40)
MOVE.L   D0, (_DOSBase).L     ; ← label this global "_DOSBase"
```

Press `N` in IDA on the `_DOSBase` write to name the variable.

### Step 2 — Find all reads of that library base

Press `X` on `_DOSBase` to show all cross-references. Each xref is either a write (the open) or a read (before a JSR).

### Step 3 — Resolve each JSR to a function name

For each `JSR (-N,A6)` where A6 holds `_DOSBase`:
1. Look up `N` in `dos_lib.fd` under `##bias N`
2. Read the function name
3. Press `N` in IDA on the JSR instruction's displacement to annotate it

After annotation:
```asm
MOVEA.L  (_DOSBase).L, A6
JSR      (Open,A6)           ; was: JSR (-30,A6)
```

### Step 4 — Note argument registers

From `dos_lib.fd`:
```
Open(name,accessMode)(d1,d2)
```
So immediately before the JSR:
- `D1` is loaded with the filename pointer
- `D2` is loaded with the access mode (`MODE_OLDFILE` = 1005, `MODE_NEWFILE` = 1006)

---

## Quick LVO Reference: dos.library

| LVO | Bias | Function | Args | Return |
|---|---|---|---|---|
| −30 | 30 | `Open` | D1=name, D2=mode | D0=BPTR handle (0=fail) |
| −36 | 36 | `Close` | D1=handle | — |
| −42 | 42 | `Read` | D1=handle, D2=buf, D3=len | D0=actual (−1=fail) |
| −48 | 48 | `Write` | D1=handle, D2=buf, D3=len | D0=actual |
| −54 | 54 | `Input` | — | D0=stdin handle |
| −60 | 60 | `Output` | — | D0=stdout handle |
| −66 | 66 | `IoErr` | — | D0=last error code |
| −78 | 78 | `CreateDir` | D1=name | D0=lock |
| −84 | 84 | `CurrentDir` | D1=lock | D0=old lock |
| −90 | 90 | `Lock` | D1=name, D2=mode | D0=lock |
| −96 | 96 | `UnLock` | D1=lock | — |
| −102 | 102 | `DupLock` | D1=lock | D0=new lock |
| −108 | 108 | `Examine` | D1=lock, D2=fib | D0=bool |
| −120 | 120 | `ExNext` | D1=lock, D2=fib | D0=bool |
| −126 | 126 | `Info` | D1=lock, D2=infoblock | D0=bool |
| −132 | 132 | `Execute` | D1=string, D2=input, D3=output | D0=bool |
| −138 | 138 | `Delay` | D1=ticks | — |
| −144 | 144 | `DateStamp` | D1=datestamp | D0=datestamp |
| −150 | 150 | `Exit` | D1=returnCode | — |
| −156 | 156 | `LoadSeg` | D1=name | D0=seglist |
| −162 | 162 | `UnLoadSeg` | D1=seglist | — |

## Quick LVO Reference: exec.library (selected)

| LVO | Bias | Function | Args | Return |
|---|---|---|---|---|
| −6 | 6 | `Supervisor` | A5=func | — |
| −120 | 120 | `Forbid` | — | — |
| −126 | 126 | `Permit` | — | — |
| −132 | 132 | `Disable` | — | — |
| −138 | 138 | `Enable` | — | — |
| −168 | 168 | `FindTask` | A1=name | D0=task |
| −174 | 174 | `SetTaskPri` | A1=task, D0=pri | D0=old |
| −192 | 192 | `Signal` | A1=task, D0=signals | — |
| −198 | 198 | `AllocMem` | D0=size, D1=attrs | D0=ptr |
| −210 | 210 | `FreeMem` | A1=ptr, D0=size | — |
| −234 | 234 | `Wait` | D0=signals | D0=set |
| −270 | 270 | `AddPort` | A1=port | — |
| −276 | 276 | `FindName` | A0=list, A1=name | D0=node |
| −378 | 378 | `PutMsg` | A0=port, A1=msg | — |
| −384 | 384 | `GetMsg` | A0=port | D0=msg |
| −408 | 408 | `WaitPort` | A0=port | D0=msg |
| −420 | 420 | `SetFunction` | A1=lib, A0=lvo, D0=func | D0=old |
| −552 | 552 | `OpenLibrary` | A1=name, D0=ver | D0=base |
| −558 | 558 | `CloseLibrary` | A1=lib | — |

Full tables: [[lvo_table.md](../../04_linking_and_libraries/lvo_table.md)](../../../04_linking_and_libraries/lvo_table.md)

---

## Automated IDA Script

```python
# apply_dos_lvos.py — run from IDA's File → Script command
import idaapi, idc, idautils

DOS_LVO = {
    -30: "Open",   -36: "Close",   -42: "Read",    -48: "Write",
    -54: "Input",  -60: "Output",  -66: "IoErr",   -132: "Execute",
    -138: "Delay", -156: "LoadSeg",-162: "UnLoadSeg",
}

EXEC_LVO = {
    -120: "Forbid",   -126: "Permit", -132: "Disable",  -138: "Enable",
    -198: "AllocMem", -210: "FreeMem",-234: "Wait",
    -378: "PutMsg",   -384: "GetMsg", -408: "WaitPort",
    -420: "SetFunction", -552: "OpenLibrary", -558: "CloseLibrary",
}

def apply_lvos(lib_global_name, lvo_map):
    ea = idc.get_name_ea_simple(lib_global_name)
    if ea == idc.BADADDR:
        print(f"Global {lib_global_name} not found")
        return
    lib_ptr = idc.get_wide_dword(ea)
    for lvo, name in lvo_map.items():
        jmp_ea  = lib_ptr + lvo
        # JMP ABS.L opcode: 4EF9, target at +2
        target  = idc.get_wide_dword(jmp_ea + 2)
        if target != 0xFFFFFFFF:
            idc.set_name(target, f"{lib_global_name[1:]}_{name}",
                         idaapi.SN_NOWARN)
            print(f"  {lvo:+5d} → {name} @ {target:#010x}")

apply_lvos("_DOSBase",  DOS_LVO)
apply_lvos("_SysBase",  EXEC_LVO)
```

---

## Identifying Unknown Library Calls

If you encounter `JSR (-N,A6)` and don't know which library A6 holds:

1. Trace A6 backward in IDA (`View → Register tracking`) to its last write
2. The write is `MOVEA.L (some_global).L, A6` — name that global
3. Trace *that* global backward to its `MOVE.L D0, ...` after an `OpenLibrary` call
4. The string argument to OpenLibrary names the library
5. Look up LVO `−N` in the matching `.fd` file

---

## References

- NDK39: `fd/` directory — all library `.fd` files (plain text, open in any editor)
- [lvo_table.md](../../04_linking_and_libraries/lvo_table.md) — formatted LVO tables
- `static/library_jmp_table.md` — JMP table layout and IDA scripting
- [fd_files.md](../../04_linking_and_libraries/fd_files.md) — `.fd` file format specification
- ADCD 2.1 Autodocs online: http://amigadev.elowar.com/read/ADCD_2.1/
