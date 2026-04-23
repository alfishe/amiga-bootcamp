[← Home](../README.md) · [Libraries](README.md)

# expansion.library — Zorro Bus and AutoConfig

## Overview

`expansion.library` handles automatic configuration of Zorro II/III expansion boards. At boot, the OS scans the expansion bus and assigns base addresses to each board based on its AutoConfig ROM.

---

## AutoConfig Sequence

1. Board asserts `CFGIN` to request configuration
2. CPU reads 256-byte config area at `$E80000`
3. Board reports: manufacturer ID, product ID, board size, flags
4. OS assigns a base address via `WriteExpansionByte`
5. Board relocates to assigned address
6. Next board in chain is configured

---

## struct ConfigDev

```c
/* libraries/configvars.h — NDK39 */
struct ConfigDev {
    struct Node      cd_Node;
    UBYTE            cd_Flags;       /* CDF_* flags */
    UBYTE            cd_Pad;
    struct ExpansionRom cd_Rom;      /* AutoConfig ROM data */
    APTR             cd_BoardAddr;   /* assigned base address */
    ULONG            cd_BoardSize;   /* board size in bytes */
    UWORD            cd_SlotAddr;    /* slot address */
    UWORD            cd_SlotSize;
    APTR             cd_Driver;      /* driver bound to this board */
    struct ConfigDev *cd_NextCD;     /* next in chain */
    /* ... */
};

struct ExpansionRom {
    UBYTE  er_Type;          /* board type + size code */
    UBYTE  er_Product;       /* product number */
    UBYTE  er_Flags;
    UBYTE  er_Reserved03;
    UWORD  er_Manufacturer; /* manufacturer ID */
    ULONG  er_SerialNumber;
    UWORD  er_InitDiagVec;  /* boot ROM offset */
    /* ... */
};
```

---

## Finding Expansion Boards

```c
struct Library *ExpansionBase = OpenLibrary("expansion.library", 0);
struct ConfigDev *cd = NULL;

while ((cd = FindConfigDev(cd, 2167, 11))) {
    /* manufacturer=2167 (Individual Computers), product=11 (ACA500plus) */
    Printf("Board at $%08lx, size %lu\n", cd->cd_BoardAddr, cd->cd_BoardSize);
}
```

---

## Common Manufacturer IDs

| ID | Manufacturer |
|---|---|
| 514 | Commodore |
| 2017 | GVP |
| 2167 | Individual Computers |
| 8512 | Phase5 |

---

## References

- NDK39: `libraries/configvars.h`, `libraries/expansion.h`
- ADCD 2.1: expansion.library autodocs
