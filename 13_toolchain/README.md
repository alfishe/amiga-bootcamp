[← Home](../README.md)

# Toolchain — Overview

Development tools for building Amiga software, from native compilers to modern cross-compilation environments.

## Section Index

| File | Description |
|---|---|
| [gcc_amiga.md](gcc_amiga.md) | m68k-amigaos-gcc cross-compiler: bebbo's toolchain, Docker setup, CPU targets, libnix/ixemul startup |
| [vbcc.md](vbcc.md) | **VBCC: Volker Barthelmann's portable C compiler — `__reg()` storage class, AmigaOS/MorphOS/AROS targets, vlink integration, cross-compilation** |
| [sasc.md](sasc.md) | SAS/C 6.x: pragma format with register encoding, compiler/linker flags, __saveds/__asm idioms, SAS/C vs GCC comparison |
| [stormc.md](stormc.md) | StormC native IDE: C/C++ with exceptions, integrated debugger, PowerPC support, version history |
| [vasm_vlink.md](vasm_vlink.md) | **vasm assembler & vlink linker: modular architecture (CPU/syntax/output modules), Devpac/PhxAss compatibility, optimization system, linker scripts, multi-file projects, C↔asm interop, 30+ output formats, cross-platform workflows** |
| [fd_files.md](fd_files.md) | FD/SFD file format and LVO generation |
| [pragmas.md](pragmas.md) | Compiler pragmas and inline stubs: SAS/C pragmas, GCC inline asm, proto headers, fd2pragma |
| [ndk.md](ndk.md) | NDK versions (3.1/3.9/3.2): contents, downloads, cross-compiler integration |
| [makefiles.md](makefiles.md) | Makefile patterns for GCC cross-compilation, vasm/vlink assembly, mixed C+asm projects |
| [debugging.md](debugging.md) | Debugging tools: Enforcer/MuForce memory watchdog, SnoopDOS tracing, FS-UAE GDB remote, kprintf, debugging checklist |
