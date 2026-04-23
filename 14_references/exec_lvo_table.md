[← Home](../README.md) · [References](README.md)

# exec.library — LVO Offset Table

## Complete LVO Table (NDK 3.9)

| LVO | Bias | Function |
|---|---|---|
| −30 | 30 | Supervisor |
| −36 | 36 | ExitIntr (private) |
| −42 | 42 | Schedule (private) |
| −48 | 48 | Reschedule (private) |
| −54 | 54 | Switch (private) |
| −60 | 60 | Dispatch (private) |
| −66 | 66 | Exception (private) |
| −72 | 72 | InitCode |
| −78 | 78 | InitStruct |
| −84 | 84 | MakeLibrary |
| −90 | 90 | MakeFunctions |
| −96 | 96 | FindResident |
| −102 | 102 | InitResident |
| −108 | 108 | Alert |
| −114 | 114 | Debug |
| −120 | 120 | Forbid |
| −126 | 126 | Permit |
| −132 | 132 | Disable |
| −138 | 138 | Enable |
| −144 | 144 | SetSR |
| −150 | 150 | SuperState |
| −156 | 156 | UserState |
| −162 | 162 | SetIntVector |
| −168 | 168 | AddIntServer |
| −174 | 174 | RemIntServer |
| −180 | 180 | Cause |
| −186 | 186 | Allocate |
| −192 | 192 | Deallocate |
| −198 | 198 | AllocMem |
| −204 | 204 | AllocAbs |
| −210 | 210 | FreeMem |
| −216 | 216 | AvailMem |
| −222 | 222 | AllocEntry |
| −228 | 228 | FreeEntry |
| −234 | 234 | Insert |
| −240 | 240 | AddHead |
| −246 | 246 | AddTail |
| −252 | 252 | Remove |
| −258 | 258 | RemHead |
| −264 | 264 | RemTail |
| −270 | 270 | Enqueue |
| −276 | 276 | FindName |
| −282 | 282 | AddTask |
| −288 | 288 | RemTask |
| −294 | 294 | FindTask |
| −300 | 300 | SetTaskPri |
| −306 | 306 | SetSignal |
| −312 | 312 | SetExcept |
| −318 | 318 | Wait |
| −324 | 324 | Signal |
| −330 | 330 | AllocSignal |
| −336 | 336 | FreeSignal |
| −342 | 342 | AllocTrap |
| −348 | 348 | FreeTrap |
| −354 | 354 | AddPort |
| −360 | 360 | RemPort |
| −366 | 366 | PutMsg |
| −372 | 372 | GetMsg |
| −378 | 378 | ReplyMsg |
| −384 | 384 | WaitPort |
| −390 | 390 | FindPort |
| −396 | 396 | AddLibrary |
| −402 | 402 | RemLibrary |
| −408 | 408 | OldOpenLibrary |
| −414 | 414 | CloseLibrary |
| −420 | 420 | SetFunction |
| −426 | 426 | SumLibrary |
| −432 | 432 | AddDevice |
| −438 | 438 | RemDevice |
| −444 | 444 | OpenDevice |
| −450 | 450 | CloseDevice |
| −456 | 456 | DoIO |
| −462 | 462 | SendIO |
| −468 | 468 | CheckIO |
| −474 | 474 | WaitIO |
| −480 | 480 | AbortIO |
| −486 | 486 | AddResource |
| −492 | 492 | RemResource |
| −498 | 498 | OpenResource |
| −504 | 504 | RawIOInit (private) |
| −510 | 510 | RawMayGetChar (private) |
| −516 | 516 | RawPutChar (private) |
| −522 | 522 | RawDoFmt |
| −528 | 528 | GetCC |
| −534 | 534 | TypeOfMem |
| −540 | 540 | Procure |
| −546 | 546 | Vacate |
| −552 | 552 | OpenLibrary |
| −558 | 558 | InitSemaphore |
| −564 | 564 | ObtainSemaphore |
| −570 | 570 | ReleaseSemaphore |
| −576 | 576 | AttemptSemaphore |
| −582 | 582 | ObtainSemaphoreList |
| −588 | 588 | ReleaseSemaphoreList |
| −594 | 594 | FindSemaphore |
| −600 | 600 | AddSemaphore |
| −606 | 606 | RemSemaphore |
| −612 | 612 | SumKickData |
| −618 | 618 | AddMemList |
| −624 | 624 | CopyMem |
| −630 | 630 | CopyMemQuick |
| −636 | 636 | CacheClearU |
| −642 | 642 | CacheClearE |
| −648 | 648 | CacheControl |
| −654 | 654 | CreateIORequest |
| −660 | 660 | DeleteIORequest |
| −666 | 666 | CreateMsgPort |
| −672 | 672 | DeleteMsgPort |
| −678 | 678 | ObtainSemaphoreShared |
| −684 | 684 | AllocVec |
| −690 | 690 | FreeVec |
| −696 | 696 | CreatePool |
| −702 | 702 | DeletePool |
| −708 | 708 | AllocPooled |
| −714 | 714 | FreePooled |
| −720 | 720 | AttemptSemaphoreShared |
| −726 | 726 | ColdReboot |
| −732 | 732 | StackSwap |
| −738 | 738 | ChildFree (private) |
| −744 | 744 | ChildOrphan (private) |
| −750 | 750 | ChildStatus (private) |
| −756 | 756 | ChildWait (private) |
| −762 | 762 | CachePreDMA |
| −768 | 768 | CachePostDMA |
| −774 | 774 | AddMemHandler |
| −780 | 780 | RemMemHandler |
| −786 | 786 | ObtainQuickVector |

---

## References

- NDK39: `fd/exec_lib.fd`
- Use `parse_fd.py` from `13_toolchain/fd_files.md` to regenerate
