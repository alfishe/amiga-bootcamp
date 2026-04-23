[← Home](../README.md) · [Exec Kernel](README.md)

# Resident Modules — RomTag, RTF_AUTOINIT, FindResident

## Overview

AmigaOS ROM and disk-resident modules (libraries, devices, resources) identify themselves via a **RomTag** structure. At boot, exec scans the ROM and loaded segments for RomTags and initialises every module it finds.

---

## struct Resident (RomTag)

```c
/* exec/resident.h — NDK39 */
struct Resident {
    UWORD  rt_MatchWord;    /* always $4AFC — magic identifier */
    struct Resident *rt_MatchTag; /* pointer back to this struct (self-ref) */
    APTR   rt_EndSkip;      /* pointer past end of this module's code */
    UBYTE  rt_Flags;        /* RTF_* flags */
    UBYTE  rt_Version;      /* module version number */
    UBYTE  rt_Type;         /* NT_LIBRARY, NT_DEVICE, NT_RESOURCE, ... */
    BYTE   rt_Pri;          /* initialisation priority (higher = earlier) */
    char  *rt_Name;         /* module name string, e.g. "dos.library" */
    char  *rt_IdString;     /* human-readable ID, e.g. "dos.library 40.1" */
    APTR   rt_Init;         /* init function or InitTable pointer */
};
```

### Magic Word

`rt_MatchWord = $4AFC` is the 68k opcode for `ILLEGAL` — a deliberate trap instruction chosen so that an accidental execution of a RomTag causes an immediate CPU exception rather than silent corruption.

### RTF_ Flags

```c
#define RTF_AUTOINIT (1<<7)  /* use rt_Init as pointer to InitTable */
#define RTF_SINGLETASK (1<<1) /* init runs in single-task context */
#define RTF_COLDSTART  (1<<0) /* init on cold boot only */
```

---

## RTF_AUTOINIT — Automatic Initialisation

When `RTF_AUTOINIT` is set, `rt_Init` points to an **InitTable** rather than a bare function:

```c
struct InitTable {
    ULONG  it_DataSize;   /* size of library instance struct */
    APTR  *it_FuncTable;  /* pointer to function pointer table */
    APTR   it_DataTable;  /* pointer to INITBYTE/INITWORD/INITLONG table */
    APTR   it_InitRoutine;/* pointer to actual LibInit() function */
};
```

exec uses `MakeLibrary()` to allocate the library, install the JMP table, and initialise the data, then calls `it_InitRoutine`. For most libraries, the author only needs to provide `it_FuncTable` and `it_DataTable` and `RTF_AUTOINIT` handles the rest automatically.

---

## Finding a Resident by Name

```c
struct Resident *res = FindResident("dos.library");   /* LVO -60 */
if (res) {
    printf("Found: %s v%d\n", res->rt_Name, res->rt_Version);
}
```

`FindResident` scans `SysBase->ResModules` — the list of all RomTag pointers collected at boot.

---

## ROM Scan at Boot

During exec initialisation, the ROM scanner walks from `$F80000` (Kickstart base) upward looking for the `$4AFC` magic word. For each match it verifies `rt_MatchTag == &rt` (self-referential pointer), confirms `rt_EndSkip` is beyond the RomTag, and adds valid entries to `ResModules`.

The same scan is applied to any loaded segment when `AddResidentModule` is called.

---

## Writing a Minimal RomTag (Assembly)

```asm
; Minimal ROM tag for a library:
        dc.w    $4AFC               ; rt_MatchWord
        dc.l    _RomTag             ; rt_MatchTag (self-ref)
        dc.l    _EndTag             ; rt_EndSkip
        dc.b    RTF_AUTOINIT        ; rt_Flags
        dc.b    1                   ; rt_Version
        dc.b    NT_LIBRARY          ; rt_Type
        dc.b    0                   ; rt_Pri
        dc.l    _Name               ; rt_Name
        dc.l    _IdString           ; rt_IdString
        dc.l    _InitTable          ; rt_Init (InitTable when AUTOINIT)
_Name:  dc.b    "mylib.library", 0
_IdString: dc.b "mylib.library 1.0 (23.4.2026)", 13, 10, 0
        even
_EndTag:
```

---

## References

- NDK39: `exec/resident.h`, `exec/execbase.h`
- ADCD 2.1: `FindResident`, `InitResident`, `AddResidentModule`
- *Amiga ROM Kernel Reference Manual: Exec* — resident modules chapter
