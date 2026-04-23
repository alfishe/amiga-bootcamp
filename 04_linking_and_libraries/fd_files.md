[← Home](../README.md) · [Linking & Libraries](README.md)

# Function Definition (.fd) Files

## Overview

**Function Definition files** (`.fd`) are the authoritative source of truth for AmigaOS library ABIs. They define:
- The **name** of every library function
- The **LVO** (Library Vector Offset) — the negative offset used to call it
- The **register parameters** — which M68k registers carry each argument
- The **bias** (starting offset, always negative)

Every AmigaOS library call ultimately traces back to an `.fd` file.

---

## File Location

In the NDK39:
```
NDK39/fd/
    dos_lib.fd
    exec_lib.fd
    graphics_lib.fd
    intuition_lib.fd
    icon_lib.fd
    ...
```

Also part of the AmigaOS developer CD (adjust to your NDK path):
```
NDK39/fd/
```

---

## .fd File Format

```
##base _DOSBase         ; library base variable name
##bias 30               ; first LVO = -30 (4 mandatory: -6,-12,-18,-24)

##public
Open(name,accessMode)(D1,D2)      ; LVO -30
Close(file)(D1)                   ; LVO -36
Read(file,buffer,length)(D1,D2,D3); LVO -42
Write(file,buffer,length)(D1,D2,D3); LVO -48
...

##private
_InternalOpen(...)                 ; private function, not in public ABI
```

### Grammar Rules

| Directive | Meaning |
|---|---|
| `##base _LibBase` | Name of the library base global variable |
| `##bias N` | Starting LVO magnitude; first public function is at `-N` |
| `##public` | Following functions are part of the public ABI |
| `##private` | Following functions are internal/private |
| `FuncName(args)(regs)` | Function with argument names and register assignments |

The LVO of function `n` (0-indexed from first public) is:
```
LVO = -(bias + n × 6)
```

---

## Register Notation

Register assignments are listed in order matching the argument list, using Amiga register names:

```
Open(name, accessMode)(D1, D2)
```

Means:
- `name` → D1
- `accessMode` → D2
- Caller must put library base in A6 (by convention)

Special register names:
- `A6` — always the library base (implicit, not listed)
- `A0`–`A3`, `D0`–`D7` — data and address registers
- `D0` — return value (by convention)

---

## LVO Calculation Example

For `dos_lib.fd` with `##bias 30`:

| LVO | Function |
|---|---|
| -6 | `Open` (mandatory) |
| -12 | `Close` (mandatory) |
| -18 | `Expunge` (mandatory) |
| -24 | `Reserved` (mandatory) |
| -30 | first public function |
| -36 | second public function |
| ... | |
| -144 | `SetComment` |
| -150 | `SetProtection` |

The actual LVOs match `dos/dos.h` defines:
```c
#define DOS_Open       (-30)
#define DOS_Close      (-36)
#define DOS_Read       (-42)
```

---

## Proto Includes (Generated from .fd)

The `proto/` directory contains compiler-specific call wrappers generated from `.fd` files:

```c
/* proto/dos.h — generated automatically from dos_lib.fd */
#ifndef PROTO_DOS_H
#include <clib/dos_protos.h>   /* function prototypes */
#include <inline/dos.h>         /* inline register call stubs */
#endif
```

`inline/dos.h` contains:
```c
#define Open(name,accessMode) \
    ({ ULONG _r; \
       __asm volatile("movea.l %1,a6; jsr -30(a6)" : "=r"(_r) : "r"(_DOSBase) : "a6"); \
       _r; })
```

---

## .fd Files and Reverse Engineering

When reversing an Amiga binary, `.fd` files give you the **complete function name and parameter register map** for every library call. If you see:

```asm
MOVEA.L $00BEEF04, A6   ; graphics.library base
JSR     -$114(A6)       ; LVO -276
```

Look up `-276` in `graphics_lib.fd`:
```
-276 ÷ 6 = 46th function from start of table
```

Or directly look at `graphics/graphics.h` or `proto/graphics.h` for the constant:
```c
#define GFX_BltBitMap   (-276)
/* → JSR -276(A6) = BltBitMap() */
```

---

## Full LVO Table Reconstruction

See [lvo_table.md](lvo_table.md) for the complete process of reconstructing a library's JMP table from scratch during reverse engineering.

---

## References

- NDK39: `fd/` directory — all `.fd` files
- NDK39: `proto/` directory — generated call wrappers
- NDK39: `clib/` directory — raw C prototypes
- ADCD 2.1: library chapters reference LVOs
- Community: `https://wiki.amigaos.net/wiki/Fd_Files`
