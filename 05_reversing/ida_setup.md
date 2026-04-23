[← Home](../README.md) · [Reverse Engineering](README.md)

# IDA Pro Setup for Amiga 68k Binaries

## Requirements

| Component | Version / Notes |
|---|---|
| IDA Pro | 7.0+ (7.5+ recommended for Hex-Rays decompiler quality) |
| Processor module | M68k — included in IDA standard install |
| HUNK loader | Included in some IDA builds; community plugin if absent |
| Hex-Rays decompiler | 68k decompiler license required for pseudocode |

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

## Step 8: Hex-Rays Decompiler Tips for 68k

The Hex-Rays 68k decompiler needs type information to produce clean pseudocode:

1. **Set function types** — mark return type and argument registers for library call wrappers
2. **Suppress spurious variables** — many D-register temps appear; use `Collapse variable` or retype
3. **Add `__asm` register hints** for known argument registers

Example — marking a library function prototype:
```c
// In IDA Local Types:
APTR __cdecl AllocMem_wrap(ULONG byteSize, ULONG requirements);
```

Then apply to call sites via `Y` (set type) on the JSR instruction.

---

## References

- IDA Pro 7.x documentation — processor modules, FLIRT
- ida-amiga plugin: https://github.com/wiemerc/ida-amiga
- Ghidra Amiga plugin: https://github.com/lab313ru/ghidra_amiga_ldr
- Ghidra m68k fixer: https://github.com/lab313ru/m68k_fixer
- BartmanAbyss Ghidra Amiga: https://github.com/BartmanAbyss/ghidra-amiga — Amiga HUNK loader + helpers for Ghidra
- IDA Pro m68k extensions: https://github.com/LucienMP/idapro_m68k — GDB step-over, type info
- NDK39: header files for type import
