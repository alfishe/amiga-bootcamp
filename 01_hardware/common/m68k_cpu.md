[← Home](../../README.md) · [Hardware](../README.md)

# M68k CPU on the Amiga

## Overview

AmigaOS runs on the Motorola 68000 family exclusively. The CPU operates in two privilege modes and interacts with the custom chips via the shared 16/32-bit bus arbitrated by Agnus/Alice.

## Privilege Modes

| Mode | SR[13] (S-bit) | Stack Pointer | Access |
|---|---|---|---|
| **Supervisor** | 1 | SSP (A7') | Full hardware access |
| **User** | 0 | USP (A7) | Restricted — no privileged instructions |

AmigaOS runs entirely in **supervisor mode**. User-mode tasks switch to supervisor via `Supervisor()` or trap instructions. The OS does not enforce user-mode isolation — all tasks share one address space.

## Register Set

```
D0–D7   Data registers (32-bit)
A0–A6   Address registers (32-bit)
A7      Stack pointer (USP in user mode, SSP in supervisor mode)
PC      Program counter
SR      Status register (CCR + supervisor bits)
```

**CCR (Condition Code Register) — lower byte of SR:**
```
bit 4: X  (extend)
bit 3: N  (negative)
bit 2: Z  (zero)
bit 1: V  (overflow)
bit 0: C  (carry)
```

**SR upper byte (supervisor only):**
```
bit 15: T1 (trace mode — single-step)
bit 14: T0
bit 13: S  (supervisor state)
bit 10-8: I2-I0 (interrupt mask level, 0–7)
```

## Exception Vector Table

Located at **$000000** (physical), shadowed from Kick ROM into Chip RAM on boot.

| Offset | Vector | Description |
|---|---|---|
| $000 | Reset SSP | Initial supervisor stack pointer |
| $004 | Reset PC | Initial program counter (ROM entry) |
| $008 | Bus Error | Access fault |
| $00C | Address Error | Odd-address word/long access |
| $010 | Illegal Instruction | Undefined opcode |
| $014 | Divide by Zero | DIVS/DIVU by zero |
| $018 | CHK | CHK instruction bound check fail |
| $01C | TRAPV / cpTRAPcc | Overflow trap |
| $020 | Privilege Violation | User-mode privileged instruction |
| $024 | Trace | Single-step trap |
| $028 | Line 1010 (A-line) | Opcode $Axxx — OS trap dispatch |
| $02C | Line 1111 (F-line) | Opcode $Fxxx — FPU / emulation |
| $060 | Spurious Interrupt | No response to interrupt acknowledge |
| $064 | Level 1 Autovector | CIA-B timer / serial / disk |
| $068 | Level 2 Autovector | CIA-A, software |
| $06C | Level 3 Autovector | VBL, copper, blitter |
| $070 | Level 4 Autovector | Audio, disk DMA |
| $074 | Level 5 Autovector | Serial port |
| $078 | Level 6 Autovector | CIA / ext interrupt |
| $07C | Level 7 Autovector | NMI (not maskable) |
| $080–$0BC | TRAP #0–#15 | Software traps |

## AmigaOS Use of Exception Vectors

- **A-Line ($028):** AmigaOS uses this for its internal library call dispatch on some early titles; modern code uses direct JSR via library base.
- **Level 3 ($06C):** Vertical Blank interrupt — exec's `AddIntServer(INTB_VERTB, ...)` chains here.
- **Level 6 ($078):** CIA interrupts chain here; exec dispatches to `INTB_EXTER` servers.
- **TRAP #0 ($080):** Used by `Supervisor()` to enter supervisor mode from user code.

## Interrupt Priority Levels

AmigaOS maps hardware interrupt levels to internal interrupt bits (`INTENA`/`INTREQ`):

| IPL | Source | INTENA bits |
|---|---|---|
| 1 | Serial TX, disk block | `INTB_TBE`, `INTB_DSKBLK` |
| 2 | Software (PostIntServer) | `INTB_SOFTINT` |
| 3 | VBlank, copper, blitter | `INTB_VERTB`, `INTB_COPPER`, `INTB_BLIT` |
| 4 | Audio ch 0–3, disk DMA | `INTB_AUD0`–`INTB_AUD3`, `INTB_DSKSYNC` |
| 5 | Serial RX | `INTB_RBF` |
| 6 | External / CIA | `INTB_EXTER` |
| 7 | NMI (rarely used) | — |

## CPU Detection at Runtime

AmigaOS stores CPU capability flags in `ExecBase->AttnFlags` (offset $128):

```c
#include <exec/execbase.h>

struct ExecBase *SysBase = *((struct ExecBase **)4);
UWORD attn = SysBase->AttnFlags;

if (attn & AFF_68020) { /* 68020+ present */ }
if (attn & AFF_68030) { /* 68030+ present */ }
if (attn & AFF_68040) { /* 68040+ present */ }
if (attn & AFF_68060) { /* 68060 present  */ }
if (attn & AFF_FPU)   { /* FPU present    */ }
if (attn & AFF_68881) { /* 68881/68882    */ }
```

**AttnFlags bit definitions** (`exec/execbase.h`):
```c
#define AFF_68010   (1<<0)
#define AFF_68020   (1<<1)
#define AFF_68030   (1<<2)
#define AFF_68040   (1<<3)
#define AFF_68881   (1<<4)  /* on-chip FPU or external 68881 */
#define AFF_FPU     (1<<4)
#define AFF_68882   (1<<5)
#define AFF_FPU40   (1<<6)  /* 040/060 on-chip FPU */
#define AFF_68060   (1<<7)
```

## Key Instruction Subsets by CPU

| Instruction | 68000 | 68020 | 68030 | 68040 |
|---|---|---|---|---|
| MULS/MULU 16×16 | ✓ | ✓ | ✓ | ✓ |
| MULS/MULU 32×32 | ✗ | ✓ | ✓ | ✓ |
| Bit-field (BFEXTU etc.) | ✗ | ✓ | ✓ | ✓ |
| CALLM/RTM | ✗ | ✓ | ✗ | ✗ |
| CAS/CAS2 | ✗ | ✓ | ✓ | ✓ |
| LPSTOP | ✗ | ✗ | ✓ | ✓ |
| CINV/CPUSH | ✗ | ✗ | ✓ | ✓ |

## References

- Motorola *M68000 Family Programmer's Reference Manual* (M68000PM/AD)
- ADCD 2.1 Hardware Manual: http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node0000.html
- NDK39: `exec/execbase.h` — `AttnFlags` definitions
