[← Home](../README.md) · [Overview](README.md)

# AmigaOS Version Matrix — 3.1 vs 3.2

> **Scope of this documentation:** OS 3.1 (Kickstart 40.x, Workbench 40.x) and OS 3.2 (Kickstart 47.x, Workbench 47.x).

## Kickstart Version Numbers

| OS Version | Kickstart Ver | Exec Ver | Release | Primary Platform |
|---|---|---|---|---|
| OS 3.0 | 39.106 | 39.x | 1992 | A1200/A4000 launch |
| **OS 3.1** | **40.068** | **40.x** | **1993** | **All AGA, final Commodore** |
| OS 3.5 | 45.x | 45.x | 1999 | Hyperion/H&P, WB-only |
| OS 3.9 | 45.x | 45.x | 2000 | Hyperion/H&P, WB-only |
| **OS 3.2** | **47.96+** | **47.x** | **2021** | **Hyperion, all 68k** |
| OS 3.2.2 | 47.102 | 47.x | 2022 | Hyperion |

---

## OS 3.1 Feature Summary (Kickstart 40.x)

This is the final OS release by Commodore before their 1994 bankruptcy. It ships with all production AGA machines (A1200, A4000) and upgrade ROMs for A500/A2000/A3000.

**Exec (40.x):**
- Stable SysBase layout (unchanged since 2.x in most respects)
- `PoolAllocMem` / `PoolFreeMem` — memory pools
- `NewMinList()` macro
- `GetCC()` — condition codes from last instruction

**dos.library (40.x):**
- `ReadArgs()` / `FreeArgs()` — template argument parsing
- `CreateNewProc()` — new process creation API
- `DosGetLocalVar()` / `DosSetLocalVar()` — local environment variables
- `ChangeMode()` — shared/exclusive lock upgrade
- `SameLock()` — lock identity comparison
- `ExAll()` — extended directory examination

**graphics.library (40.x):**
- `AllocBitMap()` / `FreeBitMap()` — dynamic bitmap allocation
- `GetBitMapAttr()` — bitmap attribute query
- `ObtainBestPenA()` — closest-match colour allocation
- `SetRPAttrsA()` / `GetRPAttrsA()` — RastPort attribute tags
- AGA full colour support: `LoadRGB32()`, 256 colour tables
- RTG stubs present but not functional (RTG lives in 3.5+)

**intuition.library (40.x):**
- BOOPSI completely stable
- `OpenWindowTagList()` / `OpenScreenTagList()` — tag-based open calls
- `GetScreenDrawInfo()` / `FreeScreenDrawInfo()`
- `LockPubScreen()` / `UnlockPubScreen()`
- `NewModifyProp()` — proportional gadget update

**locale.library (40.x):**
- Complete locale/catalog system
- `OpenCatalogA()` / `GetCatalogStr()`

**New in 3.1 vs 3.0:**
- `datatypes.library` — class-based data-type system
- Multiview application (uses datatypes)
- `asl.library` — enhanced requesters vs `req.library`
- PCMCIA card resource (`cardres`)

---

## OS 3.2 Delta — What Changed (Kickstart 47.x)

OS 3.2 is a Hyperion-developed modernisation of the 3.1 codebase, first released in 2021.

### Exec (47.x)
- `AllocSysObject()` / `FreeSysObject()` — unified object allocator
  - Replaces manual `AllocMem` + init for ports, tasks, IORequests, semaphores
- `NewCreateTask()` — extended task creation with tags
- `IExec->` interface style (for future AOS4 parity — not mandatory on 68k)
- Improved memory tracking and debug support

### dos.library (47.x)
- `BPTR`-free variants of many path functions
- Enhanced `ReadArgs()` template syntax
- `Examine()` extended: `ExamineTags()` returning `ExamineData` structs
- DOS path handling improvements (up to 1024-char paths)
- `AddDosEntry()` / `RemDosEntry()` refined

### graphics.library (47.x)
- Compositing system (alpha blending between screens)
- `CompositeTags()` — hardware-assisted screen composition
- Improved RTG (RastPort to VRAM) support via `cybergraphics.library` integration points
- `AllocSpriteDataA()` extended for RTG sprites
- Palette handling improvements

### intuition.library (47.x)
- New Intuition prefs (IPrefs 47.x)
- Better pen sharing and colour management
- `intuition.library` opens before `graphics.library` in new boot sequence
- Visual prefs: themes, scaled UI elements

### New Libraries in 3.2
| Library | Purpose |
|---|---|
| `disksonar.library` | Fast disk scanning |
| `application.library` | Application registration, task-bar |
| `timezone.library` | Timezone database |
| `identify.library` | Hardware identification |

### AHI Changes (3.2)
- AHI (Audio Hardware Interface) integrated as standard component
- `ahi.device` replaces direct `audio.device` use in 3.2 applications

---

## Cross-Version API Compatibility Table

| Function | 3.1 (40) | 3.2 (47) | Notes |
|---|---|---|---|
| `AllocMem` | ✓ | ✓ | Unchanged |
| `AllocSysObject` | ✗ | ✓ | New in 3.2 |
| `OpenLibrary` | ✓ | ✓ | Unchanged |
| `AllocBitMap` | ✓ | ✓ | Extended in 3.2 |
| `CompositeTags` | ✗ | ✓ | New in 3.2 |
| `ExamineTags` | ✗ | ✓ | New in 3.2 |
| `CreateNewProc` | ✓ | ✓ | Extended |
| `NewCreateTask` | ✗ | ✓ | New in 3.2 |
| `OpenCatalogA` | ✓ | ✓ | Unchanged |

---

## Version Detection in Code

```c
/* Check for OS 3.2+ at runtime */
struct Library *SysBase = *((struct Library **)4);
if (SysBase->lib_Version >= 47) {
    /* OS 3.2 features available */
}

/* Check for OS 3.1+ */
if (SysBase->lib_Version >= 40) {
    /* AllocBitMap, datatypes etc available */
}
```

---

## References

- NDK 3.9: `NDK39.lha` — headers define version-gated macros
- ADCD 2.1: `AmigaMail_Vol2_guide/` — release notes per OS version
- Hyperion OS 3.2 SDK: https://www.hyperion-entertainment.com/
- `exec/execbase.h` — `AttnFlags` bits for CPU detection
