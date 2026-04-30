[← Home](../README.md) · [Reverse Engineering](README.md)

# IDA Pro Setup for Amiga 68k Binaries

## Requirements

| Component | Version / Notes |
|---|---|
| IDA Pro | 7.0+ (provides standard M68k disassembly, no Hex-Rays support) |
| Processor module | M68k — included in IDA standard install |
| HUNK loader | Included in some IDA builds; community plugin if absent |

---

## Step 1: Install the HUNK Loader Plugin

IDA does not ship with an Amiga HUNK loader in all versions. The community loader is available at:

- https://github.com/wiemerc/ida-amiga (Python-based, IDA 7.x)
- Alternative: load as raw binary at base address 0, then manually define hunk segments

### Installing the plugin:

```bash
cp amiga_hunk.py ~/.idapro/plugins/        # macOS/Linux
cp amiga_hunk.py %APPDATA%\Hex-Rays\IDA Pro\plugins\   # Windows
```

Restart IDA. The loader appears in the format list when opening `.library`, `.device`, or executables with `$3F3` magic.

---

## Step 2: Processor Configuration

When loading, select:
- **Processor**: Motorola 680x0
- **Variant**: 68020 for A1200/A4000 targets, 68000 for A500 targets
- **Endianness**: Big-endian (automatic for 68k)

Changing processor after load:
`Edit → Plugins → Change processor type`

---

## Step 3: Segment Setup (Manual Load Fallback)

If not using the HUNK plugin, define segments manually after loading as raw binary:

```python
# IDA Python: create segments for a 2-hunk binary
# (code at 0, data at 0x1234)
import idc, idaapi

CODE_BASE = 0x00000000
DATA_BASE = 0x00001234

idc.add_segm(0, CODE_BASE, CODE_BASE + 0x1230, "CODE", "CODE")
idc.add_segm(0, DATA_BASE, DATA_BASE + 0x200,  "DATA", "DATA")
idc.set_segm_class(idc.get_segm_attr(CODE_BASE, idc.SEGATTR_SEL), "CODE")
```

---

## Step 4: Define SysBase and Library Bases

Tell IDA about global library pointers so it can track A6:

```python
# Mark $00000004 as SysBase (exec pointer)
idc.create_dword(4)
idc.set_name(4, "SysBase", idc.SN_NOWARN)
idc.set_cmt(4, "exec.library base pointer (absolute address 4)", 0)
```

For each library base found during analysis:
```python
idc.set_name(ea_of_libbase_var, "_DOSBase", idc.SN_NOWARN)
```

---

## Step 5: Apply FLIRT Signatures

FLIRT (Fast Library Identification and Recognition Technology) signatures identify known library startup and runtime functions. Amiga-specific signature files:

- `m68k_amiga_sasc6.sig` — SAS/C 6.x standard library
- `m68k_amiga_gcc_libnix.sig` — GCC libnix
- `m68k_amiga_vbcc.sig` — VBCC

Apply via: `File → Load file → FLIRT signature file`

If no prebuilt sigs are available, create them with IDA's PELF tool from known `.lib` files.

---

## Step 6: Import AmigaOS Types

Apply AmigaOS structure definitions:

### Option A: Type Library (.til)

If an AmigaOS `.til` is available:
```
View → Open Subviews → Type Libraries → Insert → select amigaos.til
```

### Option B: Parse Headers Directly

```
File → Load file → Parse C header file
```

Load NDK39 headers (adjust path to your NDK location):
```
NDK39/include/exec/execbase.h
NDK39/include/dos/dosextens.h
NDK39/include/graphics/gfxbase.h
```

Set pre-processor defines:
```c
#define __AMIGA__
#define __mc68000__
```

---

## Step 7: Annotate JMP Table Calls

Run the LVO annotation script:

```python
import idautils, idc, idaapi, re

# Build LVO→name dict from NDK fd files (partial)
EXEC_LVO = {
    -198: "AllocMem",   -210: "FreeMem",
    -282: "AddTask",    -288: "RemTask",
    -366: "PutMsg",     -372: "GetMsg",
    -552: "OpenLibrary",-414: "CloseLibrary",
    -420: "SetFunction",-624: "CopyMem",
    # ... extend from lvo_table.md
}

def annotate_lvos():
    for seg_ea in idautils.Segments():
        for func_ea in idautils.Functions(seg_ea, idc.get_segm_end(seg_ea)):
            for ea in idautils.FuncItems(func_ea):
                if idc.print_insn_mnem(ea).lower() == 'jsr':
                    op = idc.print_operand(ea, 0)
                    m = re.match(r'(-\d+)\(A6\)', op, re.IGNORECASE)
                    if m:
                        lvo = int(m.group(1))
                        name = EXEC_LVO.get(lvo)
                        if name:
                            idc.set_cmt(ea, f"exec: {name}", 0)

annotate_lvos()
```

---

## Step 8: Mapping Custom Hardware Registers

When reversing games or hardware-banging software, you will frequently encounter direct accesses to `$DFF000` (Custom Chips), `$BFE001` (CIAA), and `$BFD000` (CIAB).

To make these readable in IDA:
1. Ensure the Amiga NDK headers are loaded (from Step 6).
2. Go to the `Structures` tab and ensure the `Custom` structure (from `hardware/custom.h`) is defined.
3. Jump to address `$DFF000` in the IDA view (you may need to create a dummy data segment at `$DFF000` if one doesn't exist).
4. Apply the `Custom` struct format to the data at `$DFF000` (using `Alt+Q`).
5. When you see an instruction like `MOVE.W D0, $096(A4)` where you know `A4` points to `$DFF000`, press `T` (Struct offset) to map it to the human-readable `dmacon` register.

> [!TIP]
> **Automating with IDAPython:** Instead of mapping structures manually, you can use the Python scripts included in this repository to bulk-define all custom chip and CIA registers specific to your target Amiga model.
> 
> Choose the script matching your target chipset:
> - **[`scripts/ida9_amiga_ocs.py`](scripts/ida9_amiga_ocs.py)** (A1000, A500, A2000)
> - **[`scripts/ida9_amiga_ecs.py`](scripts/ida9_amiga_ecs.py)** (A500+, A600, A3000)
> - **[`scripts/ida9_amiga_aga.py`](scripts/ida9_amiga_aga.py)** (A1200, A4000, CD32)
> 
> Simply load your binary in IDA 9.x, go to `File > Script file...` (or `Alt-F7`), and select the script. It will automatically create the `HW_CUSTOM`, `HW_CIAA`, and `HW_CIAB` segments, format the data types, and apply the physical register names. This makes hardware accesses immediately readable (e.g., `MOVE.W D0, $DFF096` becomes `MOVE.W D0, DMACON`). Using the correct chipset script ensures you quickly spot if an OCS game accidentally accesses an AGA-only register!
---

## Step 9: Dynamic Analysis Workflow

IDA Pro is primarily used for **static analysis** in standard Amiga workflows. Do not attempt to use IDA's Remote GDB debugger out-of-the-box, as standard WinUAE does not contain a GDB stub.

**The Golden Amiga Reversing Workflow:**
1. Use **IDA Pro** to build the map: label variables, identify routines, and find the target logic (e.g., the copy protection check).
2. Note the physical offset of the instruction in the binary (or its relative location to a known signature).
3. Run the software in **WinUAE**.
4. Press `Shift+F12` to drop into the **WinUAE native debugger**.
5. Set breakpoints (`f <address>`) based on your findings in IDA.
6. Step through the live hardware state natively in WinUAE, where all custom chip registers and DMA timings are perfectly emulated.

---

## Step 10: Patching Workflows

IDA's internal 68k assembler is notoriously finicky for generating inline patches directly in the database. If you need to neutralize a check (e.g., changing a `BNE` to `NOP`s):

1. **Live Testing:** In the WinUAE debugger, use the `a <address>` command to assemble new instructions live in memory, or `w <address> <value>` to write hex bytes directly. Test the patch live before committing it to disk.
2. **Permanent Patching:** Once the offset and replacement bytes are confirmed, use a dedicated hex editor (like HxD or ImHex) on the actual executable file on disk, or write a small Python patcher script to seek and write the bytes.
3. **Advanced Payload Patching:** For large patches that don't fit inline, use `vasm` to assemble a payload block, append it to a new HUNK or overwrite dead code, and redirect the execution flow via a `JMP`.

---

## Step 11: Decompilation Alternatives (Ghidra)

> [!WARNING]
> **Hex-Rays Does Not Support M68k.** The official Hex-Rays decompiler *does not* natively support the Motorola 68000 architecture. IDA Pro will provide world-class disassembly, debugging, and cross-referencing for Amiga binaries, but it **cannot** generate C pseudocode for them.

If C pseudocode generation is a strict requirement for your workflow, you must use **Ghidra**:
1. Ghidra officially supports the 68000 architecture for both disassembly and its integrated decompiler.
2. Use the **[ghidra-amiga](https://github.com/BartmanAbyss/ghidra-amiga)** plugin by BartmanAbyss, which provides a robust HUNK loader, Amiga custom chipset register mappings, and OS library base tracking specifically designed for the Ghidra decompiler engine.

---

## Step 12: GCC Binary Specific Workflows

When analyzing a binary compiled with GCC (often identified by a `.text` hunk or a `LINK A6` in the first function), the standard analysis workflow changes slightly:

**1. Handle `.text` as mixed code+data.** GCC embeds strings and jump tables directly in the code hunk. After auto-analysis:
- Search for `LEA xxx(PC), An` instructions (Edit → Find → by instruction mnemonic or IDAPython)
- For each, check if the target address contains ASCII bytes — if yes, press `A` to define as string
- Mark the string as `DATA` type so IDA doesn't try to disassemble it as code

**2. Function boundary detection without LINK.** IDA's auto-analysis finds most functions via call-graph tracing from the entry point. For stragglers:
- Every `BSR addr` / `JSR addr` target is a function entry — use `Create function` (P key) at those addresses
- Look for `MOVEM.L Dn/An, -(SP)` at addresses following a `RTS` — strong function-start indicator
- Use IDAPython to scan: `for ea in idautils.Heads(): if idc.print_insn_mnem(ea) == 'MOVEM.L': ...`

**3. Identify `main()` in stripped builds.** The libnix startup sequence is fixed:
```
Entry → MOVEA.L 4.W, A6 → JSR __startup_SysBase → (open dos.library) → JSR _main
```
The `JSR` immediately after the `dos.library` open is `_main`. Mark it as a function and rename.

---

## References

- IDA Pro 7.x documentation — processor modules, FLIRT
- ida-amiga plugin: https://github.com/wiemerc/ida-amiga
- Ghidra Amiga plugin: https://github.com/lab313ru/ghidra_amiga_ldr
- Ghidra m68k fixer: https://github.com/lab313ru/m68k_fixer
- BartmanAbyss Ghidra Amiga: https://github.com/BartmanAbyss/ghidra-amiga — Amiga HUNK loader + helpers for Ghidra
- IDA Pro m68k extensions: https://github.com/LucienMP/idapro_m68k — GDB step-over, type info
- NDK39: header files for type import
