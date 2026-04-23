[← Home](../README.md) · [Exec Kernel](README.md)

# Exception and Trap Handling — M68k on AmigaOS

## Overview

The M68k CPU provides a **256-entry exception vector table** starting at address `$000000`. AmigaOS manages these vectors through `exec.library`, allowing both the OS and user code to install handlers for hardware interrupts, bus errors, and software traps.

---

## Exception Vector Table

| Vector | Address | Exception | AmigaOS Handler |
|---|---|---|---|
| 0 | `$000` | Reset: Initial SSP | (boot value) |
| 1 | `$004` | Reset: Initial PC | ROM entry point |
| 2 | `$008` | Bus Error | Guru Meditation / Enforcer |
| 3 | `$00C` | Address Error | Guru Meditation |
| 4 | `$010` | Illegal Instruction | Guru Meditation |
| 5 | `$014` | Zero Divide | Alert |
| 6 | `$018` | CHK Instruction | Alert |
| 7 | `$01C` | TRAPV | Alert |
| 8 | `$020` | Privilege Violation | Alert |
| 9 | `$024` | Trace | Debug (wack/BareFoot) |
| 10 | `$028` | Line-A Emulator | Unused (soft trap space) |
| 11 | `$02C` | Line-F Emulator | 68040/060.library FPU emulation |
| 12–14 | `$030–$038` | Reserved | — |
| 15 | `$03C` | Uninitialised Interrupt | Alert |
| 24 | `$060` | Spurious Interrupt | — |
| 25–31 | `$064–$07C` | Auto-vector interrupts 1–7 | Exec interrupt dispatcher |
| 32–47 | `$080–$0BC` | TRAP #0–#15 | User-installable traps |
| 48–63 | `$0C0–$0FC` | Reserved (FPU) | 68881/68882 exception handlers |
| 64–255 | `$100–$3FC` | User-defined vectors | User |

---

## TRAP Instructions — Software Interrupts

`TRAP #n` (n = 0–15) generates a software exception. AmigaOS uses:

| TRAP | User |
|---|---|
| `TRAP #0` | exec.library `Supervisor()` — switch to supervisor mode |
| `TRAP #1–#14` | Available for user programs |
| `TRAP #15` | Remote debugger breakpoint (BareFoot/wack) |

---

## Installing an Exception Handler

```c
/* Using exec.library SetExcept/SetTrapHandler (not recommended): */
/* Direct vector patching in supervisor mode: */

APTR OldVector;

__asm void MyTrapHandler(void)
{
    /* Save registers, examine stack frame */
    /* ... handle trap ... */
    rte
}

/* Install: */
Supervisor(function() {
    OldVector = *(APTR *)0x0B0;     /* TRAP #12 vector */
    *(APTR *)0x0B0 = MyTrapHandler;
});
```

---

## Guru Meditation

When a fatal exception occurs (Bus Error, Address Error), exec.library displays:

```
Software Failure.   Press left mouse button to continue.
Guru Meditation #XXYYYYYY.ZZZZZZZZ
```

| Field | Meaning |
|---|---|
| `XX` | Alert type: $00=recovery possible, $80=dead-end |
| `YYYYYY` | Error code (subsystem + specific error) |
| `ZZZZZZZZ` | Address where error occurred |

### Common Guru Codes

| Code | Meaning |
|---|---|
| `$80000003` | Address Error (dead-end) |
| `$80000004` | Illegal instruction (dead-end) |
| `$81000005` | exec: No memory |
| `$82000005` | graphics: No memory |
| `$87000007` | trackdisk: No disk |
| `$04000001` | exec: Recoverable alert |
| `$00000001` | No memory (recoverable) |

---

## References

- Motorola: *MC68000 Family Reference Manual* — exception processing
- NDK39: `exec/alerts.h` — alert code definitions
- RKRM: Exception chapter
