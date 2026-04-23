[← Home](../../README.md) · [Reverse Engineering](../README.md)

# SetFunction — Hooking Library Vectors at Runtime

## Overview

`SetFunction()` is the official AmigaOS mechanism for **patching a library's JMP table** at runtime. It installs a custom function at a given LVO, replacing the original, and returns the old function pointer so a trampoline can be constructed.

---

## `SetFunction()` API

```c
/* exec/execbase.h */
APTR SetFunction(struct Library *library, LONG funcOffset, APTR newFunction);
/* Returns: pointer to OLD function */
```

- `library` — target library base (e.g., `DOSBase`)
- `funcOffset` — negative LVO offset (e.g., `-30` for `dos.library Open`)
- `newFunction` — your replacement function

---

## Installing a Hook

```asm
; Example: hook dos.library Write() at LVO -48

    MOVEA.L  _SysBase, A6
    JSR      (-120,A6)          ; Forbid() — prevent preemption during patch

    MOVEA.L  _DOSBase, A1
    MOVE.L   #-48, A0           ; LVO for Write
    LEA      _my_write(PC), A2
    JSR      (-420,A6)          ; SetFunction(DOSBase, -48, &my_write)
    MOVE.L   D0, _orig_write    ; save original function pointer

    JSR      (-126,A6)          ; Permit()
```

### C equivalent:

```c
static APTR orig_write;

void install_hook(void) {
    Forbid();
    orig_write = SetFunction((struct Library *)DOSBase, -48,
                             (APTR)my_write_hook);
    Permit();
}
```

---

## Writing a Trampoline

The hook function must:
1. Perform its instrumentation
2. Call the original via the saved pointer
3. Return with the original return value in D0

```asm
_my_write:
    ; D1 = file handle, D2 = buffer, D3 = length (Write args)
    MOVEM.L  D0-D7/A0-A6, -(SP)   ; save all (we may corrupt anything)

    ; ... instrumentation: log args, patch buffer, etc. ...

    MOVEM.L  (SP)+, D0-D7/A0-A6
    MOVEA.L  _orig_write, A0
    JMP      (A0)                  ; jump to original — not JSR; let original RTS
```

In C (with `__asm` constraints):
```c
LONG __asm my_write_hook(register __d1 BPTR fh,
                          register __d2 APTR buf,
                          register __d3 LONG len) {
    /* instrumentation */
    return ((LONG (*)(BPTR,APTR,LONG))orig_write)(fh, buf, len);
}
```

---

## Restoring on Exit

**Critical:** Always restore the original function before the program exits. Failure leaves a dangling pointer in the library JMP table, causing crashes for any subsequent users of the library.

```c
void remove_hook(void) {
    Forbid();
    SetFunction((struct Library *)DOSBase, -48, orig_write);
    Permit();
}

/* Register with atexit: */
atexit(remove_hook);
```

---

## Thread Safety Considerations

- `Forbid()` / `Permit()` disable task switching — keep the window minimal
- If the hook itself calls OS functions, use `Disable()` / `Enable()` instead only when interrupts must be excluded
- Hooks are system-global — all tasks using the library will go through your hook

---

## Common Use Cases in RE

| Use | Hook | LVO |
|---|---|---|
| Trace file access | `dos.library Open` | −30 |
| Intercept writes | `dos.library Write` | −48 |
| Monitor memory allocation | `exec.library AllocMem` | −198 |
| Log task creation | `exec.library AddTask` | −282 |
| Spy on library opens | `exec.library OpenLibrary` | −552 |

---

## References

- NDK39: `exec/execbase.h`
- ADCD 2.1: `SetFunction` autodoc
- `05_reversing/dynamic/live_memory_probing.md` — SysBase structure access
- *Amiga ROM Kernel Reference Manual: Libraries* — SetFunction chapter
