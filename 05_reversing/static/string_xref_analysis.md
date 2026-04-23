[← Home](../../README.md) · [Reverse Engineering](../README.md)

# String Cross-Reference Analysis

## Overview

String references are the fastest entry point into a disassembled Amiga binary. Library name strings, error messages, and format strings immediately reveal program intent and identify OS API usage patterns.

---

## Finding Library Name Strings

Every `OpenLibrary` call is preceded by a string reference. Search for `".library"`:

```bash
# Host: grep for library name strings in binary
strings mybinary | grep -i library
# → "dos.library", "graphics.library", "intuition.library", ...
```

In IDA:
1. `View → Open Subviews → Strings` (Shift+F12)
2. Search for `.library`
3. Press `X` on any result to see all cross-references
4. Each xref leads to a `LEA str(PC), A1` or `MOVE.L #str, A1` before a `JSR -552(A6)` (OpenLibrary)

---

## Tracing OpenLibrary Calls to Their Targets

```asm
; Pattern to find:
LEA     (_str_dos).L, A1      ; "dos.library"
MOVEQ   #36, D0               ; min version
MOVEA.L 4.W, A6               ; exec.library
JSR     (-552,A6)             ; OpenLibrary → D0 = DOSBase
MOVE.L  D0, (_DOSBase).L      ; store for later use
```

Xref `_str_dos` → find this block → identify the stored library base variable → label it `_DOSBase`.

---

## Using HUNK_SYMBOL Names as Seed Labels

If `HUNK_SYMBOL` is present (debug build), IDA auto-applies names. These seed labels help bootstrap analysis:

1. `View → Open Subviews → Names` → look for any `_` prefixed symbols
2. Named functions often call unnamed helpers nearby — work outward
3. String xrefs from named functions propagate names further

---

## Error Message Strings

Error/diagnostic strings reveal program flow:

```asm
; Common pattern:
LEA     _err_nolib(PC), A0     ; "Can't open dos.library"
MOVEA.L _DOSBase, A6
JSR     (-60,A6)               ; Output() → D0 = stdout
MOVE.L  D0, D1
LEA     _err_nolib(PC), A2
MOVE.L  A2, D2
MOVEQ   #_err_nolib_end - _err_nolib, D3
JSR     (-48,A6)               ; Write(stdout, msg, len)
```

The error string tells you exactly what this code path handles.

---

## Format String Xref Analysis (printf)

SAS/C `printf` style calls via `dos.library VPrintf`:

```asm
MOVEA.L  _DOSBase, A6
LEA      _fmt_str(PC), A0      ; "Error: %ld\n"
MOVE.L   A0, D1
MOVE.L   A1, D2                ; varargs array
JSR      (-954,A6)             ; VPrintf()
```

Format strings like `"Error: %ld\n"` or `"Processing: %s"` reveal parameter types and function purpose.

---

## Workbench Title Strings

```asm
; Typical NewScreen/OpenScreen call sequence:
LEA     _screen_title(PC), A0  ; "MyApp v1.0"
MOVE.L  A0, (NewScreen+ns_Title)
```

Screen/window title strings appear in `intuition.library` `OpenScreen` / `OpenWindow` calls and give the product name.

---

## Automated String Map

Build a complete string inventory:

```python
# IDA script: map all string xrefs
for s in idautils.Strings():
    text = str(idc.get_strlit_contents(s.ea, s.length, s.strtype))
    refs = list(idautils.XrefsTo(s.ea))
    if refs:
        for ref in refs:
            func = idc.get_func_name(ref.frm)
            print(f"{s.ea:#x} [{text!r:40s}] ← {func or 'unknown'} @ {ref.frm:#x}")
```

---

## References

- IDA Pro: Strings subview (Shift+F12), Xrefs (X key)
- `static/api_call_identification.md` — resolving library base from string xrefs
- NDK39: `dos/dos.h` — `VPrintf`, `FPrintf`, error code strings
