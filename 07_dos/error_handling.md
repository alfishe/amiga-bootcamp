[← Home](../README.md) · [AmigaDOS](README.md)

# Error Handling — IoErr, Fault, PrintFault, Error Codes

## Overview

Every DOS function that can fail sets an error code retrievable via `IoErr()`. The error code is stored in `pr_Result2` of the calling process.

---

## API

| LVO | Function | Description |
|---|---|---|
| −132 | `IoErr()` | Return last error code |
| −138 | `SetIoErr(code)` | Set error code manually |
| −468 | `Fault(code, header, buf, len)` | Format error message into buffer |
| −474 | `PrintFault(code, header)` | Print error message to stderr |

---

## Complete Error Code Table

| Code | Constant | Meaning |
|---|---|---|
| 103 | `ERROR_NO_FREE_STORE` | Out of memory |
| 104 | `ERROR_TASK_TABLE_FULL` | Process table full |
| 114 | `ERROR_BAD_TEMPLATE` | Bad template for ReadArgs |
| 115 | `ERROR_BAD_NUMBER` | Bad number in argument |
| 116 | `ERROR_REQUIRED_ARG_MISSING` | Required argument missing |
| 117 | `ERROR_KEY_NEEDS_ARG` | Keyword requires an argument |
| 118 | `ERROR_TOO_MANY_ARGS` | Too many arguments |
| 119 | `ERROR_UNMATCHED_QUOTES` | Unmatched quotes |
| 120 | `ERROR_LINE_TOO_LONG` | Argument line too long |
| 121 | `ERROR_FILE_NOT_OBJECT` | Not a valid executable |
| 122 | `ERROR_INVALID_RESIDENT_LIBRARY` | Invalid resident library |
| 202 | `ERROR_OBJECT_IN_USE` | Object is in use |
| 203 | `ERROR_OBJECT_EXISTS` | Object already exists |
| 204 | `ERROR_DIR_NOT_FOUND` | Directory not found |
| 205 | `ERROR_OBJECT_NOT_FOUND` | Object not found |
| 206 | `ERROR_BAD_STREAM_NAME` | Invalid stream name |
| 207 | `ERROR_OBJECT_TOO_LARGE` | Object too large |
| 209 | `ERROR_ACTION_NOT_KNOWN` | Action not known (by handler) |
| 210 | `ERROR_INVALID_COMPONENT_NAME` | Invalid filename component |
| 211 | `ERROR_INVALID_LOCK` | Invalid lock |
| 212 | `ERROR_OBJECT_WRONG_TYPE` | Object wrong type |
| 213 | `ERROR_DISK_NOT_VALIDATED` | Disk not validated |
| 214 | `ERROR_DISK_WRITE_PROTECTED` | Disk is write-protected |
| 215 | `ERROR_RENAME_ACROSS_DEVICES` | Rename across devices |
| 216 | `ERROR_DIRECTORY_NOT_EMPTY` | Directory not empty |
| 217 | `ERROR_TOO_MANY_LEVELS` | Too many directory levels |
| 218 | `ERROR_DEVICE_NOT_MOUNTED` | Device not mounted |
| 219 | `ERROR_SEEK_ERROR` | Seek error |
| 220 | `ERROR_COMMENT_TOO_BIG` | Comment too big |
| 221 | `ERROR_DISK_FULL` | Disk full |
| 222 | `ERROR_DELETE_PROTECTED` | Delete protected |
| 223 | `ERROR_WRITE_PROTECTED` | Write protected |
| 224 | `ERROR_READ_PROTECTED` | Read protected |
| 225 | `ERROR_NOT_A_DOS_DISK` | Not a DOS disk |
| 226 | `ERROR_NO_DISK` | No disk in drive |
| 232 | `ERROR_NO_MORE_ENTRIES` | No more directory entries |
| 233 | `ERROR_IS_SOFT_LINK` | Object is a soft link |
| 234 | `ERROR_OBJECT_LINKED` | Object is hard-linked |
| 235 | `ERROR_BAD_HUNK` | Bad hunk in executable |
| 236 | `ERROR_NOT_IMPLEMENTED` | Function not implemented |
| 240 | `ERROR_RECORD_NOT_LOCKED` | Record not locked |
| 241 | `ERROR_LOCK_COLLISION` | Record lock collision |
| 242 | `ERROR_LOCK_TIMEOUT` | Record lock timeout |
| 243 | `ERROR_UNLOCK_ERROR` | Unlock error |

---

## Usage Pattern

```c
BPTR fh = Open("nonexistent", MODE_OLDFILE);
if (!fh) {
    LONG err = IoErr();
    PrintFault(err, "myapp");
    /* prints: "myapp: Object not found" */
}
```

---

## References

- NDK39: `dos/dos.h`, `dos/dosasl.h`
- ADCD 2.1: `IoErr`, `Fault`, `PrintFault`
