[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Serial Debugging — kprintf and Serial Output

## Overview

The Amiga's built-in serial port is the primary low-level debugging channel. `kprintf()` (kernel printf) and `RawPutChar()` write directly to the serial hardware, bypassing `dos.library` and working even from interrupt context or before OS initialization.

---

## `kprintf()` — Kernel Printf

`kprintf()` is a ROM debug function present in Kickstart 1.3 and later debug ROMs. It formats a string and outputs each character via `RawPutChar`.

```c
/* Prototype (exec internal, not in NDK — declare manually): */
void kprintf(const char *fmt, ...);
/* Arguments in: D1=fmt, stack args (unlike standard AmigaOS register ABI) */
```

### Calling `kprintf` from Assembly

```asm
MOVEA.L  4.W, A6            ; SysBase
LEA      _fmt_str(PC), A0   ; format string
MOVE.L   A0, -(SP)          ; push as stack argument
MOVE.L   A0, D1             ; some implementations use D1
JSR      (-$F0,A6)          ; RawDoFmt or debug rom entry
; OR for ROM debug builds:
JSR      _kprintf
```

> [!NOTE]
> `kprintf` is **not available** in standard Kickstart 3.1 release ROMs. Use `debug.lib` stubs (`dprintf`) or `RawDoFmt + RawPutChar` instead.

---

## `RawDoFmt` + `RawPutChar` — Universal Approach

This works on **all** Kickstart versions (1.2+):

```c
/* Format into a buffer and output via RawPutChar */
static void serial_putchar(UBYTE c, APTR dummy) {
    /* write directly to serial data register */
    volatile UWORD *SERDATR = (UWORD *)0xDFF018;
    volatile UWORD *SERDATW = (UWORD *)0xDFF030;
    volatile UWORD *SERDATSTAT;
    /* Wait for TBE (transmit buffer empty) */
    while (!(*SERDATR & 0x2000));
    *SERDATW = 0x0100 | c;   /* 8 bits + start bit */
}

void dbg_printf(const char *fmt, ...) {
    UBYTE buf[256];
    va_list args;
    va_start(args, fmt);
    /* RawDoFmt(fmt, args, putChar, buf) */
    RawDoFmt((STRPTR)fmt, &args,
             (VOID (*)())serial_putchar, buf);
    va_end(args);
}
```

Or simpler — write to the serial hardware directly:

```c
static void SerPutChar(UBYTE c) {
    while (!(*((volatile UWORD *)0xDFF018) & 0x2000)); /* wait TBE */
    *((volatile UWORD *)0xDFF030) = 0x0100 | c;
}
```

---

## `debug.lib` (SAS/C)

SAS/C ships `debug.lib` providing `dprintf`:

```c
#include <debug.h>
dprintf("mylib: Open called, name=%s\n", name);
```

Output goes to the serial port at the rate set by SERPER (default 9600 baud on startup, 115200 if set).

---

## Setting Baud Rate

```c
/* Set serial to 115200 baud (PAL, 3.546895 MHz clock): */
/* SERPER = (clock / (16 * baud)) - 1 */
/* = (3546895 / (16 * 115200)) - 1 = 0 */
volatile UWORD *SERPER = (UWORD *)0xDFF032;
*SERPER = 0x0000;   /* 115200 on PAL */
```

---

## Host-Side Capture

```bash
# macOS (USB-serial adapter):
screen /dev/cu.usbserial-XXXX 115200
# or:
stty -f /dev/cu.usbserial-XXXX 115200 raw && cat /dev/cu.usbserial-XXXX
```

MiSTer FPGA: the UART bridge is exposed on the MiSTer IO board or via the DE10-Nano UART.

---

## References

- NDK39: `exec/execbase.h` — `RawDoFmt`, `RawPutChar` LVOs
- [paula_serial.md](../../01_hardware/ocs_a500/paula_serial.md) — SERPER, SERDATR, SERDATW register details
- Aminet: `debug/misc/dprintf.lha`
