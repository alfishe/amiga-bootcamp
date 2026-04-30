# Amiga Knowledge Base — Gap Analysis & Improvement Proposal

> **Date:** 2026-04-25
> **Updated:** 2026-04-27 (per-article line-count tracking)
> **Scope:** All 17 sections, ~90 articles, `/doc/amiga/`

---

## Quality Assessment Methodology

Articles were scored against [AGENTS.md](../amiga/AGENTS.md) "Deep" criteria:
- Mermaid architecture / data-flow diagrams
- Named antipatterns with broken/fixed code pairs
- Pitfalls sections with bad/good code
- FAQ for commonly asked questions
- FPGA/Emulation impact section
- Use-Case Cookbook (copy-paste patterns)
- Decision Flowchart (when to use vs alternatives)
- Cross-platform comparison / Modern Analogies

---

## Tier 1 — Critical Gaps (No Article Exists) — ALL COMPLETE ✅

| # | New Article | Why Needed | Status |
|---|---|---|---|
| 1 | **Datatypes System** | The single most common AmigaOS API used by nearly every application for image/sound/text loading (ILBM, GIF, JPEG, WAV, 8SVX, etc.). `NewDTObject()` / `LoadDTObject()` / `GetDTAttrs()`. Zero coverage — major oversight. | ✅ **DONE** — `11_libraries/datatypes.md` (839 lines) |
| 2 | **AmigaGuide — Hypertext Help System** | The standard help file format for every Amiga application. AmigaGuide files (`.guide`) with embedded links, images, and `XREF` support are used universally. No article exists. | ✅ **DONE** — `11_libraries/amigaguide.md` (760 lines) |
| 3 | **commodities.library — Hotkey/I/O Hooks** | The background input-filtering system (Exchange, hotkey brokers, screen blankers, mouse gesture tools). Used by FKey, ClickToFront, MultiCX, MagicMenu. No coverage. | ✅ **DONE** — `09_intuition/commodities.md` (769 lines) |
| 4 | **translator.library — Speech Translation** | The text-to-speech phonetic translator (`translator.library` + `narrator.device`). Phoneme-based synthesis, not data format conversion. | ✅ **DONE** — `11_libraries/translator.md` (536 lines) |
| 5 | **VBCC Compiler** | vbcc is the second most popular Amiga cross-compiler after GCC bebbo. Mentioned in `register_conventions.md` and `compiler_stubs.md` but has no dedicated article unlike SAS/C and StormC. | ✅ **DONE** — `13_toolchain/vbcc.md` (703 lines) |

---

## Tier 2 — Major Upgrades (Shallow → Deep)

| # | File | Was | Now | Status |
|---|---|---|---|---|
| 6 | `00_overview/hardware_models.md` | 47 lines | 591 lines | ✅ **DONE** — Per-model deep-dive, custom chip inventory per model, memory maps, real-world context |
| 7 | `08_graphics/bitmap.md` | 118 lines | 598 lines | ✅ **DONE** — Mermaid architecture, `AllocBitMap()` lifecycle, interleaved layout, modulo alignment pitfalls, RastPort→BitMap relationship, cookbook |
| 8 | `12_networking/bsdsocket.md` | 134 lines | 1057 lines | ✅ **DONE** — Event-loop cookbook, `WaitSelect()` deep dive, non-blocking async I/O, multi-socket patterns, DNS resolution, performance tables |
| 9 | `10_devices/audio.md` | 279 | 945 | ✅ **DONE** — 5 named antipatterns, 5 pitfalls, DMA slot budget, initialization boilerplate + use-case cookbook (SFX, MOD loop, disk streaming, voice-over), decision flowchart (audio.device vs direct HW), best practices, when-NOT-to-use, 1985 cross-platform comparison, MOD file format deep-dive (structure, cultural impact, 100:1 compression), 14-bit Paula calibrated hack FAQ (Christian Buchner, AmigaAmp, mpega.library, 040/060 MP3 playback), FPGA/MiSTer impact |
| 10 | `10_devices/timer.md` | 529 | 854 | ✅ **DONE** — 8 named antipatterns with broken/fixed code pairs (Re-Arm Without Wait, Abandoned Abort, Microsecond VBlank, Naked ReadEClock, Hard-Coded Hertz, Spin Loop, Leaky Shutdown, Delay() Dependency), Use-Case Cookbook (6 patterns: blocking delay, UI timeout, game frame sync, audio refill, benchmarking, system time), decision flowchart, best practices, when-to-use/when-not-to-use, FPGA/MiSTer impact (E-clock/VBlank accuracy, non-standard refresh rates), 1985 competitive landscape (C64/MS-DOS/Atari ST/Mac vs Amiga virtualisation), modern analogies (setTimeout, requestAnimationFrame, clock_nanosleep, rdtsc), 7 FAQ items |
| 11 | `01_hardware/aga_a1200_a4000/cpu_030_040.md` | 139 | 425 | ✅ **DONE** — Commodore + third-party accelerator catalog (Blizzard, CyberStorm, WarpEngine, GVP, Apollo), quantified benchmarks (MIPS/Dhrystones/MB/s per CPU), 4 named antipatterns (Ghost Cache, Missing Library, Calibrated Loop, Speeding on Chip Bus), 3 pitfalls (CIA cache coherency, alignment, Chip RAM speed invariant), 7 best practices, when-to-use table, FPGA/MiSTer impact (TG68K vs Apollo 68080), 68K evolution timeline 1979-1994, modern analogies (non-cache-coherent DMA, x86 MTRR/PAT, ARM Cortex-A8 superscalar), FAQ |
| 12 | `08_graphics/views.md` | 109 | 445 | ✅ **DONE** — Mermaid 3-stage pipeline, ViewPort chaining (split screens), ColorMap/LoadRGB4, 3 named antipatterns (Ghost Screen, Half-Screen Haunt, Color Clash), 4 pitfalls, When-to-Use decision flowchart (Views vs Direct Copper), 7 best practices, 1985 cross-platform comparison, modern GPU analogies (command buffers, vkQueuePresentKHR) |
| 13 | `08_graphics/display_modes.md` | 217 | 646 | ✅ **DONE** — ModeID selection flowchart (Mermaid + fallback code), CRT vs flat-panel table (scandoublers, pixel aspect ratio, overscan), interlace vs progressive tradeoffs (CRT vs LCD experience, DBLPAL as flicker-free alternative), 5 named antipatterns (Hardcoded Mode, Depth Ostrich, LACE Without Thought, ModeID Bit-Whacker, FMODE Faith-Healer), 3 pitfalls (DMA starvation, overscan assumptions, PAL/NTSC assumptions), 8 best practices, when-to-use/when-NOT table, FPGA/MiSTer impact (pixel clock accuracy, FMODE bus timing, interlace field ID), 1985 competitive landscape, modern analogies (EDID, GDDR5/HBM2, Retina @2x, texture compression, CGDisplayCopyAllDisplayModes), 6 FAQ items |
| 14 | `07_dos/filesystem.md` | 304 | 1244 | ✅ **DONE** — Comprehensive capabilities matrix (max disk/file size, directory limits, nesting, floppy/HDD, crash resilience); detailed third-party filesystem deep-dive (PFS3 atomic commits, SFS journaling, FFS2 64-bit — each with named pros/cons lists); crash resilience comparison (validation vs atomic commits vs journaling with quantified validation times); **fragmentation & defragmentation deep-dive** (bitmap allocation scatter, quantified media impact table, visual fragmented vs contiguous diagrams, defrag tool catalog — ReOrg/DiskSafe/Quarterback/SFSdefrag — with 5-step ReOrg algorithm, CF/SSD no-defrag rationale, 6 best practices); **partition IDs, signatures & on-disk data layout** (two-layer identification — RDB DosType vs on-disk boot block, complete DosType reference tables with hex values for OFS/FFS/PFS3/SFS, PFS3's unique split-signature design with WARNING box, summary of what bytes you see at partition block 0 in a hex editor, ASCII box diagrams showing where each filesystem places its metadata — OFS/FFS root at midpoint, PFS3 metadata zone at beginning, SFS master directory block at block 2, quick-comparison table); full RDB partitioning deep-dive (RigidDiskBlock structure, PartitionBlock linked list, filesystem headers in RDB, partition flags, limits); Kickstart boot process (4-phase Strap enumeration, BootPri selection, filesystem loading from RDB, Early Startup Menu, 4-phase Mermaid flowchart); multi-boot/dual-boot configurations (5 scenarios); expanded When-to-Use table (filesystem selection + partition layout strategy with 7 common goals); filesystem selection decision flowchart; unified comparison matrix spanning OFS/FFS/FAT16/HFS/UFS/PFS3/SFS/FFS2; 5 named antipatterns; 4 pitfalls; 6-item fragmentation best practices; FPGA/MiSTer impact; 1985-1994 landscape + modern analogies; FAQ (12 items) |

---

## Tier 3 — Quality Boosts (Adequate → Exceptional)

| # | File | Was | Now | Status |
|---|---|---|---|---|
| 15 | `08_graphics/sprites.md` | 306 | 306 | ❌ **Pending** — Named antipatterns, pitfalls comparing hardware sprites vs SimpleSprite, FPGA sprite timing |
| 16 | `08_graphics/text_fonts.md` | 215 | 215 | ❌ **Pending** — Cookbook (bitmap vs outline fonts), pitfalls with font spacing, ColorFont memory layout |
| 17 | `09_intuition/screens.md` | 582 | 582 | ❌ **Pending** — Antipatterns, cookbook (screen flipping, borderless, PAL→NTSC handling) |
| 18 | `09_intuition/windows.md` | 370 | 370 | ❌ **Pending** — Named antipatterns ("The Borderless Too Soon"), FAQ, cookbook (custom window dragging, backdrop to screen flip) |
| 19 | `09_intuition/menus.md` | 378 | 378 | ❌ **Pending** — Menu render chain diagram, pitfalls with RemoveMenu/FreeMenu ordering, AmigaGuide help links |
| 20 | `09_intuition/gadgets.md` | 403 | 403 | ❌ **Pending** — Named antipatterns, BOOPSI command flow, GadTools→BOOPSI migration guide |
| 21 | `11_libraries/iffparse.md` | 271 | 1031 | ✅ **DONE** — Nesting & chunk hierarchy diagrams, ILBM/EHB pitfalls, PBM read patterns, cross-reference to Datatypes |
| 22 | `13_toolchain/gcc_amiga.md` | 82 | 82 | ❌ **Pending** — Extremely thin stub. Needs full build pipeline, Docker cross-compilation guide, linker scripts, amiga-gcc specifics |
| 23 | `11_libraries/layers.md` | 224 | 224 | ❌ **Pending** — Mermaid layer stacking diagram, pitfalls with layer ordering and damage regions |
| 24 | `10_devices/console.md` | 244 | 244 | ❌ **Pending** — Escape sequence table, cookbook for raw console I/O, pitfalls with buffering |
| 25 | `10_devices/trackdisk.md` | 178 | 178 | ❌ **Pending** — Sector-level format diagram, MFM encoding basics, pitfalls with trackdisk vs filesystem access |

---

## Tier 4 — Modernization & Advanced Techniques (New Articles)

| # | New Article | Why Needed | Status |
|---|---|---|---|
| 26 | **Custom Trackloaders & DRM** | 80% of classic games bypassed DOS. Reversing them requires understanding raw MFM sync words, bootblocks, and copy protection (e.g. Rob Northen Copylock). | ❌ **Pending** |
| 27 | **RTG (Retargetable Graphics)** | Modern Amigas use RTG (Picasso96/CyberGraphX) for 16/24-bit chunky graphics. Application-level rendering is undocumented in our `08_graphics` folder. | ❌ **Pending** |
| 28 | **AHI Audio Interface** | Hardware-agnostic 16-bit multi-channel audio mixing is standard for modern Amiga apps, decoupling audio from the 8-bit 4-channel Paula chip limits. | ❌ **Pending** |
| 29 | **Demoscene Techniques** | Exploits like Sprite Multiplexing and Copper Chunks defined the platform's capabilities. Crucial for understanding high-performance hardware banging. | ❌ **Pending** |
| 30 | **Modern Cross-Compilation** | Setting up `m68k-amigaos-gcc`, `vbcc`, and `vasm` via CMake on modern macOS/Linux to build native `.hunk` binaries. | ❌ **Pending** |

---

## Per-Article Status

| Status | Meaning |
|---|---|
| ✅ **Deep** | Meets AGENTS.md criteria: Mermaid, antipatterns, pitfalls, cookbook, FPGA impact, historical context, modern analogies, FAQ |
| ✅ **Adequate** | Functional reference with struct tables and API docs; lacks antipatterns / cookbooks / modern context |
| ⚠️ **Thin** | Skeleton coverage only; needs significant expansion |
| ❌ **Pending** | In Tier 3 scan — targeted for upgrade |

### 00 — Overview

| Article | Lines | Status | Notes |
|---|---|---|---|
| `hardware_models.md` | 591 | ✅ Deep | Per-model deep-dive, custom chip inventory, memory maps, real-world context |
| `history.md` | 114 | ✅ Adequate | Platform history timeline |
| `os_versions.md` | 148 | ✅ Adequate | OS version comparison table |

### 01 — Hardware

| Article | Folder | Lines | Status | Notes |
|---|---|---|---|---|
| `cpu_030_040.md` | aga | 424 | ✅ Deep | Tier 2 upgrade: accelerator catalog, benchmarks, 4 antipatterns, 68K timeline |
| `akiko_cd32.md` | aga | 386 | ✅ Deep | Akiko C2P engine, CD32 hardware architecture, CD-ROM DMA |
| `aga_copper.md` | aga | 371 | ✅ Adequate | AGA copper changes: 8-bit X position, $DFFxxx jump |
| `aga_blitter.md` | aga | 167 | ✅ Adequate | AGA 32-bit blitter: 4× throughput, FMODE register |
| `aga_palette.md` | aga | 134 | ✅ Adequate | AGA 24-bit palette: LOCT/SHCT banks |
| `chipset_aga.md` | aga | 126 | ✅ Adequate | AGA chipset architecture overview |
| `aga_display_modes.md` | aga | 122 | ✅ Adequate | AGA display modes: DBLPAL, Multiscan, HAM8 |
| `aga_registers_delta.md` | aga | 97 | ✅ Adequate | OCS→AGA register differences table |
| `memory_types.md` | common | 423 | ✅ Deep | Chip/Fast/Slow RAM, DMA constraints, $C00000 alias |
| `gayle_ide_pcmcia.md` | common | 220 | ✅ Adequate | Gayle gate array: IDE and PCMCIA controller |
| `cia_chips.md` | common | 218 | ✅ Adequate | 8520 CIA: timers, I/O ports, TOD clock |
| `address_space.md` | common | 175 | ✅ Adequate | 24-bit memory map: Chip, Fast, ROM, I/O, Zorro II |
| `m68k_cpu.md` | common | 141 | ✅ Adequate | 68000 architecture baseline: registers, exceptions |
| `zorro_bus.md` | common | 139 | ✅ Adequate | Zorro II/III expansion bus: AutoConfig, bus arbitration |
| `cdtv_hardware.md` | ocs | 283 | ✅ Adequate | CDTV-specific: CD-ROM controller, front panel, boot ROM |
| `custom_registers.md` | ocs | 183 | ✅ Adequate | OCS custom chip register map |
| `blitter.md` | ocs | 154 | ✅ Adequate | Blitter engine basics: channels, minterms, line draw |
| `sprites.md` | ocs | 136 | ✅ Adequate | Hardware sprite DMA: 8 sprites × 4 colors — **note:** separate from `08_graphics/sprites.md` (Tier 3 #15) |
| `paula_audio.md` | ocs | 135 | ✅ Adequate | Paula audio: 4-channel DMA, period/volume registers |
| `copper.md` | ocs | 128 | ✅ Adequate | Copper coprocessor basics: instruction format, WAIT/MOVE |
| `paula_serial.md` | ocs | 123 | ✅ Adequate | Paula UART and floppy disk controller |
| `chipset_ocs.md` | ocs | 107 | ✅ Adequate | OCS chipset architecture: Agnus/Denise/Paula |
| `chipset_ecs.md` | ecs | 119 | ✅ Adequate | ECS chipset changes: Super Agnus, 2 MB Chip RAM |
| `ecs_registers_delta.md` | ecs | 114 | ✅ Adequate | OCS→ECS register differences table |
| `productivity_modes.md` | ecs | 97 | ✅ Adequate | ECS productivity/VGA: 640×480×4, 31 kHz scan |
| `chip_ram_expansion.md` | ecs | 77 | ✅ Adequate | A600 trapdoor Chip RAM expansion |
| `gary_system_controller.md` | ecs | 576 | ✅ Deep | Gary & Fat Gary: address decoding, bus arbitration, interrupt controller, SCSI/SDMAC integration, AutoConfig controller, chip variants (5719/5391/5393), runtime detection (4 methods), Gary vs Gayle vs Ramsey/Budgie decision guide, 3 named antipatterns, 3 pitfalls, FPGA timing requirements, historical context (TTL→ASIC), modern Northbridge analogy |

### 02 — Boot Sequence

| Article | Lines | Status | Notes |
|---|---|---|---|
| `cold_boot.md` | 500 | ✅ Deep | Power-on to Kickstart handoff: reset vector, ROM shadow |
| `dos_boot.md` | 451 | ✅ Deep | Strap module, boot block execution, Startup-Sequence parsing |
| `kickstart_rom.md` | 446 | ✅ Deep | ROM binary structure, module inventory, extraction tools |
| `kickstart_init.md` | 406 | ✅ Deep | ExecBase creation, resident module scan, 4-phase init |
| `early_startup.md` | 253 | ✅ Deep | Early Startup Control menu, recovery scenarios |

### 03 — Executable Loader & HUNK Format

| Article | Lines | Status | Notes |
|---|---|---|---|
| `exe_crunchers.md` | 617 | ✅ Deep | PowerPacker/Imploder/Shrinkler, decrunch stubs — exemplary article |
| `hunk_format.md` | 583 | ✅ Deep | Complete HUNK binary specification, all 22 hunk type codes, debug format tags, bit masking |
| `hunk_relocation.md` | 326 | ✅ Adequate | Relocation mechanics with visual before/after diagrams |
| `overlay_system.md` | 311 | ✅ Adequate | HUNK_OVERLAY tree architecture, runtime manager |
| `exe_load_pipeline.md` | 276 | ✅ Adequate | LoadSeg → relocation → segment chain → CreateProc |
| `object_file_format.md` | 167 | ✅ Adequate | HUNK_UNIT, multi-section, linker archives |
| `hunk_ext_deep_dive.md` | 164 | ✅ Adequate | HUNK_EXT exports/imports/commons |
| `hunk_debug_info.md` | 163 | ✅ Adequate | HUNK_SYMBOL, HUNK_DEBUG, stabs format |

### 04 — Linking & Library Integration

| Article | Lines | Status | Notes |
|---|---|---|---|
| `library_structure.md` | 432 | ✅ Deep | JMP table, MakeLibrary, complete library creation walkthrough |
| `shared_libraries_runtime.md` | 430 | ✅ Deep | OpenLibrary resolution, ramlib, version negotiation |
| `register_conventions.md` | 315 | ✅ Adequate | Register ABI: integer, FPU, varargs, __saveds |
| `startup_code.md` | 209 | ✅ Adequate | Entry contract, CLI vs WB, WBStartup message |
| `inline_stubs.md` | 198 | ✅ Adequate | Inline stubs: pragma, inline asm, __reg |
| `lvo_table.md` | 194 | ✅ Adequate | JMP table layout, complete exec LVO table |
| `compiler_stubs.md` | 188 | ✅ Adequate | SAS/C, GCC, VBCC call pattern comparison |
| `fd_files.md` | 172 | ✅ Adequate | FD/SFD format, LVO calculation |
| `link_libraries.md` | 172 | ✅ Adequate | Static linking: amiga.lib, libnix, startup glue |
| `setfunction.md` | 158 | ✅ Adequate | Runtime function patching, chaining, removal |

### 05 — Reverse Engineering

| Article | Lines | Status | Notes |
|---|---|---|---|
| `patching_techniques.md` | 228 | ✅ Adequate | Surgical binary patching: hex search, ADF patching |
| `methodology.md` | 217 | ✅ Deep | Step-by-step RE workflow: static → dynamic → reconstruction |
| `ida_setup.md` | 190 | ✅ Adequate | IDA Pro config for 68k/Amiga: loaders, plugins |
| `compiler_fingerprints.md` | 183 | ✅ Adequate | Compiler identification by code patterns |
| `static/api_call_identification.md` | 532 | ✅ Deep | API call pattern recognition — complete with Mermaid, decision guide, antipatterns, cookbook |
| `static/m68k_codegen_patterns.md` | 399 | ✅ Deep | 68k code generation idiom catalog — complete with StormC/Aztec, Mermaid flowchart, cookbook |
| `static/library_jmp_table.md` | 381 | ✅ Deep | Library LVO table identification techniques — complete with third-party reconstruction, Python scripts |
| `static/struct_recovery.md` | 278 | ✅ Deep | Struct layout reconstruction from disassembly — complete with IDA Python batch annotator |
| `dynamic/live_memory_probing.md` | 263 | ✅ Deep | Runtime memory inspection techniques — complete with Mermaid, safe probing rules, cookbook |
| `dynamic/setfunction_patching.md` | 323 | ✅ Deep | Dynamic SetFunction interception — complete with before/after Mermaid, trampoline patterns, cookbook |
| `case_studies/ramdrive_device.md` | 129 | ✅ Deep | Real-world RE walkthrough: RAMDrive reverse engineering |
| `static/hunk_reconstruction.md` | 247 | ✅ Deep | HUNK binary reconstruction from memory — complete with antipatterns, Python extraction scripts |
| `static/string_xref_analysis.md` | 258 | ✅ Deep | String cross-reference analysis — complete with Mermaid, library mapping cookbook, Pascal string handling |
| `dynamic/serial_debug.md` | 178 | ✅ Deep | Serial debug output techniques — complete with Mermaid, baud rate pitfalls, host-side capture |
| `dynamic/enforcer_mungwall.md` | 215 | ✅ Deep | Enforcer/MungWall runtime error detection — complete with decision guide, antipatterns, cross-platform comparison |
| `static/asm68k_binaries.md` | 924 | ⚠️ Adequate | Hand-written assembly RE: demos, games, bootblocks, hardware-banging code — substantial research content added |
| `static/ansi_c_reversing.md` | 603 | ⚠️ Adequate | ANSI C RE: struct recovery, control flow reconstruction, library anchoring — BPTR + SAS/C convention details added |
| `static/cpp_vtables_reversing.md` | 745 | ⚠️ Adequate | C++ OOP RE: vtables, inheritance hierarchies, RTTI, name mangling — GCC vtable layout + C++ ABI details added |
| `static/other_languages.md` | 679 | ⚠️ Adequate | Non-C languages: AMOS, Blitz Basic, Amiga E, Modula-2, FORTH, ARexx — JForth corrected + BlitzLib table + E object layout added |

| Per-Compiler RE | Lines | Status | Notes |
|---|---|---|---|
| `static/compilers/README.md` | 102 | ✅ Adequate | Compiler identification flowchart and comparison matrix |
| `static/compilers/sasc.md` | 1006 | ✅ Adequate | SAS/C 5.x/6.x: LINK A5 + 9-reg save, all 4 calling conventions, register vs stack allocation, call-site patterns, IDA Python detection |
| `static/compilers/gcc.md` | 742 | ✅ Adequate | GCC 2.95.x: `.text` hunk, A6 frame pointer, `__CTOR_LIST__`, tail-call optimization, libnix startup, register allocation/stack variable identification |
| `static/compilers/vbcc.md` | 327 | ✅ Adequate | VBCC: No frame pointer, per-function saves, `__reg()`, cross-module optimization, `__MERGED` hunks |
| `static/compilers/stormc.md` | 321 | ✅ Adequate | StormC / StormC++: SAS/C-compatible C, unique C++ ABI, vtable layout differences, PowerPC support |
| `static/compilers/aztec_c.md` | 125 | ✅ Adequate | Manx Aztec C: D3-D7 save only (5 regs), D2 scratch, pre-1990 era |
| `static/compilers/lattice_c.md` | 153 | ✅ Adequate | Lattice C 3.x/4.x: SAS/C predecessor, evolutionary markers, simpler optimizer |
| `static/compilers/dice_c.md` | 135 | ✅ Adequate | DICE C: No frame pointer, `_mainCRTStartup`, fast compile speed, Matt Dillon's compiler |
| `static/code_vs_data_disambiguation.md` | 698 | ✅ Adequate | Code vs data disambiguation: IDA/Ghidra workflows, Amiga failure modes, detection scripts |

### 06 — Exec Kernel (exec.library)

| Article | Lines | Status | Notes |
|---|---|---|---|
| `multitasking.md` | 1156 | ✅ Deep | Scheduler, context switching, IPC, memory safety |
| `interrupts.md` | 404 | ✅ Adequate | Interrupt levels 1–6, INTENA/INTREQ, CIA interrupts |
| `io_requests.md` | 399 | ✅ Adequate | IORequest, DoIO, SendIO, AbortIO, device protocol |
| `tasks_processes.md` | 379 | ✅ Deep | Task/Process structs, state machine, creation |
| `memory_management.md` | 376 | ✅ Deep | AllocMem, FreeMem, MemHeader, memory types, pools |
| `signals.md` | 348 | ✅ Deep | AllocSignal, SetSignal, Wait, signal bit allocation |
| `message_ports.md` | 336 | ✅ Adequate | MsgPort, PutMsg, GetMsg, WaitPort |
| `lists_nodes.md` | 335 | ✅ Adequate | MinList/List/Node traversal, Insert/Remove operations |
| `exceptions_traps.md` | 320 | ✅ Adequate | M68k exception vectors, Trap handlers, Guru codes |
| `library_system.md` | 311 | ✅ Adequate | Library node, OpenLibrary lifecycle |
| `resident_modules.md` | 301 | ✅ Adequate | RomTag, RTF_AUTOINIT, FindResident |
| `semaphores.md` | 292 | ✅ Adequate | SignalSemaphore, shared/exclusive locking |
| `library_vectors.md` | 253 | ✅ Adequate | JMP table, LVO offsets, MakeFunctions, SetFunction |
| `exec_base.md` | 250 | ✅ Adequate | ExecBase at $4, system lists, hardware abstraction |

### 07 — DOS (dos.library)

| Article | Lines | Status | Notes |
|---|---|---|---|
| `filesystem.md` | 1246 | ✅ Deep | Tier 2 upgrade: OFS/FFS/PFS3/SFS/FFS2 deep-dive, RDB, Kickstart, multi-boot, fragmentation, partition IDs & on-disk layout, ADF reader, 5 antipatterns, 12 FAQ |
| `locks_examine.md` | 382 | ✅ Adequate | Lock semantics, ExNext/ExAll, named antipatterns |
| `file_io.md` | 285 | ✅ Adequate | Open/Close/Read/Write/Seek, buffered I/O, FileInfoBlock |
| `cli_shell.md` | 949 | ✅ Deep | CLI/Shell: architecture Mermaid, BCPL→C history, pipes (sequential temp files), I/O redirection operators, 7-pattern script cookbook (Safe Copy, Hardware Detection, Backup, Multi-Volume, File Loop, Wait-for-Volume, Toggle), ReadArgs API deep dive with template qualifiers, resident commands, shell environment (startup files, local/global vars, aliases, prompt customization), CON: window options & ANSI escape sequences, 24-item built-in commands table, 12 best practices, 4 named antipatterns (Naked WARN, Phantom PORT, Dot-Eater, Infinite Pipe), 4 pitfalls, historical context (BCPL/TRIPOS), modern analogies, 7 FAQ |
| `packet_system.md` | 93 | ✅ Adequate | DosPacket wire format, ACTION_* codes, handler protocol |
| `process_management.md` | 89 | ✅ Adequate | CreateNewProc, SystemTagList, Execute |
| `error_handling.md` | 89 | ✅ Adequate | IoErr, Fault, PrintFault, complete error code table |
| `dos_base.md` | 77 | ✅ Adequate | DosLibrary structure, RootNode, BCPL heritage |
| `pattern_matching.md` | 77 | ✅ Adequate | ParsePattern, MatchPattern, wildcard syntax |
| `environment.md` | 67 | ✅ Adequate | GetVar/SetVar, local/global/persistent env |

### 08 — Graphics (graphics.library)

| Article | Lines | Status | Notes |
|---|---|---|---|
| `pixel_conversion.md` | 1482 | ✅ Deep | Chunky↔Planar: naive, Kalms, Copper Chunky, Akiko, GPU swizzle — exemplary |
| `blitter_programming.md` | 980 | ✅ Deep | Blitter deep dive: minterms, cookie-cut, line draw, fill mode |
| `animation.md` | 804 | ✅ Deep | GEL system: BOBs, VSprites, AnimObs, collision, double buffering |
| `display_modes.md` | 645 | ✅ Deep | Tier 2 upgrade: ModeID flowchart, CRT vs flat-panel, 5 antipatterns, FPGA impact |
| `bitmap.md` | 598 | ✅ Deep | Tier 2 upgrade: AllocBitMap lifecycle, interleaved layout, cookbook |
| `views.md` | 469 | ✅ Deep | Tier 2 upgrade: 3-stage Mermaid pipeline, 3 antipatterns, GPU analogies |
| `ham_ehb_modes.md` | 442 | ✅ Adequate | HAM6/HAM8 encoding, EHB half-brite, FPGA decoder logic |
| `rastport.md` | 403 | ✅ Adequate | RastPort drawing context, layer clipping, text pipeline |
| `copper_programming.md` | 319 | ✅ Deep | Copper deep dive: copper list construction, gradient, raster effects |
| `sprites.md` | 306 | ❌ Pending | Tier 3 #15: needs antipatterns, pitfalls (HW vs SimpleSprite), FPGA sprite timing |
| `gfx_base.md` | 237 | ✅ Adequate | GfxBase, chipset detection, display pipeline overview |
| `text_fonts.md` | 215 | ❌ Pending | Tier 3 #16: needs cookbook (bitmap vs outline), font spacing pitfalls, ColorFont layout |
| `copper.md` | 124 | ✅ Adequate | Copper coprocessor basics, instruction format, UCopList |
| `blitter.md` | 109 | ✅ Adequate | Blitter DMA engine basics, minterms, BltBitMap |

### 09 — Intuition

| Article | Lines | Status | Notes |
|---|---|---|---|
| `idcmp.md` | 1060 | ✅ Deep | Event architecture, shared ports, antipatterns, cookbook — exemplary |
| `input_events.md` | 850 | ✅ Deep | Handler chain, QoS/priority, Commodities, latency analysis |
| `commodities.md` | 769 | ✅ Deep | Tier 1 creation: Exchange, hotkeys, CxObjects, brokers |
| `screens.md` | 582 | ❌ Pending | Tier 3 #17: needs antipatterns, cookbook (screen flipping, borderless, PAL→NTSC) |
| `boopsi.md` | 505 | ✅ Adequate | OOP dispatcher, ICA interconnection, custom class tutorial |
| `gadgets.md` | 403 | ❌ Pending | Tier 3 #20: needs antipatterns, BOOPSI command flow, GadTools→BOOPSI guide |
| `menus.md` | 378 | ❌ Pending | Tier 3 #19: needs menu render chain diagram, RemoveMenu/FreeMenu pitfalls |
| `windows.md` | 370 | ❌ Pending | Tier 3 #18: needs antipatterns ("The Borderless Too Soon"), FAQ, cookbook |
| `requesters.md` | 370 | ✅ Adequate | EasyRequest, ASL file/font/screenmode dialogs |
| `intuition_base.md` | 267 | ✅ Adequate | IntuitionBase, ViewLord, LockIBase |

**MUI Framework** (in `frameworks/mui/`):

| Article | Lines | Status | Notes |
|---|---|---|---|
| `README.md` | 1160 | ✅ Deep | Comprehensive MUI overview and documentation index |
| `02-architecture.md` | 529 | ✅ Deep | MUI architecture: BOOPSI classes, OOP design |
| `05-layout-system.md` | 478 | ✅ Deep | MUI layout: HGroup, VGroup, weight system |
| `12-reference-snippets.md` | 428 | ✅ Deep | MUI reference code collection |
| `06-widgets-overview.md` | 374 | ✅ Adequate | Widget catalog and usage |
| `09-custom-classes.md` | 292 | ✅ Adequate | MUI custom class development |
| `11-advanced-patterns.md` | 282 | ✅ Adequate | Advanced MUI patterns |
| `10-events-and-notifications.md` | 278 | ✅ Adequate | MUI event system |
| `03-getting-started.md` | 273 | ✅ Adequate | MUI quick-start guide |
| `04-core-concepts.md` | 235 | ✅ Adequate | Core MUI concepts |
| `07-windows-and-applications.md` | 213 | ✅ Adequate | Window and application management |
| `08-menus.md` | 211 | ✅ Adequate | MUI menu system |
| `01-introduction.md` | 133 | ✅ Adequate | MUI introduction |

### 10 — Devices

| Article | Lines | Status | Notes |
|---|---|---|---|
| `audio.md` | 945 | ✅ Deep | Tier 2 upgrade: 5 antipatterns, MOD deep-dive, 14-bit Paula, cookbook, FPGA impact |
| `timer.md` | 853 | ✅ Deep | Tier 2 upgrade: 8 antipatterns, 6-pattern cookbook, decision flowchart, FPGA impact |
| `scsi.md` | 287 | ✅ Adequate | Per-model HDD interfaces, Gayle bandwidth, TD64/NSD |
| `console.md` | 244 | ❌ Pending | Tier 3 #24: needs escape sequence table, raw console cookbook, buffering pitfalls |
| `input.md` | 216 | ✅ Adequate | Input handler chain, Commodities Exchange |
| `keyboard.md` | 179 | ✅ Adequate | CIA-A handshake, raw key codes, reset sequence, FPGA notes |
| `trackdisk.md` | 178 | ❌ Pending | Tier 3 #25: needs sector-level format diagram, MFM encoding, trackdisk vs filesystem |
| `parallel.md` | 149 | ✅ Adequate | Centronics parallel port: CIA-A Port B |
| `serial.md` | 130 | ✅ Adequate | UART/RS-232: CIA registers, baud rate, serial debugging |
| `gameport.md` | 130 | ✅ Adequate | Joystick/mouse: quadrature decoding, controller types |

### 11 — Libraries

| Article | Lines | Status | Notes |
|---|---|---|---|
| `iffparse.md` | 1031 | ✅ Deep | Tier 3 upgrade: nesting diagrams, ILBM/EHB pitfalls, PBM patterns |
| `datatypes.md` | 839 | ✅ Deep | Tier 1 creation: NewDTObject/LoadDTObject/GetDTAttrs |
| `amigaguide.md` | 760 | ✅ Deep | Tier 1 creation: .guide format, @commands, ARexx integration |
| `diskfont.md` | 619 | ✅ Deep | Bitmap font deep dive: .font format, glyph layout, color fonts |
| `translator.md` | 536 | ✅ Deep | Tier 1 creation: phonetic translation, narrator.device |
| `mathffp.md` | 468 | ✅ Adequate | Motorola FFP and IEEE 754 floating point formats |
| `locale.md` | 265 | ✅ Adequate | .cd/.ct catalog system, locale-aware formatting |
| `layers.md` | 224 | ❌ Pending | Tier 3 #23: needs Mermaid layer stacking diagram, damage region pitfalls |
| `expansion.md` | 217 | ✅ Adequate | Zorro II/III, AutoConfig ROM layout, FPGA notes |
| `utility.md` | 203 | ✅ Adequate | TagItem lists, callback hooks, date/time utilities |
| `workbench.md` | 194 | ✅ Adequate | WBStartup, AppWindow, AppIcon, AppMenuItem |
| `icon.md` | 188 | ✅ Adequate | .info format, DiskObject, ToolTypes, true-color icons |
| `rexxsyslib.md` | 176 | ✅ Adequate | ARexx hosting, command parsing, return codes |
| `arexx_integration.md` | 1128 | ✅ Adequate | Complete ARexx integration guide: dispatch tables, 6 antipatterns, use-case cookbook, event loop integration |
| `keymap.md` | 162 | ✅ Adequate | Raw-to-ASCII, KeyMap structure, dead keys |

### 12 — Networking

| Article | Lines | Status | Notes |
|---|---|---|---|
| `bsdsocket.md` | 1057 | ✅ Deep | Tier 2 upgrade: WaitSelect cookbook, multi-socket patterns, performance tables |
| `tcp_ip_stacks.md` | 426 | ✅ Adequate | Stack architecture: Amiga vs Unix, SANA-II integration, PPP/SLIP |
| `protocols.md` | 245 | ✅ Adequate | DNS, TCP client/server, UDP, DHCP sequence |
| `sana2.md` | 201 | ✅ Adequate | SANA-II driver spec: buffer hooks, send/receive patterns |

### 13 — Toolchain

| Article | Lines | Status | Notes |
|---|---|---|---|
| `vasm_vlink.md` | 842 | ✅ Deep | Bonus upgrade: modular architecture, Devpac/PhxAss compat, linker scripts, 5 examples |
| `vbcc.md` | 703 | ✅ Deep | Tier 1 creation: __reg() storage class, vlink integration, cross-compilation |
| `fd_files.md` | 203 | ✅ Adequate | FD/SFD file format and LVO generation |
| `debugging.md` | 191 | ✅ Adequate | Enforcer/MuForce, SnoopDOS, FS-UAE GDB remote, kprintf |
| `sasc.md` | 156 | ✅ Adequate | SAS/C 6.x: pragma format, __saveds/__asm, compiler flags |
| `stormc.md` | 106 | ✅ Adequate | StormC native IDE: C/C++, debugger, PowerPC support |
| `gcc_amiga.md` | 101 | ❌ Pending | Tier 3 #22: extremely thin stub — needs full build pipeline, Docker guide, linker scripts |
| `makefiles.md` | 97 | ✅ Adequate | GCC cross-compilation make patterns, vasm/vlink, mixed C+asm |
| `ndk.md` | 84 | ✅ Adequate | NDK versions (3.1/3.9/3.2): contents, cross-compiler integration |
| `pragmas.md` | 83 | ✅ Adequate | SAS/C pragmas, GCC inline asm, proto headers, fd2pragma |

### 14 — References

| Article | Lines | Status | Notes |
|---|---|---|---|
| `dos_lvo_table.md` | 169 | ✅ Adequate | Reference table — no narrative depth expected |
| `custom_chip_registers.md` | 160 | ✅ Adequate | Reference table — no narrative depth expected |
| `exec_lvo_table.md` | 142 | ✅ Adequate | Reference table — no narrative depth expected |
| `error_codes.md` | 93 | ✅ Adequate | Error code reference table — no narrative depth expected |

### 15 — FPU / MMU / Cache

| Article | Lines | Status | Notes |
|---|---|---|---|
| `fpu_architecture.md` | 1057 | ✅ Deep | Architecture deep-dive: 68881/68882 internals, 80-bit extended precision, CORDIC, Quake benchmark, AI quantization |
| `mmu_management.md` | 630 | ✅ Deep | MMU architecture: page tables, translation pipeline, MuLib, Enforcer, VMM |
| `cache_management.md` | 362 | ✅ Deep | CacheClearU/E, CACR, DMA coherency, CopyBack vs WriteThrough, cycle costs |
| `68040_68060_libraries.md` | 327 | ✅ Deep | Line-F trap handlers, RomTag structure, AttnFlags detection |

### 16 — Driver Development

| Article | Lines | Status | Notes |
|---|---|---|---|
| `rtg_driver.md` | 1020 | ✅ Deep | Picasso96/RTG: SetFunction patching, BoardInfo hooks, VRAM/CRTC |
| `sana2_driver.md` | 220 | ✅ Adequate | SANA-II network device driver specification |
| `ahi_driver.md` | 185 | ✅ Adequate | AHI retargetable audio driver interface |
| `device_driver_basics.md` | 174 | ✅ Adequate | IORequest lifecycle, BeginIO/AbortIO, unit management |

---

### Summary Statistics

| Status | Count |
|---|---|
| ✅ Deep | 56 |
| ✅ Adequate | 113 |
| ⚠️ Thin | 0 |
| ❌ Pending (Tier 3) | 10 |
| **Total** | **179** |

> MUI framework adds 13 additional articles (4 Deep, 9 Adequate) tracked separately above.
> **Progress**: 8 per-compiler RE articles created (1 README + 7 compiler field manuals). 1 code-vs-data disambiguation article added. 1 ARexx integration guide added. 10 Tier 3 items remain.

---

## Recommended Execution Order

| Priority | Item | Type | Effort | Status |
|---|---|---|---|---|
| 1 | Datatypes System (#1) | New Article | Large | ✅ DONE |
| 2 | AmigaGuide (#2) | New Article | Medium | ✅ DONE |
| 3 | commodities.library (#3) | New Article | Medium | ✅ DONE |
| 4 | `hardware_models.md` upgrade (#6) | Upgrade | Medium | ✅ DONE |
| 5 | `bitmap.md` upgrade (#7) | Upgrade | Medium | ✅ DONE |
| 6 | `bsdsocket.md` upgrade (#8) | Upgrade | Medium | ✅ DONE |
| 7 | VBCC Compiler (#5) | New Article | Medium | ✅ DONE |
| 8 | `audio.md` upgrade (#9) | Upgrade | Medium | ✅ DONE |
| 9 | `timer.md` upgrade (#10) | Upgrade | Medium | ✅ DONE |
| 10 | translator.library (#4) | New Article | Medium | ✅ DONE |

### Bonus Completed (Not in Original Scan)

| Item | Description |
|---|---|
| `13_toolchain/vasm_vlink.md` | Upgraded from 114→842 lines: modular architecture, Devpac/PhxAss compatibility, optimization system, linker scripts, C↔asm interop, 5 worked examples, assembler comparison matrix, GitHub mirrors |
| `11_libraries/iffparse.md` | Upgraded from 271→1031 lines (in original Tier 3 #21) |

### What Remains

**Tier 2 — ALL COMPLETE**

| # | File | Current |
|---|---|---|
| 9 | `10_devices/audio.md` | ✅ DONE (945 lines) |
| 10 | `10_devices/timer.md` | ✅ DONE (853 lines) |
| 11 | `01_hardware/aga_a1200_a4000/cpu_030_040.md` | ✅ DONE (424 lines) |
| 12 | `08_graphics/views.md` | ✅ DONE (469 lines) |
| 13 | `08_graphics/display_modes.md` | ✅ DONE (645 lines) |
| 14 | `07_dos/filesystem.md` | ✅ DONE (1246 lines) |

**Tier 3 — 10 pending quality boosts:**

| # | File | Current |
|---|---|---|
| 15 | `08_graphics/sprites.md` | 306 lines |
| 16 | `08_graphics/text_fonts.md` | 215 lines |
| 17 | `09_intuition/screens.md` | 582 lines |
| 18 | `09_intuition/windows.md` | 370 lines |
| 19 | `09_intuition/menus.md` | 378 lines |
| 20 | `09_intuition/gadgets.md` | 403 lines |
| 22 | `13_toolchain/gcc_amiga.md` | 101 lines |
| 23 | `11_libraries/layers.md` | 224 lines |
| 24 | `10_devices/console.md` | 244 lines |
| 25 | `10_devices/trackdisk.md` | 178 lines |

**Tier 4 — 5 pending advanced topics:**

| # | File | Current |
|---|---|---|
| 26 | `05_reversing/custom_loaders_and_drm.md` | 168 lines |
| 27 | `08_graphics/rtg_programming.md` | 0 lines |
| 28 | `11_libraries/ahi_programming.md` | 0 lines |
| 29 | `17_demoscene/README.md` | 0 lines |
| 30 | `13_toolchain/cross_compilation_guide.md` | 0 lines |

> **Progress**: 15 of 30 items complete (50%). Tier 1 and 2 fully cleared. 10 Tier 3 items and 5 Tier 4 items remain.
