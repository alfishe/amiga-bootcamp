[← Home](../README.md) · [References](README.md)

# Error Codes — Complete Reference

## DOS Error Codes

Full reference in [error_handling.md](../07_dos/error_handling.md). Summary of the most commonly encountered:

| Code | Constant | Description |
|---|---|---|
| 103 | `ERROR_INSUFFICIENT_FREE_STORE` | Out of memory |
| 114 | `ERROR_BAD_TEMPLATE` | Command-line template parse error |
| 121 | `ERROR_FILE_NOT_OBJECT` | Not a valid executable |
| 202 | `ERROR_OBJECT_IN_USE` | File/dir locked by another process |
| 203 | `ERROR_OBJECT_EXISTS` | File already exists (can't create) |
| 204 | `ERROR_DIR_NOT_FOUND` | Directory path not found |
| 205 | `ERROR_OBJECT_NOT_FOUND` | File not found |
| 209 | `ERROR_ACTION_NOT_KNOWN` | Packet type not supported by handler |
| 210 | `ERROR_INVALID_COMPONENT_NAME` | Illegal character in filename |
| 212 | `ERROR_OBJECT_WRONG_TYPE` | e.g., tried to Enter a file |
| 213 | `ERROR_DISK_NOT_VALIDATED` | Disk not yet validated after insert |
| 214 | `ERROR_DISK_WRITE_PROTECTED` | Write-protected media |
| 216 | `ERROR_DIRECTORY_NOT_EMPTY` | Can't delete non-empty directory |
| 218 | `ERROR_DEVICE_NOT_MOUNTED` | Device/volume not mounted |
| 221 | `ERROR_DISK_FULL` | No free space |
| 222 | `ERROR_DELETE_PROTECTED` | File has delete protection |
| 223 | `ERROR_WRITE_PROTECTED` | File has write protection |
| 224 | `ERROR_READ_PROTECTED` | File has read protection |
| 225 | `ERROR_NOT_A_DOS_DISK` | Unrecognised disk format |
| 226 | `ERROR_NO_DISK` | No disk in drive |
| 232 | `ERROR_NO_MORE_ENTRIES` | End of directory scan (ExNext) |
| 233 | `ERROR_IS_SOFT_LINK` | Object is a soft link |
| 303 | `ERROR_BUFFER_OVERFLOW` | Buffer too small |

---

## Exec Device Errors

Returned in `io_Error` field of IORequest:

| Code | Constant | Description |
|---|---|---|
| 0 | — | Success |
| -1 | `IOERR_OPENFAIL` | OpenDevice failed |
| -2 | `IOERR_ABORTED` | I/O request was AbortIO'd |
| -3 | `IOERR_NOCMD` | Command not supported by this device |
| -4 | `IOERR_BADLENGTH` | Invalid length parameter |
| -5 | `IOERR_BADADDRESS` | Invalid address parameter |
| -6 | `IOERR_UNITBUSY` | Unit is busy (exclusive access) |
| -7 | `IOERR_SELFTEST` | Hardware self-test failure |

---

## Trackdisk / SCSI Errors

| Code | Constant | Description |
|---|---|---|
| 20 | `TDERR_NotSpecified` | General hardware error |
| 21 | `TDERR_NoSecHdr` | Sector header not found |
| 22 | `TDERR_BadSecPreamble` | Bad sector preamble |
| 23 | `TDERR_BadSecID` | Bad sector ID |
| 24 | `TDERR_BadHdrSum` | Header checksum error |
| 25 | `TDERR_BadSecSum` | Sector checksum error |
| 26 | `TDERR_TooFewSecs` | Too few sectors found |
| 27 | `TDERR_BadSecHdr` | Bad sector header |
| 28 | `TDERR_WriteProt` | Disk is write protected |
| 29 | `TDERR_DiskChanged` | Disk was changed |
| 30 | `TDERR_SeekError` | Seek error |
| 31 | `TDERR_NoMem` | Not enough memory |
| 32 | `TDERR_BadUnitNum` | Invalid unit number |
| 33 | `TDERR_BadDriveType` | Bad drive type |
| 34 | `TDERR_DriveInUse` | Drive in use |
| 35 | `TDERR_PostReset` | Post-reset error |

---

## Intuition/Workbench Error Codes

| Value | Meaning |
|---|---|
| 0 | Success |
| 1 | Not enough memory |
| 2 | No chip memory |
| 3 | No free store |
| 4 | Screen too big |
| 5 | No screen |

---

## References

- NDK39: `dos/dos.h`, `exec/errors.h`, `devices/trackdisk.h`
- See: [error_handling.md](../07_dos/error_handling.md) — DOS error handling patterns
