[← Home](../README.md) · [Toolchain](README.md)

# vasm and vlink — Assembler and Linker

## Overview

**vasm** is a modern, free, multi-target assembler with excellent Amiga support. **vlink** is its companion linker. Together they form the primary open-source toolchain for 68k Amiga development.

---

## Installation

```bash
# Build from source:
wget http://sun.hasenbraten.de/vasm/release/vasm.tar.gz
tar xzf vasm.tar.gz && cd vasm
make CPU=m68k SYNTAX=mot       # Motorola syntax
# or:
make CPU=m68k SYNTAX=madmac    # Atari MadMac syntax

# vlink:
wget http://sun.hasenbraten.de/vlink/release/vlink.tar.gz
tar xzf vlink.tar.gz && cd vlink && make
```

---

## vasm Usage

```bash
# Assemble to Amiga hunk object:
vasmm68k_mot -Fhunk -o output.o input.s

# Common flags:
#   -Fhunk          — output Amiga hunk format
#   -Fbin           — raw binary
#   -Felf            — ELF format
#   -m68000          — target 68000 (default)
#   -m68020          — target 68020+
#   -m68040          — target 68040
#   -m68060          — target 68060
#   -no-opt          — disable optimisations
#   -I<path>         — include path
#   -D<sym>=<val>    — define symbol
#   -phxass          — PhxAss compatibility mode
#   -devpac          — Devpac compatibility mode
```

---

## vlink Usage

```bash
# Link hunk objects into executable:
vlink -bamigahunk -o output input1.o input2.o -Llib -lexec -ldos

# Common flags:
#   -bamigahunk     — output Amiga hunk executable
#   -brawbin1        — raw binary
#   -s               — strip symbols
#   -L<path>         — library search path
#   -l<lib>          — link with library
#   -Rshort          — use short (16-bit) relocations where possible
```

---

## Example: Minimal Amiga Executable

```asm
; hello.s — minimal AmigaOS executable
    SECTION code,CODE

start:
    move.l  4.w,a6          ; ExecBase
    lea     dosname(pc),a1
    moveq   #0,d0
    jsr     -552(a6)        ; OpenLibrary
    tst.l   d0
    beq.s   .exit
    move.l  d0,a6           ; DOSBase

    jsr     -60(a6)         ; Output() → stdout handle
    move.l  d0,d1
    lea     msg(pc),a0
    move.l  a0,d2
    moveq   #12,d3
    jsr     -48(a6)         ; Write(fh, buf, len)

    move.l  a6,a1
    move.l  4.w,a6
    jsr     -414(a6)        ; CloseLibrary

.exit:
    moveq   #0,d0
    rts

dosname: dc.b "dos.library",0
msg:     dc.b "Hello Amiga",10
    EVEN
```

```bash
vasmm68k_mot -Fhunk -o hello.o hello.s
vlink -bamigahunk -o hello hello.o
```

---

## References

- vasm: http://sun.hasenbraten.de/vasm/
- vlink: http://sun.hasenbraten.de/vlink/
