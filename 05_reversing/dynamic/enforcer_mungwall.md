[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Enforcer and MungWall — Memory Violation Tracing

## Overview

**Enforcer** (by Michael Sinz) and **MungWall** are the two canonical Amiga memory debugging tools. They catch illegal memory accesses and heap corruption at runtime, providing the equivalent of AddressSanitizer for AmigaOS.

---

## Enforcer

Enforcer uses the 68020+ MMU (or software patching on 68000) to trap accesses to:
- Address `$0000–$07FF` (lower 2 KB — reserved vectors and exec structures)
- Odd-addressed word/longword reads
- Accesses above the installed RAM
- Writes to ROM addresses

### Installation

```
; AmigaOS Shell:
run enforcer
; or for logging:
run enforcer QUIET LOG enforcer.log
```

Enforcer patches the `BusError` exception vector (`$8`). Any illegal access causes a bus error, which Enforcer catches, logs, and (usually) continues.

### Output Format

```
ENFORCER HIT: by Unknown (Task: "DPaint" at $001234AB)
  Program Counter: $0023AB12
  Address Accessed: $0000012C   (read longword)
  Stack Dump: $001234C0 $0001A2B4 ...
```

- **Program Counter** — instruction that caused the hit
- **Address Accessed** — illegal address
- Cross-reference PC against `HUNK_SYMBOL` names or IDA disassembly

### Common Causes

| Hit Pattern | Likely Cause |
|---|---|
| Access to `$0–$3FF` | NULL pointer dereference |
| Access to `$4` (SysBase) without read | Null exec base |
| Odd address read (word/long) | Misaligned pointer |
| Access to `$B80000–$BFFFFF` | CIA access without correct alignment |
| Write to ROM `$F80000+` | Write to Kickstart ROM |

---

## MungWall

MungWall fills `AllocMem()` allocations with a known pattern (`$ABADCAFE`) and adds guard longwords before and after each block (`$DEADBEEF`). On `FreeMem()`, it verifies the guards.

### What It Catches

- **Heap underrun** — write before the allocated block (guard before = corrupted)
- **Heap overrun** — write past the end of block (guard after = corrupted)
- **Use after free** — block is filled with `$DEADBEEF` on free; reads from it will fail if Enforcer is also running

### Installation

```
run mungwall
```

### Output on Corruption

```
MUNGWALL: Block $001A2000 (size 128) has been overwritten!
  Header guard: OK
  Trailer guard: CORRUPTED at +132
  Caller: $0023BC44  (FreeMem called from here)
```

---

## Combined Workflow

1. `run mungwall` first — patches AllocMem/FreeMem
2. `run enforcer` — adds MMU-level illegal access detection
3. Launch the suspect program
4. Any crash produces Enforcer + MungWall output on the serial port / `enforcer.log`
5. Cross-reference the PC value with `HUNK_SYMBOL` or IDA to find the exact line

---

## Serial Port Logging

Both tools output via `kprintf` to serial port (115200 8N1). Capture on host:

```bash
# macOS / Linux:
screen /dev/cu.usbserial-XXXX 115200
# or
minicom -D /dev/cu.usbserial-XXXX -b 115200
```

---

## References

- Enforcer: Michael Sinz — available on Aminet (`util/misc/Enforcer.lha`)
- MungWall: original CBM debug tool, available on Aminet
- `dynamic/serial_debug.md` — serial output setup
- *Amiga ROM Kernel Reference Manual: Libraries* — exec memory management
