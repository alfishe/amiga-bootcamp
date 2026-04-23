[← Home](../README.md) · [Toolchain](README.md)

# Compiler Pragmas and Inline Stubs

## Overview

AmigaOS library calls use **register-based** calling conventions (arguments in D0–D7/A0–A6). C compilers need pragmas or inline stubs to generate the correct register assignments instead of stack-based calls.

---

## Three Mechanisms

| Method | Compiler | How it works |
|---|---|---|
| **Pragmas** | SAS/C | `#pragma libcall` directive |
| **Inline headers** | GCC | Inline asm functions in `<inline/lib.h>` |
| **Proto headers** | All | `<proto/lib.h>` — auto-selects pragma or inline |

---

## Pragma Example (SAS/C)

```c
#pragma libcall DOSBase Open 1e 2102
/* Translates to: LVO = -0x1E = -30
   Args: D1 = arg1 (name), D2 = arg2 (mode)
   Result: D0 */
```

---

## Inline Example (GCC)

```c
/* inline/exec.h */
static __inline APTR
AllocMem(ULONG byteSize, ULONG requirements)
{
    register APTR _res __asm("d0");
    register ULONG _byteSize __asm("d0") = byteSize;
    register ULONG _requirements __asm("d1") = requirements;
    register struct ExecBase *_SysBase __asm("a6") = SysBase;
    __asm volatile (
        "jsr -198(%%a6)"
        : "=r"(_res)
        : "r"(_byteSize), "r"(_requirements), "r"(_SysBase)
        : "d1","a0","a1","cc","memory"
    );
    return _res;
}
```

---

## Generating Pragmas/Inlines from FD Files

```bash
# fd2pragma (Aminet: dev/misc/fd2pragma.lha):
fd2pragma exec_lib.fd exec_lib.sfd TO pragmas/exec_pragmas.h SPECIAL 6
fd2pragma exec_lib.fd exec_lib.sfd TO inline/exec.h SPECIAL 70
```

---

## Proto Headers

```c
/* proto/exec.h — portable wrapper: */
#ifdef __SASC
#include <pragmas/exec_pragmas.h>
#elif defined(__GNUC__)
#include <inline/exec.h>
#endif

extern struct ExecBase *SysBase;
```

---

## References

- NDK39: `pragmas/`, `inline/`, `proto/` directories
- [fd_files.md](fd_files.md) — FD file format
