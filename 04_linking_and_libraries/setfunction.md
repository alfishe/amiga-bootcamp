[← Home](../README.md) · [Linking & Libraries](README.md)

# SetFunction — Runtime Library Patching

## Overview

`exec.library SetFunction()` replaces a single function in a library's JMP table with a different function pointer. It is the standard AmigaOS mechanism for hooking, patching, and replacing library functions at runtime.

```c
/* exec/exec.h */
APTR SetFunction(
    struct Library *library,   /* A1: library to patch */
    LONG           funcOffset, /* A0: LVO (e.g., -30) — must be negative */
    ULONG         (*newFunc)() /* D0: new function address */
);
/* Returns: D0 = old function address (to call through in the replacement) */
```

---

## How SetFunction Works

SetFunction modifies the JMP table in the library's negative-offset area:

```
Before:
  lib_base - 30:   4E F9 00 01 23 45   JMP $00012345   (original function)

After SetFunction(lib, -30, MyNewFunc):
  lib_base - 30:   4E F9 00 FF 00 10   JMP $00FF0010   (replacement)
```

It also:
1. Sets `lib_Flags |= LIBF_CHANGED` — signals that the library was patched
2. Invalidates `lib_Sum` — checksum no longer matches
3. Returns the **old** function address so the replacement can chain to the original

---

## Canonical Patching Pattern

```c
/* Store the old function pointer for chaining */
static APTR OldOpen = NULL;

/* Replacement function — must match the library's calling convention */
BPTR __saveds MyOpen(struct DosLibrary *base __asm("a6"),
                     BSTR name __asm("d1"),
                     LONG accessMode __asm("d2"))
{
    /* Pre-processing */
    kprintf("Open called: %s mode %ld\n", BADDR(name), accessMode);

    /* Chain to original */
    return ((BPTR(*)(struct DosLibrary *, BSTR, LONG))OldOpen)(base, name, accessMode);
}

/* Installation */
void install_patch(void)
{
    Forbid();   /* atomic with respect to task switching */
    OldOpen = (APTR)SetFunction((struct Library *)DOSBase,
                                 -30,               /* Open LVO */
                                 (ULONG(*)())MyOpen);
    Permit();
}
```

> [!WARNING]
> `Forbid()` / `Permit()` must surround the `SetFunction` call to prevent race conditions where another task calls the function between the time you read the old pointer and the time the new pointer is installed.

---

## Calling the Original (Chaining)

The replacement function **must** call the original to maintain correct library behavior. The old function address returned by `SetFunction` is a raw pointer to the original function body (not the JMP slot):

```c
/* Jump to original using register convention */
static APTR OldAllocMem;

APTR __saveds MyAllocMem(ULONG size __asm("d0"), ULONG flags __asm("d1"),
                          struct ExecBase *base __asm("a6"))
{
    APTR result = ((APTR(*)(ULONG, ULONG, struct ExecBase *))OldAllocMem)(size, flags, base);
    
    if (result == NULL && (flags & MEMF_CHIP)) {
        kprintf("Chip RAM alloc failed: %lu bytes\n", size);
    }
    return result;
}
```

---

## Removing a Patch

To remove a patch cleanly, restore the original:

```c
void remove_patch(void)
{
    Forbid();
    SetFunction((struct Library *)DOSBase, -30, (ULONG(*)())OldOpen);
    Permit();
}
```

This **must** be done before unloading the library that contains the replacement function — otherwise the JMP table points to freed memory.

---

## SetFunction in Reverse Engineering Context

`SetFunction` creates trampoline patterns recognisable in disassembly:

**JMP table after patching:**
```asm
; Library JMP slot (lib_base - 30):
JMP.L   $00FF1234        ; replacement function (different segment)
```

**Replacement function preamble:**
```asm
00FF1234:
    MOVEM.L D0-D7/A0-A6, -(SP)   ; save all regs (wrapper)
    ; ... logging/modification ...
    MOVEM.L (SP)+, D0-D7/A0-A6
    JMP.L   OldOpen              ; chain to original
```

**Detection heuristics:**
- JMP slot points outside the library's code segment
- `lib_Flags & LIBF_CHANGED` is set
- The `lib_Sum` no longer matches a fresh calculation
- The pointed-to function immediately chains to another address

---

## SetFunction vs Manual Patching

Some protections directly write to the JMP table without using `SetFunction`:

```asm
; Direct JMP table write (bypasses SetFunction protocol):
MOVE.L  #MyFunc, -30+2(A0)   ; overwrite address part of JMP instruction
```

This does not set `LIBF_CHANGED` and is harder to detect. Look for direct writes to `LIB_BASE - N + 2` (the address word of a JMP.L instruction).

---

## References

- NDK39: `exec/execbase.h`, `exec/libraries.h`
- ADCD 2.1 Autodocs: exec — `SetFunction`
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node01A8.html
- *Amiga ROM Kernel Reference Manual: Libraries* — library patching chapter
