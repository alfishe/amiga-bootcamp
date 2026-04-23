[← Home](../README.md) · [Exec Kernel](README.md)

# Semaphores — SignalSemaphore, ObtainSemaphore, Shared/Exclusive

## Overview

Semaphores are the AmigaOS mechanism for **mutual exclusion and shared-read access** to resources. Unlike `Forbid()` (which blocks all scheduling), semaphores allow other tasks to run while waiting — the waiting task simply sleeps until the resource is available.

---

## struct SignalSemaphore

```c
/* exec/semaphores.h — NDK39 */
struct SignalSemaphore {
    struct Node  ss_Link;       /* ln_Type = NT_SIGNALSEM */
                                /* ln_Name = semaphore name (public) */
    WORD         ss_NestCount;  /* how many times THIS task has obtained it */
    struct MinList ss_WaitQueue;/* tasks waiting for exclusive access */
    struct SemaphoreRequest ss_MultipleLink; /* shared-reader slot */
    struct Task *ss_Owner;      /* task holding exclusive lock (or NULL) */
    WORD         ss_QueueCount; /* number of waiters */
};
```

---

## Initialising a Semaphore

```c
/* Stack or AllocMem — always initialise before use: */
struct SignalSemaphore sem;
InitSemaphore(&sem);   /* LVO -558 */

/* Public (named) semaphore — so other tasks can find it: */
sem.ss_Link.ln_Name = "myapp.lock";
AddSemaphore(&sem);    /* LVO -564 */

/* Later: */
RemSemaphore(&sem);    /* LVO -570 */
```

---

## Exclusive (Write) Lock

```c
/* Block until this task holds the semaphore exclusively: */
ObtainSemaphore(&sem);    /* LVO -534 */

/* --- critical section: only one task in here at a time --- */

ReleaseSemaphore(&sem);   /* LVO -546 */
```

### Non-Blocking Try

```c
/* Returns TRUE if obtained, FALSE if someone else holds it: */
if (AttemptSemaphore(&sem)) {   /* LVO -540 */
    /* got it */
    ReleaseSemaphore(&sem);
} else {
    /* resource busy — do something else */
}
```

---

## Shared (Read) Lock

Multiple tasks may hold a shared lock simultaneously. An exclusive lock blocks until all shared holders release.

```c
ObtainSemaphoreShared(&sem);   /* LVO -768 */

/* --- read-only access: multiple tasks may be here at once --- */

ReleaseSemaphore(&sem);        /* same release for both modes */
```

---

## Nesting

Semaphores are **reentrant** — the same task can call `ObtainSemaphore` multiple times. The `ss_NestCount` tracks how many times the current owner has obtained it. `ReleaseSemaphore` must be called the same number of times.

```c
ObtainSemaphore(&sem);   /* NestCount = 1 */
ObtainSemaphore(&sem);   /* NestCount = 2 — safe, same task */
ReleaseSemaphore(&sem);  /* NestCount = 1 */
ReleaseSemaphore(&sem);  /* NestCount = 0 — fully released, waiters wake */
```

---

## Semaphore vs Forbid/Disable

| Mechanism | Blocks | Other tasks run while waiting? | Interrupt safe? |
|---|---|---|---|
| `Forbid()` | All task switching | ❌ No | ✅ (interrupts still run) |
| `Disable()` | All task switching + interrupts | ❌ No | ✅ |
| `ObtainSemaphore()` | Only contending tasks | ✅ Yes | ❌ Not from interrupt context |

Use semaphores for anything that may take more than a few microseconds. Use `Forbid()` only for very short list manipulations.

---

## References

- NDK39: `exec/semaphores.h`
- ADCD 2.1: `InitSemaphore`, `ObtainSemaphore`, `ObtainSemaphoreShared`, `ReleaseSemaphore`, `AttemptSemaphore`
- *Amiga ROM Kernel Reference Manual: Exec* — semaphores chapter
