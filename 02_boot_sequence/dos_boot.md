[← Home](../README.md) · [Boot Sequence](README.md)

# DOS Boot — Bootstrap, Mount List, Startup-Sequence

## Overview

After the Kickstart ROM initialises the kernel and resident modules, `dos.library` takes over to mount filesystems and run the user's startup scripts.

---

## Boot Sequence Flow

```
Kickstart ROM init complete
    ↓
dos.library creates initial CLI process
    ↓
BootStrap module (strap) reads boot block from boot device
    ↓
Boot block executed (OFS/FFS bootblock code)
    ↓
Mount configured devices from MountList (DEVS:DOSDrivers/)
    ↓
Execute S:Startup-Sequence
    ↓
Execute S:User-Startup
    ↓
LoadWB (start Workbench)
```

---

## Boot Block Format

The first 2 sectors (1024 bytes) of a bootable disk:

```
Offset   Size   Description
$000     4      Boot block ID: "DOS\0" (OFS), "DOS\1" (FFS), etc.
$004     4      Checksum (complement to zero)
$008     4      Root block pointer (usually 880)
$00C     ...    Boot code (up to 1012 bytes of 68000 code)
```

### Boot Block Types

| ID | Hex | Type |
|---|---|---|
| `DOS\0` | `444F5300` | OFS (Old File System) |
| `DOS\1` | `444F5301` | FFS (Fast File System) |
| `DOS\2` | `444F5302` | OFS + International |
| `DOS\3` | `444F5303` | FFS + International |
| `DOS\4` | `444F5304` | OFS + Dir Cache |
| `DOS\5` | `444F5305` | FFS + Dir Cache |
| `DOS\6` | `444F5306` | OFS + Long Filenames (OS 3.2) |
| `DOS\7` | `444F5307` | FFS + Long Filenames (OS 3.2) |

---

## Boot Priority

Devices are booted in priority order. Highest priority device boots first:

| Device | Default Priority | Description |
|---|---|---|
| DF0: | 5 | First floppy drive |
| DH0: | 0 | First hard disk partition |
| DH1: | −5 | Second partition |
| DF1: | −10 | Second floppy |

Set in mountlist: `BootPri = 0` or via HDToolBox.

---

## Startup-Sequence

Standard `S:Startup-Sequence` for OS 3.1:

```
C:SetPatch QUIET            ; apply ROM patches
C:AddBuffers DH0: 50         ; filesystem buffers
C:Version >NIL:
FailAt 21
MakeDir RAM:T RAM:Clipboards RAM:ENV RAM:ENV/Sys
Copy >NIL: ENVARC: RAM:ENV ALL NOREQ
Assign >NIL: T: RAM:T
Assign >NIL: CLIPS: RAM:Clipboards
Assign >NIL: REXX: S:
Assign >NIL: PRINTERS: DEVS:Printers
Assign >NIL: KEYMAPS: DEVS:Keymaps
Assign >NIL: LOCALE: SYS:Locale
Assign >NIL: LIBS: SYS:Classes ADD
Assign >NIL: HELP: LOCALE:Help DEFER

C:IPrefs

ConClip >NIL:
; Launch Workbench:
LoadWB
EndCLI >NIL:
```

---

## Early Startup Control (Boot Menu)

Hold **both mouse buttons** during boot to access the Early Startup Control menu:

| Option | Description |
|---|---|
| Boot With No Startup-Sequence | Skip S:Startup-Sequence |
| Boot Standard | Normal boot |
| Boot With: [device list] | Select boot device |
| Display Mode: [NTSC/PAL] | Override display standard |

---

## References

- RKRM: Boot chapter
- NDK39: `dos/dosextens.h` — BootStrap
