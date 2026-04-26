# 🔧 Amiga OS 3.1/3.2 — The Developer's Source of Truth

**From cold boot to driver authoring**

> *Everything Commodore never published in one place.*
>
> A comprehensive, self-contained technical reference for AmigaOS Classic — covering hardware registers, OS internals, reverse engineering, and cross-compilation. Written for developers building on real hardware, FPGA cores, and emulators.

---

## Why This Exists

The Amiga's documentation was scattered across out-of-print manuals, Usenet posts, ADCD archives, and tribal knowledge passed between developers since 1985. This repository consolidates it into a single, cross-linked, searchable knowledge base — verified against NDK 3.9 headers and official Commodore documentation.

### What's Inside

| Layer | Coverage |
|---|---|
| **⚙️ Hardware** | Custom chip registers (OCS/ECS/AGA), Copper & Blitter programming, memory architecture (Chip/Fast/Slow RAM), CIA, Zorro bus, CPU feature matrix, **per-model hardware (A1000 WCS, A2000 Zorro II, CDTV DMAC/CD-ROM, CD32 Akiko C2P)** |
| **🔌 Boot & Init** | Cold boot sequence, ROM checksum, resident module scan, Kickstart init, startup-sequence |
| **📦 Binary Format** | HUNK executable format (every record type), relocation, debug info, overlays |
| **🔗 Linking & ABI** | .fd files, LVO tables, register calling conventions, compiler stubs, SetFunction |
| **🧠 Exec Kernel** | Tasks, interrupts, signals, semaphores, memory management, message ports, exception vectors |
| **💾 AmigaDOS** | File I/O, filesystem layout (FFS/OFS), CLI/Shell scripting, packet system |
| **🎨 Graphics** | Planar bitmaps, Copper deep dive, Blitter deep dive, HAM/EHB modes, sprites, display pipeline |
| **🖥️ Intuition** | Screens, windows, IDCMP, GadTools, BOOPSI, menus |
| **📟 Devices** | trackdisk, SCSI, serial, parallel, timer, audio, keyboard, console |
| **📚 Libraries** | utility, expansion, IFFParse, locale, ARexx, math, layers, diskfont, DataTypes, AmigaGuide, translator (speech) |
| **🌐 Networking** | bsdsocket.library API, SANA-II, TCP/IP stacks comparison |
| **🛠️ Toolchain** | GCC (bebbo/Codeberg), vasm/vlink, SAS/C, NDK, Makefiles, debugging |
| **🔍 Reverse Engineering** | IDA/Ghidra setup, compiler fingerprints, binary patching, 3 case studies |
| **🧮 FPU, MMU & Cache** | 68881/68882 FPU architecture, 68040/060 Line-F FPU emulation, PMMU page tables, cache coherency |
| **🏗️ Driver Development** | exec.device framework, SANA-II network drivers, Picasso96/RTG, AHI audio |

### Quick Start

| You are... | Start here |
|---|---|
| **New to Amiga** | [History & chipsets](00_overview/history.md) → [Boot sequence](02_boot_sequence/cold_boot.md) → [Exec kernel](06_exec_os/exec_base.md) |
| **Writing code** | [Toolchain setup](13_toolchain/gcc_amiga.md) → [Calling conventions](04_linking_and_libraries/register_conventions.md) → [.fd files](04_linking_and_libraries/fd_files.md) |
| **Doing hardware** | [Address space](01_hardware/common/address_space.md) → [Memory types](01_hardware/common/memory_types.md) → [Custom registers](01_hardware/ocs_a500/custom_registers.md) → [Copper programming](08_graphics/copper_programming.md) |
| **Reverse engineering** | [RE methodology](05_reversing/methodology.md) → [IDA/Ghidra setup](05_reversing/ida_setup.md) → [API call identification](05_reversing/static/api_call_identification.md) |
| **Building an FPGA core** | [Hardware models](00_overview/hardware_models.md) → [AGA chipset](01_hardware/aga_a1200_a4000/chipset_aga.md) → [68040/060 libs](15_fpu_mmu_cache/68040_68060_libraries.md) |

---

> **Scope:** AmigaOS Classic 3.1 (Kickstart 40.x) and 3.2 (Kickstart 47.x).
> Hardware coverage spans all chipset generations: OCS, ECS, AGA.

## Sources

| Reference | URL / Path |
|---|---|
| ADCD 2.1 Online | http://amigadev.elowar.com/read/ADCD_2.1/ |
| NDK 3.9 | Aminet: `dev/misc/NDK39.lha` (free) |
| NDK 3.2 | Hyperion Entertainment (commercial) |

| ROM Kernel Manual: Libraries | ADCD 2.1 → `Libraries_Manual_guide/` |
| ROM Kernel Manual: Devices | ADCD 2.1 → `Devices_Manual_guide/` |
| ROM Kernel Manual: Hardware | ADCD 2.1 → `Hardware_Manual_guide/` |
| Includes & Autodocs | ADCD 2.1 → `Includes_and_Autodocs_3._guide/` |

---

## Documentation Map

### 00 — Overview
| File | Topic |
|---|---|
| [history.md](00_overview/history.md) | Amiga lineage, chipset generations timeline |
| [hardware_models.md](00_overview/hardware_models.md) | Per-model specification table |
| [os_versions.md](00_overview/os_versions.md) | OS 3.0 → 3.1 → 3.2 delta matrix |

### 01 — Hardware (by chipset generation)
| Folder | Coverage |
|---|---|
| [common/](01_hardware/common/) | M68k CPU, address space, **memory types (Chip/Fast/Slow RAM)**, CIA chips, Zorro bus, **Gayle IDE/PCMCIA** |
| [ocs_a500/](01_hardware/ocs_a500/) | OCS chipset: custom registers, copper, blitter, sprites, Paula, **A1000 WCS**, **A2000 Zorro II**, **CDTV hardware** |
| [ecs_a600_a3000/](01_hardware/ecs_a600_a3000/) | ECS chipset: Super Agnus, productivity modes, **Gary** system controller |
| [aga_a1200_a4000/](01_hardware/aga_a1200_a4000/) | AGA chipset: Alice, Lisa, copper, blitter (64-bit), palette, **CD32 Akiko**, **A4000T SCSI** |

### 02 — Boot Sequence
| File | Topic |
|---|---|
| [cold_boot.md](02_boot_sequence/cold_boot.md) | Power-on: CPU reset vectors, ROM checksum, hardware reset, memory detection, diagnostic indicators |
| [**kickstart_rom.md**](02_boot_sequence/kickstart_rom.md) | **Kickstart ROM internals: binary structure, module inventory, extraction tools, custom ROM building** |
| [kickstart_init.md](02_boot_sequence/kickstart_init.md) | ExecBase creation, capture vectors, ROM scan algorithm, 4-phase resident init |
| [dos_boot.md](02_boot_sequence/dos_boot.md) | strap module, boot block format and execution, MountList, Startup-Sequence walkthrough |
| [early_startup.md](02_boot_sequence/early_startup.md) | Early Startup Control menu: device selection, display mode, recovery scenarios |

### 03 — Executable Loader & HUNK Format
| File | Topic |
|---|---|
| [hunk_format.md](03_loader_and_exec_format/hunk_format.md) | Complete HUNK specification — all 22 type codes, wire format, memory flags, advisory bits |
| [hunk_ext_deep_dive.md](03_loader_and_exec_format/hunk_ext_deep_dive.md) | HUNK_EXT: exports (EXT_DEF), imports (EXT_REF32), commons, linker resolution |
| [hunk_relocation.md](03_loader_and_exec_format/hunk_relocation.md) | Relocation mechanics: visual before/after, RELOC32/SHORT/DREL32, PC-relative impact |
| [hunk_debug_info.md](03_loader_and_exec_format/hunk_debug_info.md) | HUNK_SYMBOL and HUNK_DEBUG: stabs format, debugger consumption, stripping |
| [exe_load_pipeline.md](03_loader_and_exec_format/exe_load_pipeline.md) | LoadSeg → AllocMem → relocation → segment chain → CreateProc → entry point |
| [object_file_format.md](03_loader_and_exec_format/object_file_format.md) | HUNK_UNIT object files, multi-section layout, HUNK_LIB archives, linker operation |
| [overlay_system.md](03_loader_and_exec_format/overlay_system.md) | HUNK_OVERLAY: tree architecture, runtime overlay manager, modern alternatives |
| [**exe_crunchers.md**](03_loader_and_exec_format/exe_crunchers.md) | **Executable packers: PP20/Imploder/Shrinkler, decrunch stubs, algorithms, detection** |

### 04 — Linking & Library Integration
| File | Topic |
|---|---|
| [library_structure.md](04_linking_and_libraries/library_structure.md) | Library memory layout, JMP table encoding, MakeLibrary, complete library creation example |
| [shared_libraries_runtime.md](04_linking_and_libraries/shared_libraries_runtime.md) | OpenLibrary resolution, ramlib disk loader, version negotiation, expunge mechanics |
| [register_conventions.md](04_linking_and_libraries/register_conventions.md) | Register ABI: integer, FPU, varargs/TagItem, small-data model, __saveds |
| [fd_files.md](04_linking_and_libraries/fd_files.md) | .fd descriptor format, LVO calculation, proto/inline generation |
| [lvo_table.md](04_linking_and_libraries/lvo_table.md) | Complete exec.library LVO table, IDA reconstruction script |
| [compiler_stubs.md](04_linking_and_libraries/compiler_stubs.md) | SAS/C, GCC, VBCC call patterns — compiler signature identification |
| [inline_stubs.md](04_linking_and_libraries/inline_stubs.md) | Pragma (SAS/C), inline asm (GCC), __reg (VBCC), stub generation tools |
| [link_libraries.md](04_linking_and_libraries/link_libraries.md) | amiga.lib, sc.lib, libnix, auto.lib, WBStartup glue, stack cookie |
| [startup_code.md](04_linking_and_libraries/startup_code.md) | c.o / gcrt0.S: entry contract, CLI vs WB detection, argument parsing |
| [setfunction.md](04_linking_and_libraries/setfunction.md) | Runtime function patching: canonical pattern, chaining, RE detection |

### 05 — Reverse Engineering
| File | Topic |
|---|---|
| [methodology.md](05_reversing/methodology.md) | General Amiga RE workflow |
| [ida_setup.md](05_reversing/ida_setup.md) | IDA Pro setup for Amiga binaries |
| [compiler_fingerprints.md](05_reversing/compiler_fingerprints.md) | SAS/C vs GCC vs VBCC codegen patterns |
| [patching_techniques.md](05_reversing/patching_techniques.md) | Binary patching strategies |

| Static Analysis | Topic |
|---|---|
| [api_call_identification.md](05_reversing/static/api_call_identification.md) | Recognising OS API calls in disassembly |
| [hunk_reconstruction.md](05_reversing/static/hunk_reconstruction.md) | Rebuilding HUNK structure |
| [library_jmp_table.md](05_reversing/static/library_jmp_table.md) | Decoding library JMP tables |
| [m68k_codegen_patterns.md](05_reversing/static/m68k_codegen_patterns.md) | Compiler-specific assembly idioms |
| [string_xref_analysis.md](05_reversing/static/string_xref_analysis.md) | String cross-reference hunting |
| [struct_recovery.md](05_reversing/static/struct_recovery.md) | Recovering C structures from assembly |

| Dynamic Analysis | Topic |
|---|---|
| [enforcer_mungwall.md](05_reversing/dynamic/enforcer_mungwall.md) | Enforcer, MungWall memory debugging |
| [setfunction_patching.md](05_reversing/dynamic/setfunction_patching.md) | Runtime function hooking |
| [live_memory_probing.md](05_reversing/dynamic/live_memory_probing.md) | Live memory inspection |
| [serial_debug.md](05_reversing/dynamic/serial_debug.md) | Serial debug output |

| [ramdrive_device.md](05_reversing/case_studies/ramdrive_device.md) | RAM disk device driver RE |

### 06 — Exec Kernel (OS 3.1/3.2)
| File | Topic |
|---|---|
| [exec_base.md](06_exec_os/exec_base.md) | ExecBase — absolute address $4, system lists, hardware detection, structure layout |
| [**multitasking.md**](06_exec_os/multitasking.md) | **Multitasking deep-dive — scheduler, context switching, IPC, memory safety, real-world scenarios** |
| [tasks_processes.md](06_exec_os/tasks_processes.md) | Task/Process structs, state machine, creation, cleanup, priority guidelines |
| [library_system.md](06_exec_os/library_system.md) | Library node, OpenLibrary lifecycle, expunge mechanics, version management |
| [library_vectors.md](06_exec_os/library_vectors.md) | JMP table, LVO offsets, MakeFunctions, SetFunction patching |
| [interrupts.md](06_exec_os/interrupts.md) | Interrupt levels 1–6, INTENA/INTREQ, server chains, CIA interrupts, software interrupts |
| [exceptions_traps.md](06_exec_os/exceptions_traps.md) | M68k exception vectors, TRAP handlers, Guru Meditation decoder, Line-F emulation |
| [memory_management.md](06_exec_os/memory_management.md) | AllocMem/AllocVec, MEMF flags, pools, fragmentation, MemHeader internals |
| [message_ports.md](06_exec_os/message_ports.md) | MsgPort, PutMsg, GetMsg, WaitPort, ownership rules, request-reply pattern |
| [signals.md](06_exec_os/signals.md) | AllocSignal, Signal, Wait, SetSignal, multi-source event loop patterns |
| [semaphores.md](06_exec_os/semaphores.md) | SignalSemaphore, shared/exclusive locking, deadlock avoidance, decision guide |
| [io_requests.md](06_exec_os/io_requests.md) | IORequest, DoIO, SendIO, CheckIO, AbortIO, IOF_QUICK, timer device example |
| [lists_nodes.md](06_exec_os/lists_nodes.md) | MinList/List/Node traversal, sentinel design, Enqueue, safe iteration |
| [resident_modules.md](06_exec_os/resident_modules.md) | RomTag, RTF_AUTOINIT, boot priority, ROM scan, disk-resident loading |

### 07 — AmigaDOS
| File | Topic |
|---|---|
| [dos_base.md](07_dos/dos_base.md) | DosLibrary structure and global state |
| [file_io.md](07_dos/file_io.md) | Open/Read/Write, FileHandle, BPTR |
| [locks_examine.md](07_dos/locks_examine.md) | Lock/UnLock, Examine, FileInfoBlock |
| [pattern_matching.md](07_dos/pattern_matching.md) | ParsePattern, MatchPattern |
| [process_management.md](07_dos/process_management.md) | CreateNewProc, SystemTagList |
| [packet_system.md](07_dos/packet_system.md) | DosPacket, ACTION_* codes |
| [filesystem.md](07_dos/filesystem.md) | FFS/OFS block layout, hash, checksum |
| [environment.md](07_dos/environment.md) | GetVar/SetVar, local/global env variables |
| [error_handling.md](07_dos/error_handling.md) | IoErr, error codes, PrintFault |
| [cli_shell.md](07_dos/cli_shell.md) | CLI/Shell: pipes, redirection, scripts, ReadArgs |

### 08 — Graphics
| File | Topic |
|---|---|
| [gfx_base.md](08_graphics/gfx_base.md) | GfxBase, chip detection, PAL/NTSC |
| [bitmap.md](08_graphics/bitmap.md) | Planar BitMap, pixel layout, allocation |
| [copper.md](08_graphics/copper.md) | Copper coprocessor, MOVE/WAIT/SKIP, UCopList |
| [copper_programming.md](08_graphics/copper_programming.md) | Copper deep dive: architecture, system diagram, examples |
| [blitter.md](08_graphics/blitter.md) | Blitter DMA, minterms, BltBitMap |
| [blitter_programming.md](08_graphics/blitter_programming.md) | Blitter deep dive: cookie-cut, fill, line draw |
| [sprites.md](08_graphics/sprites.md) | Hardware sprites, SimpleSprite |
| [rastport.md](08_graphics/rastport.md) | RastPort, drawing primitives, layers |
| [views.md](08_graphics/views.md) | View/ViewPort, MakeVPort, display pipeline |
| [text_fonts.md](08_graphics/text_fonts.md) | TextFont, OpenFont, text rendering |
| [display_modes.md](08_graphics/display_modes.md) | ModeID, display database |
| [ham_ehb_modes.md](08_graphics/ham_ehb_modes.md) | HAM6, HAM8, EHB special display modes |
| [animation.md](08_graphics/animation.md) | GEL system: BOBs, VSprites, AnimObs |

### 09 — Intuition
| File | Topic |
|---|---|
| [intuition_base.md](09_intuition/intuition_base.md) | IntuitionBase global state |
| [screens.md](09_intuition/screens.md) | OpenScreen, SA_ tags, public screens |
| [windows.md](09_intuition/windows.md) | OpenWindow, WA_ tags, event loop |
| [gadgets.md](09_intuition/gadgets.md) | GadTools, BOOPSI gadgets |
| [menus.md](09_intuition/menus.md) | MenuStrip construction |
| [requesters.md](09_intuition/requesters.md) | EasyRequest, ASL file/font requesters |
| [idcmp.md](09_intuition/idcmp.md) | IDCMP message classes, IntuiMessage |
| [boopsi.md](09_intuition/boopsi.md) | BOOPSI object system, custom classes |
| [input_events.md](09_intuition/input_events.md) | InputEvent, Commodities Exchange |
| [commodities.md](09_intuition/commodities.md) | Commodities Exchange: hotkeys, screen blankers, CxObject API |

### 10 — Devices
| File | Topic |
|---|---|
| [trackdisk.md](10_devices/trackdisk.md) | Floppy I/O, geometry |
| [scsi.md](10_devices/scsi.md) | Hard disk, HD_SCSICMD |
| [serial.md](10_devices/serial.md) | RS-232 serial |
| [parallel.md](10_devices/parallel.md) | Centronics parallel |
| [timer.md](10_devices/timer.md) | Timing, delays, E-clock |
| [audio.md](10_devices/audio.md) | DMA audio channels |
| [keyboard.md](10_devices/keyboard.md) | Keycodes, key matrix |
| [gameport.md](10_devices/gameport.md) | Joystick and mouse |
| [input.md](10_devices/input.md) | Event stream merging |
| [console.md](10_devices/console.md) | Text terminal, escape sequences |

### 11 — Libraries
| File | Topic |
|---|---|
| [utility.md](11_libraries/utility.md) | TagItems, hooks, date utilities |
| [expansion.md](11_libraries/expansion.md) | Zorro bus, AutoConfig |
| [icon.md](11_libraries/icon.md) | Workbench icons, DiskObject |
| [workbench.md](11_libraries/workbench.md) | WBStartup, AppWindow |
| [iffparse.md](11_libraries/iffparse.md) | IFF file parsing: ILBM/8SVX/ANIM, nested chunks, ByteRun1, PBM deinterleaving, clipboard, decision guide vs DataTypes |
| [locale.md](11_libraries/locale.md) | Internationalization, catalogs |
| [keymap.md](11_libraries/keymap.md) | Keyboard mapping, MapRawKey |
| [rexxsyslib.md](11_libraries/rexxsyslib.md) | ARexx interface |
| [mathffp.md](11_libraries/mathffp.md) | Floating point libraries, FFP, IEEE |
| [layers.md](11_libraries/layers.md) | Window clipping layers |
| [diskfont.md](11_libraries/diskfont.md) | **Bitmap fonts: .font file format, FontContentsHeader, glyph bitmap layout, FONTS: assign, adding fonts, bitmap vs TrueType, Compugraphic outline fonts** |
| [datatypes.md](11_libraries/datatypes.md) | DataTypes system: object-oriented file loading for images, sound, text, animation |
| [amigaguide.md](11_libraries/amigaguide.md) | AmigaGuide hypertext help system: database format, API, context-sensitive help |
| [translator.md](11_libraries/translator.md) | translator.library: English-to-phonetic translation, narrator.device integration, ARPABET phonemes |

### 12 — Networking
| File | Topic |
|---|---|
| [bsdsocket.md](12_networking/bsdsocket.md) | **BSD socket API deep dive: event-loop patterns, WaitSelect signal integration, non-blocking I/O, multi-socket design, performance** |
| [sana2.md](12_networking/sana2.md) | SANA-II device driver interface |
| [tcp_ip_stacks.md](12_networking/tcp_ip_stacks.md) | AmiTCP vs Miami vs Roadshow |
| [protocols.md](12_networking/protocols.md) | DNS, HTTP, DHCP |

### 13 — Toolchain
| File | Topic |
|---|---|
| [vasm_vlink.md](13_toolchain/vasm_vlink.md) | **vasm assembler & vlink linker: modular architecture, Devpac/PhxAss compatibility, optimization system, linker scripts, C↔asm interop, 30+ output formats** |
| [gcc_amiga.md](13_toolchain/gcc_amiga.md) | m68k-amigaos-gcc (bebbo fork, Codeberg) |
| [vbcc.md](13_toolchain/vbcc.md) | **VBCC cross-compiler: `__reg()` register control, AmigaOS/MorphOS/AROS, vlink, fast compile times** |
| [sasc.md](13_toolchain/sasc.md) | SAS/C 6.x compiler |
| [stormc.md](13_toolchain/stormc.md) | StormC native IDE and C/C++ compiler |
| [fd_files.md](13_toolchain/fd_files.md) | FD/SFD file format, Python parser |
| [pragmas.md](13_toolchain/pragmas.md) | Compiler pragmas, inline stubs |
| [ndk.md](13_toolchain/ndk.md) | NDK versions, contents, downloads |
| [makefiles.md](13_toolchain/makefiles.md) | Cross-compilation Makefile patterns |
| [debugging.md](13_toolchain/debugging.md) | Enforcer, SnoopDOS, GDB remote, kprintf |

### 14 — References
| File | Topic |
|---|---|
| [custom_chip_registers.md](14_references/custom_chip_registers.md) | Complete custom chip register map |
| [exec_lvo_table.md](14_references/exec_lvo_table.md) | exec.library LVO table |
| [dos_lvo_table.md](14_references/dos_lvo_table.md) | dos.library LVO table |
| [error_codes.md](14_references/error_codes.md) | DOS error code reference |

### 15 — FPU, MMU & Cache
| File | Topic |
|---|---|
| [fpu_architecture.md](15_fpu_mmu_cache/fpu_architecture.md) | FPU architecture & history: 68881/68882, 68040/060 FPU, die budget, transistor counts, coprocessor interface, FPU vs soft-float benchmarks, Amiga FPU accelerator landscape |
| [68040_68060_libraries.md](15_fpu_mmu_cache/68040_68060_libraries.md) | 68040/060 FPU and instruction emulation libraries |
| [mmu_management.md](15_fpu_mmu_cache/mmu_management.md) | MMU page tables, mmu.library, Enforcer, VMM |
| [cache_management.md](15_fpu_mmu_cache/cache_management.md) | CacheClearU, CACR, DMA coherency |

### 16 — Driver Development
| File | Topic |
|---|---|
| [device_driver_basics.md](16_driver_development/device_driver_basics.md) | Exec device framework, BeginIO/AbortIO |
| [sana2_driver.md](16_driver_development/sana2_driver.md) | Writing SANA-II network drivers |
| [rtg_driver.md](16_driver_development/rtg_driver.md) | Writing Picasso96/RTG display drivers |
| [ahi_driver.md](16_driver_development/ahi_driver.md) | Writing AHI audio drivers |
