[← Home](../README.md) · [Boot Sequence](README.md)

# Kickstart Initialisation — ROM Scan, ExecBase, Resident Modules

## Overview

After hardware init, the Kickstart ROM creates `ExecBase` and scans for **resident modules** — the OS components compiled into ROM. This process builds the entire OS kernel from tagged structures embedded in the ROM image.

---

## ExecBase Creation

1. Allocate ExecBase structure at a known address (end of Chip RAM)
2. Initialise memory lists, library list, device list, resource list
3. Store ExecBase pointer at **address `$000004`** — the global `SysBase`
4. Initialise the Supervisor stack, interrupt vectors, trap vectors

```
After this step:
  *(ULONG *)4 == ExecBase pointer
  SysBase->LibNode.lib_Version == Kickstart version
```

---

## Resident Module Scan

The ROM scanner searches for **RomTag** markers (`$4AFC`) throughout the ROM address range:

```c
struct Resident {
    UWORD rt_MatchWord;     /* $4AFC — magic marker */
    struct Resident *rt_MatchTag; /* pointer to self (verification) */
    APTR  rt_EndSkip;       /* skip past this address */
    UBYTE rt_Flags;         /* RTF_COLDSTART, RTF_SINGLETASK, etc. */
    UBYTE rt_Version;       /* version number */
    UBYTE rt_Type;          /* NT_LIBRARY, NT_DEVICE, NT_RESOURCE */
    BYTE  rt_Pri;           /* init priority (higher = earlier) */
    char *rt_Name;          /* module name */
    char *rt_IdString;      /* version string */
    APTR  rt_Init;          /* init function or auto-init table */
};
```

### Scan Algorithm

```
for addr in ROM_START to ROM_END step 2:
    if *(UWORD *)addr == $4AFC:
        tag = (struct Resident *)addr
        if tag->rt_MatchTag == tag:  /* self-pointer validates */
            add to resident list
            addr = tag->rt_EndSkip  /* skip past module */
```

---

## Initialisation Phases

Residents are initialised in **priority order** within each phase:

### Phase 1: RTF_COLDSTART (flags bit 0)

Called during cold boot, single-tasking (no scheduler yet):

| Priority | Module | Description |
|---|---|---|
| 126 | `exec.library` | Core kernel |
| 120 | `expansion.library` | AutoConfig Zorro boards |
| 105 | `68040.library` | CPU trap handlers (if present) |
| 100 | `utility.library` | Tag/hook support |
| 70 | `graphics.library` | Display init |
| 50 | `layers.library` | Clipping layers |
| 50 | `intuition.library` | GUI subsystem |
| 40 | `timer.device` | Timing services |
| 30 | `keyboard.device` | Keyboard |
| 20 | `input.device` | Input event merging |
| 10 | `trackdisk.device` | Floppy |
| −50 | `dos.library` | AmigaDOS file system |
| −120 | `ramlib` | Disk-based library/device loader |

### Phase 2: RTF_SINGLETASK

Runs after all COLDSTART modules but before multitasking begins. Used by strap (bootstrap) module.

### Phase 3: RTF_AFTERDOS

Runs after DOS is available. External disk-based modules.

---

## After Resident Init

1. Multitasking enabled (scheduler starts)
2. `dos.library` creates initial CLI process
3. Boot task launches `strap` → reads boot block from DF0: or boot device
4. Control passes to `startup-sequence`

---

## References

- NDK39: `exec/resident.h`
- RKRM: Resident modules chapter
