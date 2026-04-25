[← Home](../README.md)

# FPU, MMU & Cache — Overview

The Motorola 68040 and 68060 processors introduced new complexity for Amiga developers: removed instructions requiring software trap emulation, data/instruction caches needing explicit coherency management, and on-chip MMUs enabling virtual memory and memory protection. AmigaOS itself treats these CPU upgrades as transparent additions to the flat memory model, but third-party libraries and tools (MuLib, Enforcer, VMM) unlock the full capability. For MiSTer FPGA developers, the TG68K core's cache and MMU implementation status directly determines which software runs correctly.

## Section Index

| File | Description |
|---|---|
| [68040_68060_libraries.md](68040_68060_libraries.md) | 68040.library / 68060.library — Line-F trap handlers that emulate missing FPU and integer instructions removed from the 040/060 microcode; RomTag structure, installation, detection via AttnFlags, performance trade-offs |
| [cache_management.md](cache_management.md) | Cache control deep dive: CacheClearU/CacheClearE/CacheControl API, CACR register bits, DMA coherency protocol (CachePreDMA/CachePostDMA), CopyBack vs WriteThrough modes, quantified cycle costs |
| [mmu_management.md](mmu_management.md) | MMU architecture across 68030/040/060: page tables, address translation pipeline, transparent translation registers, MuLib API, Enforcer hit detection, VMM demand-paged virtual memory, direct MMU programming examples |
