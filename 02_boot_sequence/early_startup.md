[← Home](../README.md) · [Boot Sequence](README.md)

# Early Startup Control — Boot Options

## Overview

The **Early Startup Control** (ESC) menu appears when both mouse buttons are held during power-on or reset. It provides boot device selection, display mode override, and emergency recovery options.

---

## Activation

- **Both mouse buttons held** before the boot screen hand animation completes
- On A1200: hold both buttons during "floppy click" phase
- Requires Kickstart 2.0+ (not available on 1.3)

---

## Menu Options (OS 3.1)

```
┌──────────────────────────────────┐
│     EARLY STARTUP CONTROL        │
│                                  │
│  Boot With No Startup-Sequence   │
│  Boot Standard                   │
│                                  │
│  Boot Device:                    │
│    DF0:  (pri 5)                 │
│    DH0:  (pri 0)                 │
│                                  │
│  Display Mode:                   │
│    ● PAL   ○ NTSC                │
│                                  │
│          [BOOT]                  │
└──────────────────────────────────┘
```

---

## Recovery Scenarios

| Scenario | Fix |
|---|---|
| Corrupted Startup-Sequence | Boot with No Startup-Sequence, then `ED S:Startup-Sequence` |
| Wrong display mode (no image) | Hold both buttons → change PAL/NTSC |
| Boot from floppy instead of HD | Select DF0: as boot device |
| Assign loops / infinite boot | No Startup-Sequence → fix assigns manually |

---

## References

- RKRM: Early Startup chapter
- OS 3.1 AmigaGuide: `System/BootMenu`
