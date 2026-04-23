[← Home](../README.md) · [Toolchain](README.md)

# Debugging Tools — BareFoot, wack, GDB Remote

## Overview

Debugging Amiga programs ranges from ROM-resident kernel debuggers (wack/SAD) through software monitors to modern cross-debugging via GDB stubs.

---

## Tool Comparison

| Tool | Type | Target | Best for |
|---|---|---|---|
| BareFoot | Serial debugger | Real hardware / UAE | OS-level, Exec kernel |
| wack/SAD | ROM debugger | Real hardware | Boot-time, crash analysis |
| MonAm | Software monitor | AmigaOS | Breakpoints, disassembly |
| IDA Pro | Static + remote | Cross-platform | Static RE, decompilation |
| GDB (m68k-elf-gdb) | Cross-debugger | FS-UAE / Basilisk | Source-level C debugging |
| Enforcer | Memory watchdog | AmigaOS (68020+) | Illegal memory access detection |
| MuForce | Memory watchdog | AmigaOS (68040+) | Same as Enforcer for 040/060 |

---

## Enforcer / MuForce

Detects invalid memory accesses using MMU:

```
Enforcer Hit!   $0000000C read by task "myapp" at $00020456
```

```
; Install:
run >NIL: Enforcer
; or for 040/060:
run >NIL: MuForce
```

---

## FS-UAE GDB Debugging

```bash
# In fs-uae.conf:
remote_debugger = 1
remote_debugger_port = 6860

# Connect from host:
m68k-elf-gdb myapp
(gdb) target remote localhost:6860
(gdb) break main
(gdb) continue
```

---

## References

- BareFoot: Aminet `dev/debug/BareFoot.lha`
- Enforcer: Aminet `dev/debug/Enforcer.lha`
- MuForce: Aminet `dev/debug/MuForce.lha`
