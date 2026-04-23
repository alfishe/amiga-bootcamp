[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Live Memory Probing

## Overview

Live memory probing on a running Amiga means directly reading exec structures — `SysBase`, `LibList`, `TaskReady`, `MemList` — to observe system state without a traditional debugger.

---

## SysBase: The Root of Everything

`SysBase` is always at absolute address `$4` (a pointer to the `ExecBase` structure):

```c
struct ExecBase *SysBase = *((struct ExecBase **)4);
printf("exec version: %d.%d\n",
       SysBase->LibNode.lib_Version,
       SysBase->LibNode.lib_Revision);
```

In assembly:
```asm
MOVEA.L  4.W, A6              ; A6 = SysBase (exec.library base)
MOVE.W   ($16,A6), D0         ; lib_Version
MOVE.W   ($18,A6), D1         ; lib_Revision
```

---

## Walking the Library List

```c
struct Node *n = SysBase->LibList.lh_Head;
while (n->ln_Succ != NULL) {
    struct Library *lib = (struct Library *)n;
    printf("%-30s v%d.%d  opens=%d\n",
           lib->lib_Node.ln_Name,
           lib->lib_Version, lib->lib_Revision,
           lib->lib_OpenCnt);
    n = n->ln_Succ;
}
```

This enumerates all currently loaded libraries. Useful for:
- Finding if a target library is loaded
- Reading `lib_OpenCnt` to detect if your hook is installed
- Checking `lib_Flags & LIBF_DELEXP` (expunge pending)

---

## Reading `lib_OpenCnt` Live

```c
/* Check if bsdsocket.library is loaded and its open count */
struct Library *base = FindName(&SysBase->LibList, "bsdsocket.library");
if (base) {
    printf("bsdsocket: OpenCnt=%d, Version=%d\n",
           base->lib_OpenCnt, base->lib_Version);
}
```

`FindName` scans `ln_Name` in a linked list — it is an exec function at LVO −276.

---

## Memory Region Map

`SysBase->MemList` lists all memory regions:

```c
struct MemHeader *mh = (struct MemHeader *)SysBase->MemList.lh_Head;
while (mh->mh_Node.ln_Succ) {
    printf("Region: %s  %08lx–%08lx  free=%ld\n",
           mh->mh_Node.ln_Name,
           (ULONG)mh->mh_Lower,
           (ULONG)mh->mh_Upper,
           mh->mh_Free);
    mh = (struct MemHeader *)mh->mh_Node.ln_Succ;
}
```

Output example:
```
Region: chip memory   $000000–$1FFFFF  free=524288
Region: fast memory   $200000–$9FFFFF  free=6291456
```

---

## Task List Inspection

```c
/* Running tasks: */
Forbid();
struct Task *t = (struct Task *)SysBase->TaskReady.lh_Head;
while (t->tc_Node.ln_Succ) {
    printf("Task: %-20s pri=%d state=%d\n",
           t->tc_Node.ln_Name,
           t->tc_Node.ln_Pri,
           t->tc_State);
    t = (struct Task *)t->tc_Node.ln_Succ;
}
Permit();
```

`Forbid()` / `Permit()` are mandatory — the task list must not change while walking it.

---

## Patching Memory Live (Surgical Writes)

For RE/patching: direct longword write to an OS structure:

```c
/* Example: force a library's version to 99 */
Forbid();
target_lib->lib_Version = 99;
Permit();
```

> [!CAUTION]
> Direct memory writes to OS structures bypass all synchronization. Always use `Forbid()` at minimum; use `Disable()` if modifying interrupt-visible data.

---

## References

- NDK39: `exec/execbase.h`, `exec/memory.h`, `exec/tasks.h`
- `06_exec_os/exec_base.md` — full ExecBase offset table
- `06_exec_os/memory_management.md` — MemHeader structure
- `05_reversing/dynamic/setfunction_patching.md` — Forbid/Permit patterns
