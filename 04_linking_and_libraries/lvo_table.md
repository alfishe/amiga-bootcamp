[← Home](../README.md) · [Linking & Libraries](README.md)

# LVO Table Layout & Reconstruction

## Overview

The **Library Vector Offset (LVO) table** is the core mechanism of the AmigaOS ABI. Understanding and reconstructing it is essential for reversing any Amiga binary that calls system libraries.

---

## Memory Layout of a Loaded Library

```
Low addresses
←──────────────────────────────────────────────────────────→
                                                High addresses

[JMP table (negative area)]          [struct Library + private data]
...  -36  -30  -24  -18  -12   -6   base+0  base+2  ...

 ↑                               ↑
 Last user function          Library base pointer
 (e.g., -576 for graphics)   (returned by OpenLibrary)
```

Each slot is **6 bytes**:
```
4E F9 AA AA AA AA    JMP.L AAAAAAAA
```

---

## Calculating LVOs

Given `##bias N` in the `.fd` file, the LVO of the `k`th public function (1-indexed) is:
```
LVO_k = -(N + (k-1) × 6)
```

The four mandatory functions before public functions (Open, Close, Expunge, Reserved) are at:
- `LVO_Open = -6`
- `LVO_Close = -12`
- `LVO_Expunge = -18`
- `LVO_Reserved = -24`

For a library with `##bias 30`, the first public function is at `-30`.

---

## Key Library LVO Tables

### exec.library (##bias 30)

| LVO | Function | Registers |
|---|---|---|
| -30 | `Supervisor` | A5=function |
| -36 | `ExitIntr` | (internal) |
| -42 | `Schedule` | (internal) |
| -48 | `Reschedule` | (internal) |
| -54 | `Switch` | (internal) |
| -60 | `Dispatch` | (internal) |
| -66 | `Exception` | (internal) |
| -72 | `InitCode` | D0=startClass, D1=version |
| -78 | `InitStruct` | A1=mem, A2=table, D0=size |
| -84 | `MakeLibrary` | A0=vectors, A1=struct, A2=init, D0=dataSize, D1=segList |
| -90 | `MakeFunctions` | A0=target, A1=funcArray, A2=funcDispBase |
| -96 | `FindResident` | A1=name |
| -102 | `InitResident` | A1=resident, D1=segList |
| -108 | `Alert` | D7=alertNum |
| -114 | `Debug` | D0=flags |
| -120 | `Disable` | |
| -126 | `Enable` | |
| -132 | `Forbid` | |
| -138 | `Permit` | |
| -144 | `SetSR` | D0=newSR, D1=mask |
| -150 | `SuperState` | |
| -156 | `UserState` | D0=savedSR |
| -162 | `SetIntVector` | D0=intNum, A1=interrupt |
| -168 | `AddIntServer` | D0=intNum, A1=interrupt |
| -174 | `RemIntServer` | D0=intNum, A1=interrupt |
| -180 | `Cause` | A1=interrupt |
| -186 | `Allocate` | A0=memHeader, D0=size |
| -192 | `Deallocate` | A0=memHeader, A1=memBlock, D0=size |
| -198 | `AllocMem` | D0=byteSize, D1=requirements |
| -204 | `AllocAbs` | D0=byteSize, A1=location |
| -210 | `FreeMem` | A1=memBlock, D0=byteSize |
| -216 | `AvailMem` | D1=requirements |
| -222 | `AllocEntry` | A0=entry |
| -228 | `FreeEntry` | A0=entry |
| -234 | `Insert` | A0=list, A1=node, A2=listNode |
| -240 | `AddHead` | A0=list, A1=node |
| -246 | `AddTail` | A0=list, A1=node |
| -252 | `Remove` | A1=node |
| -258 | `RemHead` | A0=list |
| -264 | `RemTail` | A0=list |
| -270 | `Enqueue` | A0=list, A1=node |
| -276 | `FindName` | A0=list, A1=name |
| -282 | `AddTask` | A1=task, A2=initialPC, A3=finalPC |
| -288 | `RemTask` | A1=task |
| -294 | `FindTask` | A1=name |
| -300 | `SetTaskPri` | A1=task, D0=priority |
| -306 | `SetSignal` | D0=newSignals, D1=signalSet |
| -312 | `SetExcept` | D0=newSignals, D1=signalSet |
| -318 | `Wait` | D0=signalSet |
| -324 | `Signal` | A1=task, D0=signals |
| -330 | `AllocSignal` | D0=signalNum |
| -336 | `FreeSignal` | D0=signalNum |
| -342 | `AllocTrap` | D0=trapNum |
| -348 | `FreeTrap` | D0=trapNum |
| -354 | `AddPort` | A1=port |
| -360 | `RemPort` | A1=port |
| -366 | `PutMsg` | A0=port, A1=message |
| -372 | `GetMsg` | A0=port |
| -378 | `ReplyMsg` | A1=message |
| -384 | `WaitPort` | A0=port |
| -390 | `FindPort` | A1=name |
| -396 | `AddLibrary` | A1=library |
| -402 | `RemLibrary` | A1=library |
| -408 | `OldOpenLibrary` | A1=libName |
| -414 | `CloseLibrary` | A1=library |
| -420 | `SetFunction` | A1=library, A0=funcOffset, D0=newFunc |
| -426 | `SumLibrary` | A1=library |
| -432 | `AddDevice` | A1=device |
| -438 | `RemDevice` | A1=device |
| -444 | `OpenDevice` | A0=devName, D0=unit, A1=ioReq, D1=flags |
| -450 | `CloseDevice` | A1=ioReq |
| -456 | `DoIO` | A1=ioReq |
| -462 | `SendIO` | A1=ioReq |
| -468 | `CheckIO` | A1=ioReq |
| -474 | `WaitIO` | A1=ioReq |
| -480 | `AbortIO` | A1=ioReq |
| -486 | `AddResource` | A1=resource |
| -492 | `RemResource` | A1=resource |
| -498 | `OpenResource` | A1=resName |
| -552 | `OpenLibrary` | A1=libName, D0=version |
| -558 | `InitSemaphore` | A0=semaphore |
| -564 | `ObtainSemaphore` | A0=semaphore |
| -570 | `ReleaseSemaphore` | A0=semaphore |
| -576 | `AttemptSemaphore` | A0=semaphore |
| -582 | `ObtainSemaphoreList` | A0=sigSemList |
| -588 | `ReleaseSemaphoreList` | A0=sigSemList |
| -594 | `FindSemaphore` | A1=sigSem |
| -600 | `AddSemaphore` | A1=sigSem |
| -606 | `RemSemaphore` | A1=sigSem |
| -612 | `SumKickData` | |
| -618 | `AddMemList` | D0=size, D1=attr, D2=pri, A0=base, A1=name |
| -624 | `CopyMem` | A0=source, A1=dest, D0=size |
| -630 | `CopyMemQuick` | A0=source, A1=dest, D0=size |
| -636 | `CacheClearU` | |
| -642 | `CacheClearE` | A0=addr, D0=len, D1=caches |
| -648 | `CacheControl` | D0=cacheBits, D1=cacheMask |
| -654 | `CreateIORequest` | A0=port, D0=size |
| -660 | `DeleteIORequest` | A0=ioreq |
| -666 | `CreateMsgPort` | |
| -672 | `DeleteMsgPort` | A0=port |
| -678 | `ObtainSemaphoreShared` | A0=sigSem |
| -684 | `AllocVec` | D0=size, D1=attr |
| -690 | `FreeVec` | A1=mem |
| -726 | `NewAddTask` | A1=task, A2=initialPC, A3=finalPC, A4=?? |

---

## Reconstructing the JMP Table During Reverse Engineering

When analysing a patched library (e.g., `bsdsocket.library`):

1. **Find the library base** — usually pointed to by a global variable or passed in A6
2. **Read `lib_NegSize`** at `base+0x10` — this gives the total JMP table byte count
3. **Scan the JMP table** — from `base - lib_NegSize` to `base - 6` in 6-byte steps
4. **Decode each JMP** — `4E F9 AA AA AA AA` → target at `AAAAAAAA`
5. **Match to .fd file** — entry at offset `(-6 × n)` corresponds to function `n`

IDA Pro script to dump JMP table:
```python
import idc, idaapi

def dump_jmp_table(lib_base, num_funcs, fd_names):
    for i, name in enumerate(fd_names):
        slot = lib_base - 6 * (i + 1)
        opcode = idc.get_wide_word(slot)
        if opcode == 0x4EF9:
            target = idc.get_wide_dword(slot + 2)
            idc.set_name(slot, f"lvo_{name}", idc.SN_NOWARN)
            idc.set_name(target, name, idc.SN_NOWARN)
            print(f"LVO -{6*(i+1):4d}  {name:40s} → {target:#010x}")
```

---

## References

- NDK39: `fd/exec_lib.fd`, `fd/dos_lib.fd`, `fd/graphics_lib.fd`
- NDK39: `include/exec/execbase.h` — SysBase layout
- ADCD 2.1 Autodocs: all library function descriptions
