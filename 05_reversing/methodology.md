[← Home](../README.md) · [Reverse Engineering](README.md)

# RE Methodology — AmigaOS HUNK Binaries

## Phase 1: Initial Triage

### 1.1 Identify the File Type

```bash
xxd target.library | head -4
```

| First 4 bytes | Type |
|---|---|
| `00 00 03 F3` | Executable (HUNK_HEADER) |
| `00 00 03 E7` | Object file (HUNK_UNIT) |
| `70 FF 60 FA` | Resident tag (RomTag) |

### 1.2 Dump HUNK Structure

```bash
hunkinfo target.library
```

Expected output:
```
Hunk 0: CODE  size=$1234  offset=$00012000
Hunk 1: DATA  size=$0200  offset=$00013240
Hunk 2: BSS   size=$0400
Symbols: 45
Relocs:  127
```

### 1.3 Verify Library Header

For a `.library` file, hunk 0 should start with a `RomTag` (resident module tag):

```
$4AFC    ; RT_MATCHWORD (hex: MOVEQ #0, D0 in context)
```

Real `RomTag` starts at word `$4AFC`:
```asm
_romtag:
    DC.W    RTC_MATCHWORD       ; $4AFC
    DC.L    _romtag             ; RT_MATCHTAG (self-pointer)
    DC.L    _endskip            ; RT_ENDSKIP
    DC.B    RTF_AUTOINIT        ; RT_FLAGS
    DC.B    VERSION             ; RT_VERSION
    DC.B    NT_LIBRARY          ; RT_TYPE
    DC.B    PRIORITY            ; RT_PRI
    DC.L    _libname            ; RT_NAME
    DC.L    _idstring           ; RT_IDSTRING
    DC.L    _inittable          ; RT_INIT (or function)
```

---

## Phase 2: Load in IDA Pro

### 2.1 Load the File

File → New → select the binary → select "Amiga HUNK" format (or m68k raw if plugin not available).

If using the HUNK plugin:
- Hunks are mapped to segments: `CODE0`, `DATA0`, `BSS0`, etc.
- HUNK_SYMBOL entries become IDA names automatically
- HUNK_RELOC32 become IDA fixups

> [!NOTE]
> **Alternative: Native Disassemblers**
> If you are working directly on an Amiga or via emulation (WinUAE), native tools are highly effective:
> - **Interactive Disassemblers**: *ReSource* allows for interactive tracing and is well-aware of AmigaOS structures.
> - **Command-line Disassemblers**: *IRA* (Interactive Reassembler) is excellent for generating re-assemblable source code from HUNK binaries.
> - **Assembler Environments**: *AsmOne* provides a fully integrated debugging, disassembling, and patching environment.

### 2.2 Set Processor

`Options → General → Processor type = Motorola 680x0`

For A1200/A4000 targets, enable `68020` or `68040` instruction sets.

### 2.3 Apply Library Type Information

Load the AmigaOS TIL (Type Information Library) if available:
- `File → Load file → FLIRT signature file` — use Amiga-specific FLIRT sigs
- Or manually: `View → Open Subviews → Type Libraries` → load `amigaos.til`

---

## Phase 3: Locate the Library Base

For a `.library` file, the library base is created by `MakeLibrary()` at runtime. In the static binary, look for:

```asm
; InitTable for the library:
DC.L  _libsize         ; LIB_POSSIZE (struct size)
DC.L  _funcTable       ; function array pointer
DC.L  _dataTable       ; data init table (or NULL)
DC.L  _initCode        ; init function
```

The function table is an array of absolute function pointers terminated by `-1`:
```asm
_funcTable:
    DC.L  _Open
    DC.L  _Close
    DC.L  _Expunge
    DC.L  _Reserved
    DC.L  _MyFunc1
    DC.L  _MyFunc2
    ...
    DC.L  -1           ; terminator
```

This is the easiest way to find all library functions from the static binary.

---

## Phase 4: Identify Calling Conventions

### 4.1 Find Library Calls

Search for the pattern `JSR -N(A6)` or `JSR -N(A5)` (some code uses A5):

In IDA, search for instruction text: `jsr -`

Each hit is a library call. The register `A6` (or A5) holds the library base at that point.

### 4.2 Trace Library Base

Trace backwards from the JSR to find where A6 was loaded:

```asm
MOVEA.L _DOSBase, A6     ; most common: global variable
JSR     -48(A6)          ; Write

MOVEA.L D0, A6           ; from return value of OpenLibrary
JSR     -30(A6)          ; Open

MOVEA.L 4.W, A6          ; SysBase directly
JSR     -198(A6)         ; AllocMem
```

### 4.3 Resolve the LVO

```python
# IDA Python: resolve a JSR -N(A6) to a function name
def resolve_lvo(ea):
    insn = idc.print_insn_mnem(ea)
    if insn not in ('jsr', 'JSR'):
        return
    op = idc.print_operand(ea, 0)
    # op looks like "-48(A6)" or "-552(a6)"
    import re
    m = re.match(r'(-?\d+)\(A6\)', op, re.IGNORECASE)
    if m:
        lvo = int(m.group(1))
        # Look up in your LVO table
        name = LVO_TABLE.get(lvo, f"unknown_lvo_{-lvo}")
        idc.set_cmt(ea, f"→ {name} LVO={lvo}", 0)
```

---

## Phase 5: Annotate and Name

### 5.1 Apply Library Function Names

Using the LVO tables from [lvo_table.md](../04_linking_and_libraries/lvo_table.md), annotate each JSR:

```python
# IDA script: annotate all JSR -N(A6) calls in exec context
import idautils, idc, idaapi

EXEC_LVOS = {
    -198: "AllocMem",
    -210: "FreeMem",
    -282: "AddTask",
    -552: "OpenLibrary",
    # ... (full table from lvo_table.md)
}

for ea in idautils.CodeRefsTo(idc.get_name_ea_simple("_SysBase"), 0):
    # For each reference to SysBase load, find subsequent JSR
    pass  # implement full trace
```

### 5.2 Name Functions

After resolving all library calls in a function, it becomes clear what the function does. Apply a meaningful name:

```
IDA: Press N on a function → rename to descriptive identifier
```

### 5.3 Define Structures

Apply AmigaOS structure types:
- `View → Open Subviews → Local Types` → import from AmigaOS headers
- Or manually define: `ExecBase`, `DosLibrary`, `MsgPort`, etc.

---

## Phase 6: Patch Analysis

Look for evidence of `SetFunction` patching:
1. JMP table entries pointing outside the library code segment
2. `LIBF_CHANGED` bit set in `lib_Flags`
3. Functions that immediately JSR to a stored old-function address

Look for timer/protection mechanisms:
1. Calls to `dos.library CurrentTime()` or `timer.device`
2. CIA timer reads (`$BFDE00` area)
3. Comparison of tick counts with a threshold

---

## Limitations: The Decompilation Problem

While decompilation (generating C/C++ source code from assembly) is a common modern RE workflow via Hex-Rays or Ghidra, the Amiga ecosystem presents severe challenges for decompilation:

- **Heavy reliance on hand-written assembly**: Many Amiga games and demos eschewed C compilers entirely. Decompiling highly optimized 68000 assembly that uses custom chip registers directly into C yields poor, unreadable results.
- **Custom Calling Conventions**: Unlike modern standard ABIs (e.g., cdecl, fastcall), Amiga software frequently used register-based arguments (e.g., D0-D1 for data, A0-A1 for pointers) tailored to specific routines.

> [!NOTE]
> **Historical Context**
> Straightforward decompilation of Amiga games is largely a myth. Successful "decompilation" projects, such as Tom Morton's *GLFrontier* (a port of the Atari ST/Amiga game *Frontier*), rely heavily on custom-built decompilation solutions tailored precisely to the game's specific binary patterns, rather than generic tools.

---

## References

- [ida_setup.md](ida_setup.md) — IDA configuration details
- [compiler_fingerprints.md](compiler_fingerprints.md) — compiler identification
- [lvo_table.md](../04_linking_and_libraries/lvo_table.md) — complete LVO tables
- [code_vs_data_disambiguation.md](static/code_vs_data_disambiguation.md) — distinguishing code bytes from data
- NDK39: all `.fd` and `include/` files
