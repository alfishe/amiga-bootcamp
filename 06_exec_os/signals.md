[← Home](../README.md) · [Exec Kernel](README.md)

# Signals — AllocSignal, SetSignal, Wait

## Overview

Signals are the lightest AmigaOS synchronization primitive. Each task has 32 signal bits (`tc_SigAlloc`). A task blocks on `Wait(mask)` until any of the specified bits are set by another task or interrupt handler calling `Signal()`.

---

## Signal Bit Constants

```c
/* exec/tasks.h — NDK39 */
/* Bits 0–15: application-allocated via AllocSignal() */
/* Bits 16–31: reserved by exec */

#define SIGB_ABORT      0    /* bit 0: break signal */
#define SIGB_CHILD      1    /* bit 1: child task signal */
#define SIGB_BLIT       4    /* bit 4: blitter done (exec internal) */
#define SIGB_SINGLE     4    /* alias */
#define SIGB_INTUITION  5    /* bit 5: Intuition events (exec internal) */
#define SIGB_DOS        8    /* bit 8: DOS signal */

/* Workbench/DOS break signals (bits 12–15): */
#define SIGBREAKB_CTRL_C  12
#define SIGBREAKB_CTRL_D  13
#define SIGBREAKB_CTRL_E  14
#define SIGBREAKB_CTRL_F  15

#define SIGBREAKF_CTRL_C  (1L<<SIGBREAKB_CTRL_C)  /* $1000 */
#define SIGBREAKF_CTRL_D  (1L<<SIGBREAKB_CTRL_D)  /* $2000 */
#define SIGBREAKF_CTRL_E  (1L<<SIGBREAKB_CTRL_E)  /* $4000 */
#define SIGBREAKF_CTRL_F  (1L<<SIGBREAKB_CTRL_F)  /* $8000 */
```

---

## Allocating and Freeing Signals

```c
/* Allocate an unused signal bit (-1 = any free bit): */
LONG sigBit = AllocSignal(-1);   /* LVO -246 */
if (sigBit < 0) { /* all 16 user bits in use */ }

ULONG sigMask = (1L << sigBit);

/* Free when done: */
FreeSignal(sigBit);   /* LVO -252 */
```

---

## Waiting for Signals

```c
/* Block until any of the listed signals arrive: */
ULONG received = Wait(sigMask | SIGBREAKF_CTRL_C);   /* LVO -318 */

if (received & SIGBREAKF_CTRL_C) {
    /* user pressed CTRL-C */
    cleanup_and_exit();
}
if (received & sigMask) {
    /* our custom event occurred */
}
```

`Wait()` returns only after at least one bit in the mask is set. It is equivalent to sleeping — the task is moved to `TaskWait` and no CPU is consumed.

---

## Sending Signals

```c
/* Signal a task from another task or interrupt handler: */
Signal(target_task, sigMask);   /* LVO -324 */
```

`Signal()` is safe from interrupt context.

---

## SetSignal — Read and Clear

```c
/* Read and clear specific signal bits atomically: */
ULONG old = SetSignal(new_bits, change_mask);   /* LVO -306 */
/* old = previous state of all 32 signal bits */
/* new value = (old & ~change_mask) | (new_bits & change_mask) */

/* Check CTRL-C without blocking: */
if (SetSignal(0, SIGBREAKF_CTRL_C) & SIGBREAKF_CTRL_C) {
    /* CTRL-C was pending — now cleared */
}
```

---

## Typical Usage Pattern: Event Loop

```c
struct MsgPort *port = CreateMsgPort();
ULONG portSig = (1L << port->mp_SigBit);
ULONG waitMask = portSig | SIGBREAKF_CTRL_C;

BOOL running = TRUE;
while (running) {
    ULONG sigs = Wait(waitMask);

    if (sigs & SIGBREAKF_CTRL_C) {
        running = FALSE;
    }
    if (sigs & portSig) {
        struct Message *msg;
        while ((msg = GetMsg(port)) != NULL) {
            /* handle message */
            ReplyMsg(msg);
        }
    }
}
DeleteMsgPort(port);
```

---

## References

- NDK39: `exec/tasks.h`, `exec/execbase.h`
- ADCD 2.1: `AllocSignal`, `FreeSignal`, `Signal`, `Wait`, `SetSignal`
- [tasks_processes.md](tasks_processes.md) — tc_SigAlloc, tc_SigRecvd fields
- *Amiga ROM Kernel Reference Manual: Exec* — signals chapter
