[← Home](../README.md) · [AmigaDOS](README.md)

# Packet System — DosPacket, ACTION_* Codes

## Overview

AmigaDOS filesystem handlers communicate via **DosPackets** — messages sent to the handler's `MsgPort`. Every file operation (`Open`, `Read`, `Lock`, etc.) is internally translated into an `ACTION_*` packet. Understanding packets is essential for writing custom handlers or intercepting filesystem calls.

---

## struct DosPacket

```c
/* dos/dosextens.h — NDK39 */
struct DosPacket {
    struct Message *dp_Link;  /* exec message (backlink) */
    struct MsgPort *dp_Port;  /* reply port */
    LONG   dp_Type;           /* ACTION_* code */
    LONG   dp_Res1;           /* primary result */
    LONG   dp_Res2;           /* secondary result (error code) */
    LONG   dp_Arg1;           /* argument 1 — type depends on dp_Type */
    LONG   dp_Arg2;
    LONG   dp_Arg3;
    LONG   dp_Arg4;
    LONG   dp_Arg5;
    LONG   dp_Arg6;
    LONG   dp_Arg7;
};
```

---

## Common ACTION_* Codes

| Code | Dec | Action | Args |
|---|---|---|---|
| `ACTION_FINDINPUT` | 1005 | Open for reading | Arg1=FileHandle, Arg2=Lock, Arg3=name(BSTR) |
| `ACTION_FINDOUTPUT` | 1006 | Open for writing (create) | same |
| `ACTION_FINDUPDATE` | 1004 | Open for r/w | same |
| `ACTION_READ` | 82 | Read bytes | Arg1=FH_Arg1, Arg2=buf, Arg3=len |
| `ACTION_WRITE` | 87 | Write bytes | Arg1=FH_Arg1, Arg2=buf, Arg3=len |
| `ACTION_SEEK` | 1008 | Seek | Arg1=FH_Arg1, Arg2=pos, Arg3=mode |
| `ACTION_END` | 1007 | Close file | Arg1=FH_Arg1 |
| `ACTION_LOCATE_OBJECT` | 8 | Lock (obtain) | Arg1=dirLock, Arg2=name(BSTR), Arg3=mode |
| `ACTION_FREE_LOCK` | 15 | UnLock | Arg1=lock |
| `ACTION_EXAMINE_OBJECT` | 23 | Examine (stat) | Arg1=lock, Arg2=FIB(BPTR) |
| `ACTION_EXAMINE_NEXT` | 24 | ExNext | Arg1=lock, Arg2=FIB(BPTR) |
| `ACTION_PARENT` | 29 | ParentDir | Arg1=lock |
| `ACTION_DELETE_OBJECT` | 16 | Delete | Arg1=lock, Arg2=name(BSTR) |
| `ACTION_RENAME_OBJECT` | 17 | Rename | Arg1=fromLock, Arg2=fromName, Arg3=toLock, Arg4=toName |
| `ACTION_CREATE_DIR` | 22 | CreateDir | Arg1=lock, Arg2=name(BSTR) |
| `ACTION_SET_PROTECT` | 21 | SetProtection | Arg1=0, Arg2=lock, Arg3=name(BSTR), Arg4=bits |
| `ACTION_DISK_INFO` | 25 | Info | Arg1=InfoData(BPTR) |
| `ACTION_IS_FILESYSTEM` | 1027 | Query | (none) → Res1=DOSTRUE if filesystem |

---

## Sending a Packet Manually

```c
struct MsgPort *handler = ((struct FileLock *)BADDR(lock))->fl_Task;
struct StandardPacket sp;
sp.sp_Msg.mn_Node.ln_Name = (char *)&sp.sp_Pkt;
sp.sp_Pkt.dp_Link = &sp.sp_Msg;
sp.sp_Pkt.dp_Port = CreateMsgPort();
sp.sp_Pkt.dp_Type = ACTION_DISK_INFO;
sp.sp_Pkt.dp_Arg1 = MKBADDR(infodata);
PutMsg(handler, &sp.sp_Msg);
WaitPort(sp.sp_Pkt.dp_Port);
GetMsg(sp.sp_Pkt.dp_Port);
/* sp.sp_Pkt.dp_Res1 = result */
DeleteMsgPort(sp.sp_Pkt.dp_Port);
```

---

## BSTR — BCPL Strings

Handler packets use **BSTR** for filenames: a BPTR to a length-prefixed string:
```
[len_byte][char_0][char_1]...[char_n]
```
- `len_byte` = string length (max 255)
- No null terminator
- Convert: `UBYTE *bstr = (UBYTE *)BADDR(bstr_bptr); int len = bstr[0]; char *name = &bstr[1];`

---

## References

- NDK39: `dos/dosextens.h`, `dos/dos.h`
- ADCD 2.1: `DoPkt`, packet system
- *Amiga ROM Kernel Reference Manual: Devices* — filesystem handler chapter
