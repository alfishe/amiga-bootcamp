[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Case Study — ramdrive.device Structure Analysis

## Overview

`ramdrive.device` is the Amiga's built-in RAM disk device. It provides a RAM-based disk drive (`RAD:`) that can survive a warm reboot (Ctrl-Amiga-Amiga). This makes it an excellent target for reverse engineering to understand **Resident Modules**, **Exec Device Architecture**, and **Memory Survival** techniques.

Analysing it teaches:
- Exec device initialization and the `Resident` structure.
- `BeginIO` dispatch logic.
- Persistence mechanisms across system resets.

---

## Resident Structure (`ROMTag`)

Like all Amiga libraries and devices, `ramdrive.device` starts with a `struct Resident` (defined in `exec/resident.h`):

```c
struct Resident {
    UWORD rt_MatchWord;    /* $4AFC (RTC_MATCHWORD) */
    struct Resident *rt_MatchTag; /* Pointer to self */
    APTR  rt_EndSkip;      /* Pointer to end of module */
    UBYTE rt_Flags;        /* RTF_AFTERDOS | RTF_COLDBOOT */
    UBYTE rt_Version;      /* Version of module */
    UBYTE rt_Type;         /* NT_DEVICE */
    BYTE  rt_Pri;          /* Priority */
    char *rt_Name;         /* "ramdrive.device" */
    char *rt_IdString;     /* ID string */
    APTR  rt_Init;         /* Pointer to Init routine */
};
```

### Reset Survival Mechanism

The primary challenge for `ramdrive.device` is ensuring its memory is not reclaimed by the system after a reset.

1.  **Memory Allocation**: When first initialized, it allocates a large block for disk data.
2.  **Validation**: It writes a "magic cookie" and a checksum at the start of this block.
3.  **Resident List**: It adds its own `ROMTag` to the `ExecBase->ResModules` list.
4.  **Warm Reboot**: On a reset, the Exec loader scans memory for `RTC_MATCHWORD` ($4AFC). When it finds the `ramdrive.device` tag, it checks the block's checksum.
5.  **Re-binding**: If valid, the device re-binds the existing data block instead of allocating a new one.

---

## Locating ramdrive.device in ROM

```bash
# Find the resident tag in Kickstart ROM dump:
python3 - <<'EOF'
import struct, sys

rom = open("kick31.rom", "rb").read()
for i in range(0, len(rom)-4, 2):
    tag = struct.unpack_from(">H", rom, i)[0]
    if tag == 0x4AFC:   # RomTag magic
        rt_matchword = struct.unpack_from(">H", rom, i)[0]
        rt_matchtag  = struct.unpack_from(">I", rom, i+2)[0]
        rt_name      = struct.unpack_from(">I", rom, i+14)[0]
        # Offset lookup for "ramdrive.device" string
        print(f"RomTag @ ROM+{i:#x}")
EOF
```

---

## Device Structure Layout

`ramdrive.device` extends `struct Device` (which extends `struct Library`):

```c
struct RAMDriveBase {
    struct Device  rd_Device;    /* standard device base */
    /* private fields follow */
    APTR           rd_RAMStart;  /* pointer to allocated RAM block */
    ULONG          rd_RAMSize;   /* total size */
    ULONG          rd_BlockSize; /* always 512 */
    ULONG          rd_NumBlocks; /* RAMSize / BlockSize */
    struct MinList rd_Units;     /* list of open units */
};
```

---

## Standard Device Vectors (LVO)

| Offset | Vector | Description |
|---|---|---|
| −6 | `Open` | Open a unit (unit number in io_Unit) |
| −12 | `Close` | Close unit, decrement open count |
| −18 | `Expunge` | Unload if no users |
| −24 | `Reserved` | NULL |
| −30 | `BeginIO` | Queue or execute an IORequest |
| −36 | `AbortIO` | Cancel pending IORequest |

---

## IORequest Command Handling

`BeginIO` is the heart of the driver. It dispatches on `io_Command`:

```c
void BeginIO(struct IORequest *ior) {
    struct IOStdReq *io = (struct IOStdReq *)ior;
    switch (io->io_Command) {
        case CMD_READ:    rd_Read(io);   break;
        case CMD_WRITE:   rd_Write(io);  break;
        case CMD_CLEAR:   rd_Clear(io);  break;
        case TD_FORMAT:   rd_Format(io); break;
        case TD_GETGEOMETRY: rd_Geometry(io); break;
        default:
            io->io_Error = IOERR_NOCMD;
            ReplyMsg(&io->io_Message);
    }
}
```

### `CMD_READ` Implementation

```c
void rd_Read(struct IOStdReq *io) {
    UBYTE *src = rdbase->rd_RAMStart + io->io_Offset;
    CopyMem(src, io->io_Data, io->io_Length);
    io->io_Actual = io->io_Length;
    io->io_Error  = 0;
    ReplyMsg(&io->io_Message);
}
```

---

## Deep Analysis: Checksum Verification

When disassembling the initialization routine, look for the verification pattern that identifies a valid "surviving" RAM disk:

```asm
; Typical checksum verification pattern
CheckSum:
    move.l  (a0)+, d1     ; Get magic cookie
    cmpi.l  #$ABCDEF01, d1 ; Verify magic
    bne.s   Invalid
    move.l  #Length, d0
Loop:
    add.l   (a0)+, d2     ; Sum up the block
    dbf     d0, Loop
    cmp.l   Expected, d2
```

---

## Disassembly Landmarks in IDA

1. **Search for string `"ramdrive.device"`** → finds the `ROMTag`.
2. **`RT_INIT` pointer** → points to the initialization function.
3. **`RT_INIT` logic** → calls `MakeLibrary` then `AddDevice`.
4. **Library Base** → Follow the `rd_Device` base to find the `BeginIO` entry point at offset -30.
5. **Switch Table** → `BeginIO` typically uses a jump table (JMP) or a series of `CMPI / BEQ` to dispatch commands.

---

## References

- NDK39: `exec/devices.h`, `exec/io.h`, `devices/trackdisk.h`, `exec/resident.h`
- [io_requests.md](../../06_exec_os/io_requests.md) — IORequest structure and dispatch
- `10_devices/trackdisk_device.md` — TD_* command codes
- [IRA Disassembly of ramdrive.device](http://aminet.net/package/dev/asm/ramdrive_src) — Reference for instruction patterns.
