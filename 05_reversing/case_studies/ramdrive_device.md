[← Home](../../README.md) · [Reverse Engineering](../README.md)

# Case Study — ramdrive.device Structure Analysis

## Overview

`ramdrive.device` is the Amiga's built-in RAM disk device. It ships in Kickstart ROM and implements the `trackdisk.device`-compatible interface on top of allocated Chip/Fast RAM. Analysing it teaches exec device architecture, IORequest handling, and the device-as-library pattern.

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
        # print offset and map rt_name to string
        print(f"RomTag @ ROM+{i:#x}")
EOF
```

The RomTag for `ramdrive.device` has `RT_TYPE=NT_DEVICE` and `RT_NAME="ramdrive.device"`.

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

`BeginIO` is the heart of any device driver — it dispatches on `io_Command`.

---

## IORequest Command Handling

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

## Memory Allocation Strategy

On initialization, `ramdrive.device` uses `AllocMem`:

```c
rdbase->rd_RAMStart = AllocMem(rdbase->rd_RAMSize,
                               MEMF_PUBLIC | MEMF_CLEAR);
```

Later requests can pass `MEMF_CHIP` to force chip RAM allocation (useful for audio/graphics DMA sources).

---

## Disassembly Landmarks in IDA

After loading Kickstart ROM in IDA with M68k + HUNK/ROM loader:

1. Search for string `"ramdrive.device"` → find RomTag
2. `RT_INIT` pointer → initialization function
3. `RT_INIT` calls `MakeLibrary` then `AddDevice`
4. The device base is stored — follow to find `BeginIO` function
5. `BeginIO` switch table → individual command handlers

---

## References

- NDK39: `exec/devices.h`, `exec/io.h`, `devices/trackdisk.h`
- [io_requests.md](../../06_exec_os/io_requests.md) — IORequest structure and dispatch
- `10_devices/trackdisk_device.md` — TD_* command codes
- Kickstart 3.1 ROM dump (required for disassembly)
