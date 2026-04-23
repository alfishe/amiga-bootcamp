[← Home](../README.md) · [Linking & Libraries](README.md)

# AmigaLib Static Linking

## Overview

AmigaOS programs are linked against a set of **static libraries** that provide startup code, C runtime stubs, and glue for OS entry points. The linker resolves all external symbols at link time and produces a self-contained HUNK-format executable.

---

## Key Static Libraries (NDK39 / SAS/C)

| Library | Purpose |
|---|---|
| `amiga.lib` | OS stub functions — `OpenLibrary`, `AllocMem`, etc. for non-inline linking |
| `sc.lib` / `c.lib` | SAS/C runtime: `printf`, `malloc`, `strlen`, standard I/O |
| `auto.lib` | Auto-open libraries (`DOSBase`, `SysBase` acquisition) |
| `debug.lib` | `kprintf`, `dprintf` serial debugging stubs |
| `m.lib` | Math library (software floating point) |
| `scm68020.lib` | SAS/C math for 68020 (co-processor stubs) |

For GCC:
| Library | Purpose |
|---|---|
| `libnix` | C runtime for `m68k-amigaos-gcc` — replaces `sc.lib` |
| `libamiga` | OS glue for GCC (NDK-based) |
| `libm` | Soft-float math |
| `libgcc` | GCC internal helpers (division, etc.) |

---

## Startup Object: `c.o` / `_start`

Every AmigaOS C program begins execution at the **first word of segment 0** — not at `main()`. The startup object `c.o` (SAS/C) or `crt0.o` (GCC/libnix) is always linked first and provides:

```asm
;; SAS/C c.o skeleton (simplified)
_start:
    MOVE.L  4.W, A6              ; SysBase from absolute location $4
    MOVE.L  A0, _CommandStr      ; raw CLI argument string (from dos.library)
    MOVE.L  A1, _WBenchMsg       ; WBStartup message (if WB launch, else NULL)
    JSR     __main               ; C runtime init → eventually calls main()
    ; D0 = exit code from main()
    MOVE.L  D0, _rc              ; save return code
    JSR     __exit               ; C runtime cleanup
    RTS                          ; return to dos.library
```

### What `__main` Does

1. Opens `DOSBase` via `OpenLibrary("dos.library", 0)` using SysBase in A6
2. Sets up `stdin`/`stdout`/`stderr` file handles (wraps `dos.library` I/O)
3. Allocates C heap (if any static `malloc`/`new` usage)
4. Initializes `errno`, `_timezone`, `__ProgramName`
5. Calls any registered `__constructor` functions (C++ static init)
6. Calls `main(argc, argv)` — argument string is parsed from `_CommandStr`
7. Calls `exit(return_code)` → runs `atexit()` handlers → `CloseLibrary(DOSBase)`

---

## WBStartup Glue

When launched from Workbench (double-click), `A0 = NULL`, `A1 = WBStartup msg ptr`. The startup code must:

```c
/* standard WB detection in __main / startup */
if (_WBenchMsg) {
    /* We are a WB launch. argc=0, argv=NULL passed to main() */
    /* Must not return until cleanup */
}
```

On exit from a WB-launched program:
```c
Forbid();                          /* prevent task switching during cleanup */
ReplyMsg((struct Message *)_WBenchMsg);  /* unblock Workbench */
/* now safe to RTS / remove task */
```

This pattern is critical: **failing to `ReplyMsg` a WB launch will hang Workbench**.

---

## Stack Cookie

SAS/C startup checks for a stack size cookie in the executable:

```c
/* In your source — sets minimum stack to 8 KB */
LONG __stack = 8192;
```

The linker includes this symbol at a known offset; the OS shell reads it and allocates at least that much stack before launching. IDA Pro will often highlight `_stack` as a data symbol.

---

## CTRL-C Checking

SAS/C runtime polls for CTRL-C via `CheckSignal(SIGBREAKF_CTRL_C)` inside `printf`, `fgets`, and other stdio functions. Programs that do long computation loops should call:

```c
if (SetSignal(0, 0) & SIGBREAKF_CTRL_C)
    cleanup_and_exit();
```

Or use `SAS/C`'s `__chkabort()` hook.

---

## Typical Link Command (SAS/C)

```
slink FROM lib/c.o myobj.o LIB lib/sc.lib lib/amiga.lib TO myprogram
```

Order matters:
1. `lib/c.o` — **must be first** (entry point at start of segment 0)
2. Object files (`myobj.o`, ...)
3. `sc.lib` — C runtime (resolves `printf`, etc.)
4. `amiga.lib` — OS stubs (resolves any non-inlined OS calls)

### Typical GCC Link (bebbo)

```bash
m68k-amigaos-gcc -o myprogram myobj.o -lamiga -lnix -lgcc \
    -Wl,-Map,myprogram.map
```

Linker script places `crt0.o` automatically via `-lnix` startup group.

---

## Library Archive Format

Static libraries (`.lib`) are HUNK_LIB archives — sequences of embedded HUNK_UNIT object files with a HUNK_INDEX for fast symbol lookup:

```
HUNK_LIB
  [HUNK_UNIT: AllocMem.o]
    HUNK_CODE
    HUNK_EXT   (export: _AllocMem)
    HUNK_END
  [HUNK_UNIT: FreeMem.o]
    ...
HUNK_INDEX
  [symbol table: _AllocMem → unit 0, _FreeMem → unit 1, ...]
```

The linker only pulls in units whose exported symbols are referenced — unused code from libraries is **not** linked into the executable (link-time dead-stripping).

---

## Segment Layout in Final Executable

With a typical 3-object, 2-lib link:

```
Segment 0 (code):  c.o startup + all CODE sections merged
Segment 1 (data):  all DATA sections merged
Segment 2 (BSS):   all BSS sections (zero-filled)
```

Most linkers merge same-type sections by default. `slink` supports explicit placement control via `CHIP` / `FAST` keywords.

---

## References

- NDK39: `lib/` — `amiga.lib`, `auto.lib`, `debug.lib`, `c.o`
- SAS/C 6.x Programmer's Reference Manual — linking chapter
- libnix source: https://github.com/bebbo/libnix
- *Amiga ROM Kernel Reference Manual: Libraries* — process startup appendix
