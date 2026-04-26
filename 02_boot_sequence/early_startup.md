[← Home](../README.md) · [Boot Sequence](README.md)

# Early Startup Control — Boot Menu, Display Mode, Recovery

## Overview

The **Early Startup Control** (ESC) menu is a built-in boot manager available on all Amigas with Kickstart 2.0+. It provides boot device selection, display mode override, and emergency recovery options. It appears when both mouse buttons are held during the early boot phase — before the OS loads from disk.

---

## Activation

### How to Trigger

Hold **both mouse buttons** (left + right) immediately after power-on or during the Ctrl-Amiga-Amiga reset sequence. The timing window is:

| Kickstart | When to Hold | Visual Cue |
|---|---|---|
| 2.0–3.0 | During boot color sequence | Before "Insert Disk" or disk activity |
| 3.1 | During the hand/checkmark animation | While the Amiga hand appears |
| 3.1.4 / 3.2 | Same as 3.1 | Same timing window |

> **Tip**: Hold both buttons before powering on — this guarantees you catch the window. Release them once the menu appears.

### Not Available On

- Kickstart 1.2 / 1.3 (no boot menu feature)
- Any system where the ROM is corrupted (red screen before menu)
- Systems with custom boot ROMs that bypass standard init

---

## Menu Layout

### OS 3.1 Early Startup Control

```
╔══════════════════════════════════════════╗
║        EARLY STARTUP CONTROL             ║
║                                          ║
║  Boot Options:                           ║
║    ○ Boot With No Startup-Sequence       ║
║    ● Boot Standard                       ║
║                                          ║
║  Boot Device:                            ║
║    ● DF0:   (pri  5)                     ║
║    ○ DH0:   (pri  0)                     ║
║    ○ DH1:   (pri -5)                     ║
║                                          ║
║  Display Mode:                           ║
║    ● PAL          ○ NTSC                 ║
║                                          ║
║              [ BOOT ]                    ║
╚══════════════════════════════════════════╝
```

### OS 3.2 Early Startup Control

OS 3.2 adds additional options:

```
╔══════════════════════════════════════════╗
║        EARLY STARTUP CONTROL             ║
║                                          ║
║  Boot Options:                           ║
║    ○ Boot With No Startup-Sequence       ║
║    ● Boot Standard                       ║
║    ○ Boot (Debug)                        ║
║                                          ║
║  Boot Device:                            ║
║    ● DF0:   (pri  5)                     ║
║    ○ DH0:   (pri  0)   "System3.1"      ║
║    ○ DH1:   (pri -5)   "Work"           ║
║    ○ CD0:   (pri -20)                    ║
║                                          ║
║  Display Mode:                           ║
║    ○ PAL    ○ NTSC    ● Best Available   ║
║                                          ║
║  ROM Modules:                            ║
║    [x] Enable SetPatch                   ║
║    [x] Enable 68040.library              ║
║                                          ║
║              [ BOOT ]                    ║
╚══════════════════════════════════════════╝
```

---

## Menu Options

### Boot Options

| Option | Effect |
|---|---|
| **Boot Standard** | Normal boot — executes S:Startup-Sequence |
| **Boot With No Startup-Sequence** | Boots to a CLI prompt. S:Startup-Sequence is NOT executed. Assigns (SYS:, C:, etc.) are still set. |
| **Boot (Debug)** | (OS 3.2) Boots with debugging enabled — serial debug output, extended logging |

### Boot Device Selection

Lists all devices registered with `AddBootNode()`:

- Floppy drives: DF0:, DF1: (always present if trackdisk.device loaded)
- Hard disk partitions: DH0:, DH1:, etc. (from RDB on SCSI/IDE)
- CD-ROM: CD0: (if device driver available)
- Network: (if SANA-II device registered as bootable)

Select a device and click BOOT — the system uses that device as `SYS:` regardless of configured boot priority.

### Display Mode

| Option | Effect |
|---|---|
| **PAL** | Force PAL display (50 Hz, 283 visible lines) |
| **NTSC** | Force NTSC display (60 Hz, 241 visible lines) |
| **Best Available** | (OS 3.2) Auto-detect from hardware and monitor |

> **Why this matters**: If someone changes the display mode to a setting their monitor can't sync to (e.g., PAL on an NTSC-only monitor), the screen goes blank. The ESC menu renders using the most basic display mode, so it's always visible — even when the configured mode is incompatible.

---

## How It Works Internally

### Detection

```c
/* During boot, before strap runs: */
/* intuition.library checks both mouse buttons via CIA-A/B port registers */

UBYTE ciaA_pra = ciaa.ciapra;   /* CIA-A Port A — mouse button 1 (bit 6) */
UBYTE potgor   = custom.potgor;  /* POT port — mouse button 2 (bit 10) */

BOOL leftButton  = !(ciaA_pra & 0x40);    /* Active low */
BOOL rightButton = !(potgor & 0x0400);     /* Active low */

if (leftButton && rightButton)
{
    /* Both buttons held — enter Early Startup Control */
    ShowBootMenu();
}
```

### Display

The ESC menu uses the lowest-level graphics possible:

- Opens a 640×200 (or 640×256 PAL) 2-color screen
- Uses the Topaz 8 ROM font (always available — no disk access needed)
- Renders using direct `RastPort` calls — no windows, no layers
- Mouse pointer uses hardware sprite 0

### Boot Menu Rendering Order

1. `graphics.library` init completes → display hardware ready
2. `intuition.library` init completes → input handling ready
3. Check mouse buttons
4. If held: create the boot menu screen
5. Wait for user selection + BOOT button
6. Close screen, continue boot with selected options

---

## Recovery Scenarios

### Corrupted Startup-Sequence

```
Problem: System hangs during boot — bad script
Fix:
  1. Hold both mouse buttons → ESC menu
  2. Select "Boot With No Startup-Sequence"
  3. Boot → CLI prompt appears
  4. Edit the script: ED S:Startup-Sequence
  5. Reboot normally
```

### Wrong Display Mode (No Picture)

```
Problem: Changed to PAL on NTSC monitor (or vice versa) — screen blank
Fix:
  1. Power off
  2. Hold both mouse buttons, power on
  3. ESC menu appears (uses safe display mode)
  4. Select correct display mode (PAL/NTSC)
  5. Click BOOT
```

### Boot from Floppy Instead of Hard Disk

```
Problem: Hard disk is corrupted, need to boot from floppy
Fix:
  1. Insert bootable Workbench floppy in DF0:
  2. Hold both mouse buttons during boot
  3. Select DF0: as boot device
  4. Click BOOT
  5. System boots from floppy — hard disk accessible as DH0:
```

### Assign Loops / Infinite Requester

```
Problem: Startup-Sequence has an Assign to a missing volume
         → "Please insert volume X" in infinite loop
Fix:
  1. ESC menu → "Boot With No Startup-Sequence"
  2. Fix the Assign in S:Startup-Sequence
  3. Or: Add NOREQ flag to the problematic Assign
     Assign >NIL: WORK: DH1:
```

### Hard Disk Not Appearing in Boot Menu

```
Problem: DH0: doesn't show in the ESC boot device list
Possible causes:
  1. IDE/SCSI device not detected — check cables
  2. No valid RDB (Rigid Disk Block) — use HDToolBox
  3. Boot priority not set — use HDToolBox to set BootPri
  4. Partition table corrupt — try mounting from floppy boot
```

### Testing Multiple OS Versions

```
Scenario: Two OS versions on different partitions
  1. Install OS 3.1 on DH0: (BootPri 0)
  2. Install OS 3.2 on DH1: (BootPri -5)
  3. Normal boot → DH0: (OS 3.1)
  4. ESC menu → select DH1: → boots OS 3.2
  5. Or: change BootPri in HDToolBox to swap default
```

---

## Keyboard Alternative

On Amiga 1000 (no right mouse button connector) or when mouse is unavailable:

- Some A1000 models use a key combination instead of mouse buttons
- External button boxes connected to the joystick port can substitute
- DiagROM provides keyboard-driven boot menu alternatives

---

## References

- RKRM: Early Startup chapter
- OS 3.1 AmigaGuide: `System/BootMenu`
- OS 3.2 Release Notes: new ESC menu options
- See also: [DOS Boot](dos_boot.md) — what happens after device selection
- See also: [Cold Boot](cold_boot.md) — hardware init before ESC menu
