[← Home](../README.md) · [Devices](README.md)

# input.device — Event Stream Merging

## Overview

`input.device` merges events from keyboard, mouse, gameport, and timer into a single input stream that feeds Intuition. Input handlers can be installed at various priorities to filter, modify, or consume events.

---

## Handler Priority Levels

| Priority | Consumer |
|---|---|
| 100 | System reserved |
| 51+ | Custom high-priority handlers |
| 50 | Intuition |
| 20 | Console.device |
| 0 | Default |

---

## Commands

| Code | Constant | Description |
|---|---|---|
| 9 | `IND_ADDHANDLER` | Add input handler |
| 10 | `IND_REMHANDLER` | Remove input handler |
| 11 | `IND_WRITEEVENT` | Inject an InputEvent into the stream |
| 12 | `IND_SETTHRESH` | Set double-click threshold |
| 13 | `IND_SETPERIOD` | Set key repeat period |
| 14 | `IND_SETMPORT` | Set mouse port type |
| 15 | `IND_SETMTRIG` | Set mouse trigger |
| 16 | `IND_SETMTYPE` | Set mouse type |

---

## References

- NDK39: `devices/input.h`
- [input_events.md](../09_intuition/input_events.md) — handler installation example
