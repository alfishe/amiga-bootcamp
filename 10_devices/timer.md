[← Home](../README.md) · [Devices](README.md)

# timer.device — Timing and Delays

## Overview

`timer.device` provides precise timing services: delays, time-of-day, and high-resolution timestamps. It has two units:

| Unit | Constant | Resolution | Use |
|---|---|---|---|
| 0 | `UNIT_MICROHZ` | ~2µs (E-clock) | Short, precise delays |
| 1 | `UNIT_VBLANK` | ~20ms (VBlank) | Long delays, lower overhead |
| 2 | `UNIT_ECLOCK` | CIA E-clock ticks | Highest resolution timing (OS 2.0+) |
| 3 | `UNIT_WAITUNTIL` | absolute time | Wait until specific time (OS 2.0+) |
| 4 | `UNIT_WAITECLOCK` | E-clock absolute | (OS 2.0+) |

---

## struct timeval / timerequest

```c
/* devices/timer.h — NDK39 */
struct timeval {
    ULONG tv_secs;    /* seconds */
    ULONG tv_micro;   /* microseconds */
};

struct timerequest {
    struct IORequest tr_node;
    struct timeval   tr_time;
};
```

---

## Simple Delay

```c
struct timerequest *tr = (struct timerequest *)
    CreateIORequest(port, sizeof(struct timerequest));
OpenDevice("timer.device", UNIT_VBLANK, (struct IORequest *)tr, 0);

tr->tr_node.io_Command = TR_ADDREQUEST;
tr->tr_time.tv_secs  = 2;
tr->tr_time.tv_micro = 0;
DoIO((struct IORequest *)tr);   /* blocks for 2 seconds */

CloseDevice((struct IORequest *)tr);
DeleteIORequest((struct IORequest *)tr);
```

---

## Getting Current Time

```c
tr->tr_node.io_Command = TR_GETSYSTIME;
DoIO((struct IORequest *)tr);
Printf("Time: %lu.%06lu\n", tr->tr_time.tv_secs, tr->tr_time.tv_micro);
```

---

## High-Resolution Timing

```c
/* Read E-clock (OS 2.0+): */
struct EClockVal eclock;
ULONG freq = ReadEClock(&eclock);  /* returns ticks/second */
/* eclock.ev_hi, eclock.ev_lo = 64-bit tick count */
/* Typical freq: 709379 Hz (PAL) or 715909 Hz (NTSC) */
```

---

## References

- NDK39: `devices/timer.h`
- ADCD 2.1: timer.device autodocs
