[← Home](../README.md) · [Reverse Engineering](README.md)

# Patching Techniques for Amiga Binaries

## Overview

This document covers the methods used to surgically patch AmigaOS HUNK executables and libraries — without access to source code. All techniques operate on the binary file directly.

---

## Method 1: NOP Patching

Replace one or more instructions with `NOP` ($4E71) to eliminate a code path:

```python
# Python: NOP out 6 bytes at offset $1234
import struct

with open("target.library", "r+b") as f:
    f.seek(0x1234)
    f.write(b'\x4e\x71' * 3)   # 3× NOP = 6 bytes
```

**Use case:** Disable a conditional check:
```asm
; Before: jumps to expiry code if timer > limit
CMPI.L  #$12345678, D3
BHI.S   .expired

; After: NOP the BHI (2 bytes)
CMPI.L  #$12345678, D3
NOP
NOP
```

---

## Method 2: Branch Inversion

Flip the condition of a branch instruction to always take / never take a path:

| Original | Patched | Effect |
|---|---|---|
| `BEQ $4E43` | `BRA $4E43` | Always branch (was: branch if equal) |
| `BNE $4E43` | `BRA $4E43` | Always branch (was: branch if not equal) |
| `BEQ $4E43` | `NOP`×2 | Never branch (was: branch if equal) |
| `BHI $4E43` | `BLS $4E43` | Invert condition |

Branch instruction bytes:
```
67 xx   BEQ.S (offset xx)
66 xx   BNE.S
6E xx   BGT.S
6F xx   BLE.S
60 xx   BRA.S
```

Change `BEQ.S` to `BRA.S`: replace first byte `$67` with `$60`.

---

## Method 3: Return Value Forcing

Force a function to always return a specific value:

```asm
; Original: complex check, returns 0 on failure
_CheckTimer:
    LINK    A5, #-4
    ...                   ; timer logic
    UNLK    A5
    RTS

; Patched: always return 1 (success/valid)
_CheckTimer:
    MOVEQ   #1, D0        ; $7001 — MOVEQ #1, D0 (2 bytes)
    RTS                   ; $4E75 (2 bytes)
```

`MOVEQ #1, D0` = `$70 $01` (2 bytes)
`RTS`          = `$4E $75` (2 bytes)

Write 4 bytes at the function entry point.

---

## Method 4: JMP Redirect

Redirect a function call to a completely different address:

```asm
; Original call:
JSR     _CheckAuth          ; $4EB9 XXXXXXXX

; Patched to call our stub instead:
JSR     _AlwaysTrue         ; $4EB9 YYYYYYYY
```

Requires updating the relocation table if the new address is in a different hunk — simpler if both are in the same hunk (no reloc change needed).

---

## Method 5: Constant Replacement

Replace a comparison constant (timer limit, version check value, etc.):

```asm
; Original: 10 retry limit
CMPI.L  #$0000000A, D3     ; $0A = 10

; Patched: effectively unlimited retries
CMPI.L  #$7FFFFFFF, D3     ; max positive longword
```

Find the constant in the binary: `xxd target.library | grep "00 00 00 0a"`
Replace with new value at that offset.

---

## Method 6: Library JMP Table Patch (Runtime)

For patching a library's JMP table at runtime (not file-level):

```asm
; Install patch at LVO -30 of DOSBase:
MOVEA.L _DOSBase, A0        ; library base
MOVE.L  #_MyOpen, -28(A0)  ; overwrite address bytes of JMP.L at -30
                             ; JMP.L = 4E F9 [AAAAAAAA]
                             ; address is at offset -30+2 = -28
```

Note: this does not use `SetFunction()` — no `LIBF_CHANGED` flag. Used when you need silent patching.

---

## Updating Relocations After Patching

If a patched longword is in the HUNK_RELOC32 list, the loader will overwrite your patch at load time by adding the hunk base to it. You must either:

1. **Remove the reloc entry** for that offset from `HUNK_RELOC32`
2. **Adjust the stored value** so that after relocation it becomes the desired value

**Finding reloc entries to remove:**

```python
def remove_reloc_entry(data, hunk_offset, target_offset):
    """Remove a specific offset from HUNK_RELOC32 records."""
    # Parse the file, find HUNK_RELOC32, remove the entry
    # This requires a full HUNK parser — see hunk_parser.py
    pass
```

---

## Automated Patcher Template (Python)

```python
#!/usr/bin/env python3
"""
Amiga HUNK Binary Patcher
"""
import struct
import shutil
import sys

class AmigaPatcher:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.data = bytearray(f.read())
        self.path = path

    def find_pattern(self, pattern: bytes) -> list:
        """Find all occurrences of a byte pattern."""
        results = []
        idx = 0
        while True:
            idx = self.data.find(pattern, idx)
            if idx == -1:
                break
            results.append(idx)
            idx += 1
        return results

    def patch_bytes(self, offset: int, new_bytes: bytes, comment: str = ""):
        old = self.data[offset:offset+len(new_bytes)]
        print(f"[PATCH] {comment}")
        print(f"  Offset: {offset:#010x}")
        print(f"  Old: {old.hex()}")
        print(f"  New: {new_bytes.hex()}")
        self.data[offset:offset+len(new_bytes)] = new_bytes

    def nop(self, offset: int, count: int, comment: str = ""):
        self.patch_bytes(offset, b'\x4e\x71' * count, f"NOP×{count}: {comment}")

    def save(self, out_path: str):
        with open(out_path, 'wb') as f:
            f.write(self.data)
        print(f"[SAVE] Written to {out_path}")

# Example usage:
if __name__ == "__main__":
    p = AmigaPatcher("target.library")

    # Patch 1: NOP out redundant range check
    p.nop(0x1234, 3, "skip bounds validation BHI branch")

    # Patch 2: Force version check to pass
    p.patch_bytes(0x5678, bytes([0x70, 0x01, 0x4E, 0x75]),
                  "always return 1 from CheckVersion")

    p.save("target_patched.library")
```

---

## Verification After Patching

1. **Checksum update**: Some libraries check `SumLibrary()` at init — may need to disable that check too
2. **Test on hardware**: Use the MiSTer or UAE emulator to verify the patched binary
3. **Regression test**: Ensure patched functions that are chained still work correctly

---

## References

- [setfunction.md](../04_linking_and_libraries/setfunction.md) — runtime patching
- [hunk_relocation.md](../03_loader_and_exec_format/hunk_relocation.md) — relocation interaction
- [case_studies/ramdrive_device.md](case_studies/ramdrive_device.md) — complete real-world example
