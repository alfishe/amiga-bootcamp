[← Home](../README.md) · [Exec Kernel](README.md)

# ExecBase — Full Structure Reference

## Overview

`ExecBase` is the root structure of AmigaOS, located at absolute address `$4`. It is a `struct Library` extended with all exec kernel state: memory lists, task queues, interrupt vectors, library lists, and hardware abstraction fields.

---

## Locating ExecBase

```c
struct ExecBase *SysBase = *((struct ExecBase **)4);
```

In assembly:
```asm
MOVEA.L  4.W, A6   ; A6 = SysBase
```

---

## Key Field Groups

### Library Header (offset 0)
```c
struct Library  LibNode;     /* +0  — ln_Name = "exec.library" */
                             /* +20 — lib_Version (40 = OS3.1, 44 = OS3.2) */
```

### Interrupts (offset +84)
```c
UWORD   AttnFlags;       /* +0x128 — processor capability flags */
UWORD   AttnResched;     /* +0x12A — reschedule attention flag */
```

### Task Scheduling
| Offset | Field | Description |
|---|---|---|
| +0x128 | `TaskReady` | `struct List` — tasks ready to run |
| +0x132 | `TaskWait` | `struct List` — tasks waiting on signals |
| +0x126 | `IDNestCnt` | Interrupt disable nesting count |
| +0x127 | `TDNestCnt` | Task disable nesting count |

### Memory
| Offset | Field | Description |
|---|---|---|
| +0x130 | `MemList` | `struct List` of `MemHeader` regions |
| +0x134 | `ResourceList` | Resources list |

### Library and Device Lists
| Offset | Field | Description |
|---|---|---|
| +0x17A | `LibList` | `struct List` — loaded libraries |
| +0x182 | `DeviceList` | `struct List` — loaded devices |
| +0x18A | `IntrList` | Interrupt server list |
| +0x192 | `PortList` | Public message ports |
| +0x19A | `TaskList` | All tasks (not just ready/waiting) |

### Vectors and ROM
| Offset | Field | Description |
|---|---|---|
| +0x26 | `SoftVer` | Kickstart software revision |
| +0x10 | `ChkBase` | Checksum of library header |
| +0x222 | `PowerSupplyFrequency` | 50 or 60 Hz |
| +0x21E | `ChipRevBits0` | Chip revision detection flags |

### Chip Revision Flags (`ChipRevBits0`)

| Bit | Constant | Chip |
|---|---|---|
| 4 | `ATNF_68010` | 68010 or better |
| 5 | `ATNF_68020` | 68020 or better |
| 6 | `ATNF_68030` | 68030 |
| 7 | `ATNF_68040` | 68040 |
| 10 | `ATNF_FPU40` | 68040 internal FPU |

---

## Detecting CPU and Chipset

```c
/* CPU: */
if (SysBase->AttnFlags & AFF_68020) { /* 020+ */ }
if (SysBase->AttnFlags & AFF_68040) { /* 040 */ }

/* Chipset (via graphics.library): */
struct GfxBase *gfx = (struct GfxBase *)OpenLibrary("graphics.library", 36);
if (gfx->ChipRevBits0 & GFXB_AA_ALICE) { /* AGA Alice chip */ }
```

---

## ExecBase in IDA Pro

After loading Kickstart ROM:
1. Create a segment at `$4` containing a pointer
2. Follow the pointer to the ExecBase (in ROM)
3. Apply `struct ExecBase` type (from NDK39 headers parsed via `File → Parse C header`)
4. All `N(A6)` offsets auto-annotate as field names

---

## References

- NDK39: `exec/execbase.h` — authoritative field definitions
- ADCD 2.1: exec.library autodoc
- *Amiga ROM Kernel Reference Manual: Exec* — ExecBase chapter
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node0072.html
