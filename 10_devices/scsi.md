[← Home](../README.md) · [Devices](README.md)

# scsi.device — Hard Disk I/O

## Overview

SCSI and IDE hard disks are accessed via `scsi.device` (A3000/A4000 built-in) or `2nd.scsi.device` / `ide.device` (A1200/A600). The API is the same as trackdisk for basic read/write, with additional SCSI direct commands.

---

## Opening

```c
struct IOStdReq *scsi = CreateStdIO(port);
OpenDevice("scsi.device", 0, (struct IORequest *)scsi, 0);
/* unit 0 = first SCSI/IDE device */
```

---

## Standard Commands

Same as trackdisk: `CMD_READ`, `CMD_WRITE`, `CMD_UPDATE`, `TD_CHANGENUM`, etc.

---

## Direct SCSI Commands (HD_SCSICMD)

```c
struct SCSICmd scsicmd;
UBYTE cdb[10];    /* SCSI CDB */
UBYTE sense[20];  /* sense data buffer */
UBYTE data[512];  /* data buffer */

/* Read 1 sector at LBA 0: */
cdb[0] = 0x28;    /* READ(10) */
cdb[1] = 0;
cdb[2] = 0; cdb[3] = 0; cdb[4] = 0; cdb[5] = 0;  /* LBA = 0 */
cdb[6] = 0;
cdb[7] = 0; cdb[8] = 1;  /* transfer length = 1 sector */
cdb[9] = 0;

scsicmd.scsi_Data      = (UWORD *)data;
scsicmd.scsi_Length     = 512;
scsicmd.scsi_Command    = cdb;
scsicmd.scsi_CmdLength  = 10;
scsicmd.scsi_Flags      = SCSIF_READ;
scsicmd.scsi_SenseData  = sense;
scsicmd.scsi_SenseLength = sizeof(sense);

scsi->io_Command = HD_SCSICMD;
scsi->io_Data    = &scsicmd;
scsi->io_Length  = sizeof(scsicmd);
DoIO((struct IORequest *)scsi);

if (scsicmd.scsi_Status != 0) {
    /* SCSI error — check sense data */
}
```

---

## References

- NDK39: `devices/scsidisk.h`
- ADCD 2.1: scsi.device autodocs
