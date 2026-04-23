[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Reconstructing Library JMP Tables

## Overview

Every AmigaOS library has a **JMP table** at negative offsets from its base pointer. Reconstructing this table maps LVOs to function names and is essential for identifying all OS calls made by a binary under analysis.

---

## JMP Table Layout

```
lib_base - N*6:  JFF xxxx xxxx   ; JMP to function N (6 bytes)
...
lib_base - 24:   JMP Reserved()
lib_base - 18:   JMP Expunge()
lib_base - 12:   JMP Close()
lib_base -  6:   JMP Open()
lib_base + 0:    struct Library  ; lib_Node, lib_Version, ...
```

Each entry is a 68k `JMP (abs.l)` — opcode `4EF9` followed by a 4-byte absolute address, totalling 6 bytes. Hence LVO = `−6 × slot_index`.

---

## Finding the Library Base

### From SysBase LibList

The `exec.library` maintains a doubly-linked list at `SysBase→LibList`:

```c
struct ExecBase {
    ...
    struct List LibList;  /* offset +378 — list of open libraries */
    ...
};

/* Walk the list: */
struct Node *n = SysBase->LibList.lh_Head;
while (n->ln_Succ) {
    struct Library *lib = (struct Library *)n;
    printf("%s v%d\n", lib->lib_Node.ln_Name, lib->lib_Version);
    n = n->ln_Succ;
}
```

### In IDA Pro

After loading, `SysBase` is at `$4`. Use `Edit → Segments → Create Segment` pointed at `$4` with type `WORD` to follow the pointer to `ExecBase`. Then navigate to `LibList` at offset `+0x17A` and walk the linked list.

---

## Reading the JMP Table in IDA

1. Know the library base address (e.g., `DOSBase` from the `OpenLibrary` result)
2. Navigate to `lib_base - 6` — first user function slot
3. IDA shows `JMP sub_XXXXXX` — the target is the actual function implementation
4. Rename each `sub_` with the function name from the LVO table

### Automated Script: `apply_lvo_names.py`

```python
import idaapi, idc

LVO_DOS = {
    -30: "Open",      # LVO -30 = Open(name, mode) d1/d2
    -36: "Close",
    -42: "Read",
    -48: "Write",
    -54: "Input",
    -60: "Output",
    -126: "WaitForChar",
    -138: "Delay",
    # ... extend from dos_lib.fd
}

DOS_BASE = idc.get_name_ea_simple("_DOSBase")
dos_ptr  = idc.get_wide_dword(DOS_BASE)

for lvo, name in LVO_DOS.items():
    jmp_entry = dos_ptr + lvo
    # read the JMP target: opcode at jmp_entry is 4EF9, target at +2
    target = idc.get_wide_dword(jmp_entry + 2)
    idc.set_name(target, f"dos_{name}", idaapi.SN_NOWARN)
    print(f"LVO {lvo:+d}: {name} → {target:#010x}")
```

---

## Mapping LVO → Function via `.fd` Files

NDK39 `.fd` files define the exact register assignments and bias (LVO offset):

```
## NDK39/fd/dos_lib.fd (excerpt)
##base _DOSBase
##bias 30
##public
Open(name,accessMode)(d1,d2)
##bias 36
Close(file)(d1)
##bias 42
Read(file,buffer,length)(d1,d2,d3)
##bias 48
Write(file,buffer,length)(d1,d2,d3)
```

The `##bias` value **is** the positive LVO — the actual call offset is `−bias`.

---

## JSR −LVO(A6) Pattern in Disassembly

```asm
; Typical OS call site in disassembly:
MOVEA.L  (_DOSBase).L, A6
JSR      (-30,A6)          ; Open(d1=name, d2=mode)
; D0 = file handle (BPTR) or 0 on error
```

In IDA, this appears as `jsr ($fffffffe2,a6)` with displacement `-30` (`$FFFFFFE2` in two's complement 16-bit). Applying LVO names makes this `jsr (Open,a6)`.

---

## Common Library Bases and LVO Tables

See [`../../../04_linking_and_libraries/lvo_table.md`](../../../04_linking_and_libraries/lvo_table.md) for complete LVO offset tables for:
- `exec.library`
- `dos.library`
- `graphics.library`
- `intuition.library`

---

## References

- NDK39: `fd/` directory — all library `.fd` files
- `04_linking_and_libraries/lvo_table.md`
- ADCD 2.1: `Libraries_Manual_guide/`
- IDA Pro scripting: `idc.py` reference
