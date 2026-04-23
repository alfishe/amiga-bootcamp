[← Home](../README.md) · [Linking & Libraries](README.md)

# Startup Code — c.o / gcrt0.S

## Overview

The AmigaOS **startup code** is the first code that runs when an executable is launched. It bridges the OS loader (which jumps to hunk 0 offset 0) and the C `main()` function. Understanding it is critical for reverse engineering — it reveals the initialisation sequence, library opens, argument parsing, and the Workbench vs CLI detection path.

---

## Entry Point Contract

When `CreateProc()` dispatches the new task, the CPU jumps to the first longword of hunk 0 with:

| Register | Value |
|---|---|
| D0 | Length of CLI argument string |
| A0 | Pointer to CLI argument string (or NULL for Workbench) |
| A1 | Pointer to WBStartup message (Workbench) or NULL (CLI) |
| A6 | (caller's A6 — not reliable) |
| SP | Top of the allocated stack |

---

## SAS/C Startup (c.o)

The SAS/C `c.o` module is the canonical AmigaOS C startup:

```asm
_start:
    ; 1. Get SysBase from absolute address 4
    MOVE.L  4.W, A6
    MOVE.L  A6, _SysBase

    ; 2. Detect CLI vs Workbench launch
    MOVE.L  D0, _RawCommandLen     ; save CLI arg length
    MOVE.L  A0, _RawCommandStr     ; save CLI arg pointer
    TST.L   A1                     ; A1=NULL means CLI, non-NULL = Workbench
    BEQ.S   .cli_launch

    ; Workbench path:
    MOVE.L  A1, _WBenchMsg         ; save WBStartup message
    JSR     _OpenLibraries          ; open DOS, graphics etc.
    BSR     _main                   ; call C main()
    BRA.S   .exit

.cli_launch:
    JSR     _OpenLibraries
    BSR     _main
    ; fall through to exit

.exit:
    MOVE.L  D0, _ReturnCode         ; main() return value
    JSR     _CloseLibraries
    ; return D0 to AmigaDOS
    RTS
```

### _OpenLibraries (SAS/C)

```asm
_OpenLibraries:
    MOVEA.L _SysBase, A6

    ; Open dos.library
    LEA     _dosname(PC), A1        ; "dos.library"
    MOVEQ   #0, D0
    JSR     -552(A6)                ; OpenLibrary
    MOVE.L  D0, _DOSBase

    ; (other libraries as needed by pragmas)
    RTS

_dosname:   DC.B    "dos.library", 0
```

### Workbench Message Handling (SAS/C)

```asm
; After main() returns, if Workbench launch:
    MOVEA.L _SysBase, A6
    JSR     -132(A6)                ; Forbid()
    MOVEA.L _WBenchMsg, A1
    JSR     -378(A6)                ; ReplyMsg(_WBenchMsg)
    JSR     -138(A6)                ; Permit() — never actually reached
    RTS
```

> [!IMPORTANT]
> For Workbench launches, `Forbid()` must be called **before** `ReplyMsg()` on the WBStartup message. The Workbench process waits for this reply; if the app exits without replying, the Workbench can crash or hang.

---

## GCC Startup (gcrt0.S / libnix)

GCC's AmigaOS startup is provided by `libnix` (or newer `clib2`):

```asm
/* gcrt0.S — GCC startup */
.text
.globl _start
_start:
    move.l  4.w, a6              /* SysBase */
    jsr     ___startup_SysBase   /* store SysBase, init libnix */

    /* Open dos.library */
    lea     _doslib(pc), a1
    moveq   #0, d0
    jsr     -552(a6)             /* OpenLibrary */
    move.l  d0, _DOSBase

    /* Parse args, set up __argv/__argc */
    jsr     ___parse_args

    /* Call main() */
    jsr     _main

    /* Exit cleanup */
    move.l  d0, -(sp)            /* return value */
    jsr     ___exit

_doslib: .asciz "dos.library"
```

`libnix` provides a more complete C runtime than the minimal SAS/C `c.o`.

---

## Argument Parsing

### CLI Arguments

CLI arguments arrive as a **raw byte string** pointed to by A0, with D0 holding the length. The startup code must:

1. Copy the string (it lives in the caller's stack)
2. Tokenise it into `argc`/`argv` (standard) or pass raw via `RawArg()`

SAS/C standard `argc`/`argv`:
```c
/* _main.c in c.o */
int main(int argc, char *argv[]);

/* startup converts:
   RawCommandStr = "myarg1 myarg2\n"
   → argc = 3, argv = ["progname", "myarg1", "myarg2"] */
```

### Workbench Arguments

For Workbench launches, the WBStartup message carries an array of `WBArg` structures:
```c
struct WBStartup {
    struct Message sm_Message;
    struct MsgPort *sm_Process;   /* WB process port */
    BPTR           sm_Segment;   /* loaded segment */
    LONG           sm_NumArgs;   /* number of args */
    char           *sm_ToolWindow;
    struct WBArg   *sm_ArgList;  /* array of WBArg */
};

struct WBArg {
    BPTR  wa_Lock;    /* directory containing the icon */
    STRPTR wa_Name;   /* filename of the icon */
};
```

---

## Stack Setup

The stack size is specified at link time (SAS/C) or in the Tooltype/CLI:

```
; SAS/C: specify in linker command:
slink  lib/c.o myobj.o TO myexe  STACKSIZE 8192

; At runtime, AmigaDOS CreateProc() passes NP_StackSize
```

The startup code does **not** set up the stack — that is done by `CreateProc()` / the OS task dispatch. The startup can optionally check for stack overflow via `GetCC()` / `CheckStack()`.

---

## Recognising Startup Code in IDA Pro

The startup stub is always at the start of hunk 0. Look for:
```asm
; SAS/C signature:
MOVE.L  $00000004, A6    ; or MOVEA.L 4.W, A6
; followed immediately by MOVE.L A6, _SysBase
```

```asm
; GCC signature (bebbo):
MOVE.L  4.W, A6
JSR     some_init_stub   ; libnix internal
```

After identifying startup, `main()` is the first function BSR/JSR'd after the library opens.

---

## References

- NDK39: `lib/` directory — `c.o`, `c_sm.o` (SAS/C startup variants)
- libnix source: https://github.com/bebbo/libnix
- clib2 source: https://github.com/adozenlines/clib2
- SAS/C 6.x Programmer's Guide — startup code chapter
- *Amiga ROM Kernel Reference Manual: Libraries* — process creation, Workbench startup
