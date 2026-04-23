[← Home](../README.md) · [Linking & Libraries](README.md)

# AmigaOS Library Structure

## The Library Node

Every AmigaOS library (and device, resource) begins with a `struct Library` at its base address:

```c
/* exec/libraries.h */
struct Library {
    struct Node  lib_Node;       /* +$00: linked list node */
    UBYTE        lib_Flags;      /* +$0E: LIBF_ flags */
    UBYTE        lib_pad;        /* +$0F: (reserved) */
    UWORD        lib_NegSize;    /* +$10: bytes of function table (negative area) */
    UWORD        lib_PosSize;    /* +$12: bytes of struct Library + private data */
    UWORD        lib_Version;    /* +$14: major version */
    UWORD        lib_Revision;   /* +$16: minor revision */
    APTR         lib_IdString;   /* +$18: pointer to ID string */
    ULONG        lib_Sum;        /* +$1C: checksum of the function table */
    UWORD        lib_OpenCnt;    /* +$20: number of current openers */
};
```

`lib_NegSize` is the total byte size of the JMP table (the negative-address area preceding the struct). It equals `num_functions × 6` bytes per JMP instruction.

---

## JMP Table (Negative Offset Area)

The function table is constructed **below** the library base address. Each entry is a 6-byte JMP instruction:

```
Library base - 6:    4E F9 xx xx xx xx   JMP  AbsAddress  (Open)
Library base - 12:   4E F9 xx xx xx xx   JMP  AbsAddress  (Close)
Library base - 18:   4E F9 xx xx xx xx   JMP  AbsAddress  (Expunge)
Library base - 24:   4E F9 xx xx xx xx   JMP  AbsAddress  (Reserved)
Library base - 30:   4E F9 xx xx xx xx   JMP  AbsAddress  (first user function)
Library base - 36:   ...
```

### Standard Functions (Fixed LVOs for All Libraries)

| LVO (offset) | Function |
|---|---|
| -6 | `Open` |
| -12 | `Close` |
| -18 | `Expunge` |
| -24 | `Reserved` (must return 0) |

These four are mandatory for every library. User functions start at LVO -30.

### JMP Encoding

`4E F9 AAAA AAAA` = `JMP.L absolute_address`

To call function at LVO -30:
```asm
MOVEA.L LibBase, A6
JSR     -30(A6)         ; call through JMP table
```

The `JSR -30(A6)` does **not** jump directly to the function — it jumps to the JMP slot, which then jumps to the real function. This indirection is essential for `SetFunction()` patching.

---

## MakeLibrary() — Constructing the Table

`exec.library MakeLibrary()` builds a library:

```c
struct Library *MakeLibrary(
    APTR funcArray,    /* array of function pointers (APTR) or LONG offsets */
    APTR structInit,   /* structure initialiser table (or NULL) */
    ULONG (*initFunc)(), /* init function (or NULL) */
    ULONG dataSize,    /* size of library data area */
    BPTR segList       /* segment list of the library code */
);
```

`funcArray` is a NULL-terminated list of function addresses. `MakeLibrary` allocates the combined negative+positive area and fills in the JMP table.

---

## Library Initialisation

At `MakeNode()` / `MakeLibrary()` time:
1. `AllocMem(lib_NegSize + lib_PosSize, MEMF_PUBLIC | MEMF_CLEAR)`
2. Fill JMP table at negative offsets
3. Initialise `struct Library` fields at positive offsets
4. Set `lib_Sum` to the checksum of the JMP table

At `AddLibrary()`:
1. Library is added to `SysBase->LibList`
2. Future `OpenLibrary()` calls find it by name via `FindName()`

---

## OpenLibrary() Path

```c
struct Library *base = OpenLibrary("mylib.library", MIN_VERSION);
```

Internally:
1. `exec` searches `SysBase->LibList` for a node with `ln_Name == "mylib.library"`
2. If found and version sufficient: calls `LVO_Open` (offset -6) on the library
3. If not found: attempts to load `LIBS:mylib.library` from disk via `LoadSeg()` + `InitResident()`
4. Returns library base pointer, or NULL on failure

---

## ROM Libraries (Kickstart)

Some libraries are **resident** — embedded directly in the Kickstart ROM:
- `exec.library` — always in ROM; base at `$4` in exec exception vector
- `graphics.library`, `intuition.library`, `dos.library` — loaded from ROM on boot

ROM-resident libraries are listed in the **Resident module** list. During boot, `exec` calls `InitResident()` for each module marked as auto-init.

---

## Library Flags

```c
/* lib_Flags bits: */
#define LIBF_SUMMING   (1<<0)   /* currently computing checksum */
#define LIBF_CHANGED   (1<<1)   /* function table was patched (SetFunction) */
#define LIBF_SUMUSED   (1<<2)   /* checksum is valid */
#define LIBF_DELEXP    (1<<3)   /* delayed expunge requested */
```

`LIBF_CHANGED` is set by `SetFunction()` to signal that the checksum is no longer valid — tools like `ShowConfig` use this to detect patched libraries.

---

## References

- NDK39: `exec/libraries.h`, `exec/nodes.h`
- ADCD 2.1 Autodocs: exec — OpenLibrary, MakeLibrary, AddLibrary, SetFunction
- *Amiga ROM Kernel Reference Manual: Libraries* — library architecture chapter
- http://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node0002.html
