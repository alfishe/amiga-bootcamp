[← Home](../README.md) · [Reverse Engineering](README.md)

# Ghidra Setup for Amiga 68k Binaries

## Requirements

| Component | Version / Notes |
|---|---|
| Ghidra | 10.x+ or 11.x+ recommended |
| Processor module | M68k — included in Ghidra standard install |
| HUNK loader & Amiga extensions | **ghidra-amiga** by BartmanAbyss |

---

## Step 1: Install the Amiga Extension

Ghidra natively supports the M68000 architecture and includes a powerful decompiler for it, but it does not understand the Amiga OS executable format (HUNK) out of the box. 

1. Download the latest release of `ghidra-amiga` from: https://github.com/BartmanAbyss/ghidra-amiga
2. Open Ghidra.
3. Go to `File → Install Extensions...`
4. Click the green `+` (Add extension) button.
5. Select the downloaded `.zip` file (do not extract it).
6. Restart Ghidra.

This essential extension provides:
- A complete Amiga HUNK format loader.
- Custom chipset register definitions mapped to `$DFF000`.
- OS library LVO (Library Vector Offset) definitions.
- Analyzer scripts specifically for resolving Amiga binaries.

---

## Step 2: Importing and Analyzing

1. Create a new project or open an existing one.
2. Select `File → Import File...` and choose your Amiga executable or library.
3. The format should automatically be detected as `Amiga Executable` (thanks to the extension).
4. Double-click the imported file to open it in the CodeBrowser.
5. When prompted to analyze, click **Yes**.
6. Ensure the `Amiga` analyzers (provided by the extension) are enabled in the analysis options list before hitting Analyze.

---

## Step 3: Decompilation and M68k Specifics

Unlike IDA Pro (which lacks Hex-Rays support for M68k), **Ghidra's built-in decompiler fully supports the Motorola 68000 family.**

- The `ghidra-amiga` extension actively assists the decompiler by automatically annotating library calls (like `exec/AllocMem` or `dos/Open`) when it detects jumps to negative offsets on `A6`.
- The decompiler will translate these `JSR` instructions directly into C pseudocode function calls with the correct parameters, making it vastly superior for analyzing C/C++ compiled Amiga software.

---

## Step 4: Custom Hardware Registers ($DFF000)

The `ghidra-amiga` extension automatically creates memory blocks for Amiga custom chips and CIA registers.

1. Go to `Window → Memory Map`. You will see `custom` ($DFF000), `ciaa` ($BFE001), and `ciab` ($BFD000) accurately mapped into the address space.
2. The extension automatically defines the Amiga Custom Chip data types.
3. When analyzing code that bangs the hardware (e.g., `move.w d0, $096(A4)`), if Ghidra knows `A4` is `$DFF000`, it will automatically format it as `custom->dmacon` in the C pseudocode!
4. If it fails to detect the base register automatically, you can manually set the register value by highlighting the start of the function, right-clicking, and selecting `Set Register Values` (or `Ctrl-R`), then defining `A4 = 0xDFF000`.

---

## Step 5: Dynamic Analysis

Ghidra is purely for **static analysis**. 
For dynamic debugging, the workflow is identical to IDA:
1. Do your mapping and decompilation in Ghidra.
2. Note the physical addresses and offsets.
3. Run the binary in WinUAE and drop into the native debugger (`Shift+F12`) to set breakpoints and step through the hardware state live.

---

## Step 6: GCC Binary Specific Workflows

When dealing with GCC-compiled Amiga binaries (especially those with debug info), there are a few Ghidra-specific workflows to note:

**1. Install `ghidra-gcc2-stabs`** (`RidgeX/ghidra-gcc2-stabs`) if the binary has debug info. After loading:
- Run the script: `Analysis → Run Script → ImportGCC2Stabs.java`
- The script reads `HUNK_DEBUG`, extracts `N_FUN`/`N_SLINE`/`N_LSYM` stabs, and creates function labels, source line annotations, and local variable names automatically.
- Even partial stabs (e.g., `N_SO` + `N_FUN` only) restore function boundaries and names.

**2. PC-relative string handling.** Ghidra's m68k analyzer natively handles `LEA xxx(PC), An` correctly and creates data cross-references. Check the `References` view for `LEA` targets — strings listed there can be viewed and renamed.

**3. Function boundary heuristic.** Ghidra's default analysis finds GCC functions reasonably well. For missed functions:
- Use `Search → For Instruction Patterns` → `MOVEM.L *, -(SP)` (opcode `48E7`) to find all prologues.
- Right-click → `Create Function` at each found address.

**4. Recognizing tail calls.** Ghidra may misidentify `BRA _otherFunc` as a local branch. If Ghidra marks code after a `BRA` as unreachable or creates a new function at the `BRA` target, verify manually: if the `BRA` target is a named function elsewhere in `.text`, it's a tail call — the `BRA` terminates the current function and the target function returns directly to the original caller.

---

## References

- [ghidra-amiga by BartmanAbyss](https://github.com/BartmanAbyss/ghidra-amiga) — The definitive Amiga loader and extension suite for Ghidra.
- [Ghidra Official Website](https://ghidra-sre.org/)
- [vscode-amiga-debug](https://github.com/BartmanAbyss/vscode-amiga-debug) — Excellent extension for source-level Amiga debugging if you are writing modern Amiga patches.
