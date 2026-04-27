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

---

## Decision Guide — Enforcer vs MungWall vs Manual Debugging

| Scenario | Use | Why |
|---|---|---|
| Random Guru Meditation, unknown cause | Both | Enforcer catches the access violation; MungWall catches the corruption that caused it |
| Reproducible crash at known address | Enforcer first | Identifies the exact instruction and register state at the crash |
| Heap data corruption (silent, no crash) | MungWall | Guards catch overwrites on FreeMem — may be the only detection |
| Use-after-free bugs | Both | MungWall poisons freed blocks; Enforcer traps reads from unmapped freed pages |
| 68000 (no MMU) | MungWall only | Enforcer requires 68020+ MMU for hardware trapping |
| MiSTer FPGA / emulation | Both (if MMU implemented) | Verify MMU implementation supports Enforcer's page-level trapping |

---

## Named Antipatterns

### 1. "The Ignored Hit"

**What it looks like** — seeing an Enforcer hit, noting the PC, but dismissing it because "the program still runs":

```
ENFORCER HIT: READ-WORD FROM $00000012
  PC: $0023AB12
```

**Why it fails:** Enforcer catches the violation and *allows the program to continue* by emulating the access or returning dummy data. The crash may not happen immediately — but the corruption is real. A null pointer read that "works" because Enforcer returned `$00000000` may cause a crash 10 minutes later when that zero propagates to a pointer dereference.

**Correct:** Every Enforcer hit is a real bug. Fix them all, even if the program appears to survive.

### 2. "The Missing MungWall on Exit"

**What it looks like** — running MungWall, seeing clean output during the program, but not checking on program exit:

```
run mungwall
myapp
; No MungWall output during run — looks clean!
; But on exit, all allocations are freed — that's when guards are checked
```

**Why it fails:** MungWall validates guards at `FreeMem()` time, not at corruption time. If the program corrupts a buffer, the corruption is detected only when that buffer is freed — typically at program exit. If you don't capture exit-time output, you miss the report.

**Correct:** Always capture serial output until the program fully exits and the CLI prompt returns.

---

## Use-Case Cookbook

### Track Down a Heap Overflow

1. `run mungwall` — intercepts AllocMem/FreeMem
2. `run enforcer QUIET LOG enforcer.log` — catches illegal accesses
3. Launch the program
4. Reproduce the crash
5. Check `enforcer.log` and serial output
6. If MungWall reports "Trailer guard CORRUPTED at +132":
   - The allocation at the reported address + the offset is the corruption site
   - Walk backward from `FreeMem` PC to find the caller that corrupted it
   - Set a **hardware write watchpoint** on the guard address using Enforcer's MMU capability

### Verify All Allocations Are Freed (Leak Detection)

MungWall can report unfreed allocations at exit:

```bash
run mungwall LEAKCHECK
myapp
# Output on exit:
# MUNGWALL: 3 blocks still allocated (48 bytes total):
#   $001A2000: size=16, alloc PC=$0023BC44
#   $001A3000: size=16, alloc PC=$0023BC44
#   $001A4000: size=16, alloc PC=$0023BD12
```

Cross-reference the alloc PCs with IDA to find the leaking code.

---

## Cross-Platform Comparison

| Amiga Concept | Modern Equivalent | Notes |
|---|---|---|
| Enforcer (MMU trap) | AddressSanitizer (ASan) | Same concept: trap illegal accesses, report PC + registers |
| MungWall (heap guards) | `mallocscribble` / `MALLOC_CHECK_` | Same: canary values before/after each allocation |
| MungWall use-after-free | ASan quarantine / `MALLOC_PERTURB_` | Same: poison freed memory, trap on re-read |
| Combined Enforcer + MungWall | `-fsanitize=address` (GCC/Clang) | ASan combines both approaches in one tool |
| Serial port output | `ASAN_OPTIONS=log_path=asan.log` | Same: output goes to a separate channel to survive crashes |

---

## FAQ

### Does Enforcer work on 68000 (A500/A600/A2000)?

Enforcer can work in "software mode" on 68000 by patching the bus error exception vector and using `trap #N` for software breakpoints. However, it cannot detect arbitrary illegal memory accesses without MMU hardware — the 68000 has no page tables to mark addresses as inaccessible. Use MungWall alone on 68000 systems.

### Why does Enforcer hit on perfectly valid code?

False positives are rare but possible: (1) self-modifying code that writes to code segments, (2) ROM shadowing — writing to what appears to be ROM but is actually a RAM mirror, (3) memory-mapped I/O regions that Enforcer doesn't know about (custom expansion hardware).

---

## References
```

---

## References

- Enforcer: Michael Sinz — available on Aminet (`util/misc/Enforcer.lha`)
- MungWall: original CBM debug tool, available on Aminet
- `dynamic/serial_debug.md` — serial output setup
- *Amiga ROM Kernel Reference Manual: Libraries* — exec memory management
