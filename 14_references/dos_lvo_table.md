[← Home](../README.md) · [References](README.md)

# dos.library — LVO Offset Table

## Complete LVO Table (NDK 3.9, Public Functions)

| LVO | Bias | Function |
|---|---|---|
| −30 | 30 | Open |
| −36 | 36 | Close |
| −42 | 42 | Read |
| −48 | 48 | Write |
| −54 | 54 | Input |
| −60 | 60 | Output |
| −66 | 66 | Seek |
| −72 | 72 | DeleteFile |
| −78 | 78 | Rename |
| −84 | 84 | Lock |
| −90 | 90 | UnLock |
| −96 | 96 | DupLock |
| −102 | 102 | Examine |
| −108 | 108 | ExNext |
| −114 | 114 | Info |
| −120 | 120 | CreateDir |
| −126 | 126 | CurrentDir |
| −132 | 132 | IoErr |
| −138 | 138 | CreateProc |
| −144 | 144 | Exit |
| −150 | 150 | LoadSeg |
| −156 | 156 | UnLoadSeg |
| −162 | 162 | ClearVec (private) |
| −168 | 168 | NoReqLoadSeg (private) |
| −174 | 174 | DeviceProc |
| −180 | 180 | SetComment |
| −186 | 186 | SetProtection |
| −192 | 192 | DateStamp |
| −198 | 198 | Delay |
| −204 | 204 | WaitForChar |
| −210 | 210 | ParentDir |
| −216 | 216 | IsInteractive |
| −222 | 222 | Execute |
| −228 | 228 | AllocDosObject |
| −234 | 234 | FreeDosObject |
| −240 | 240 | DoPkt |
| −246 | 246 | SendPkt |
| −252 | 252 | WaitPkt |
| −258 | 258 | ReplyPkt |
| −264 | 264 | AbortPkt |
| −270 | 270 | LockRecord |
| −276 | 276 | LockRecords |
| −282 | 282 | UnLockRecord |
| −288 | 288 | UnLockRecords |
| −294 | 294 | SelectInput |
| −300 | 300 | SelectOutput |
| −306 | 306 | FGetC |
| −312 | 312 | FPutC |
| −318 | 318 | UnGetC |
| −324 | 324 | FRead |
| −330 | 330 | FWrite |
| −336 | 336 | FGets |
| −342 | 342 | FPuts |
| −348 | 348 | VFWritef |
| −354 | 354 | VFPrintf |
| −360 | 360 | Flush |
| −366 | 366 | SetVBuf |
| −372 | 372 | DupLockFromFH |
| −378 | 378 | OpenFromLock |
| −384 | 384 | ParentOfFH |
| −390 | 390 | ExamineFH |
| −396 | 396 | SetFileDate |
| −402 | 402 | NameFromLock |
| −408 | 408 | NameFromFH |
| −414 | 414 | SplitName |
| −420 | 420 | SameLock |
| −426 | 426 | SetMode |
| −432 | 432 | ExAll |
| −438 | 438 | ReadLink |
| −444 | 444 | MakeLink |
| −450 | 450 | ChangeMode |
| −456 | 456 | SetFileSize |
| −462 | 462 | SetIoErr |
| −468 | 468 | Fault |
| −474 | 474 | PrintFault |
| −480 | 480 | ErrorReport |
| −492 | 492 | Cli |
| −498 | 498 | CreateNewProc |
| −504 | 504 | RunCommand |
| −510 | 510 | GetConsoleTask |
| −516 | 516 | SetConsoleTask |
| −522 | 522 | GetFileSysTask |
| −528 | 528 | SetFileSysTask |
| −534 | 534 | GetArgStr |
| −540 | 540 | SetArgStr |
| −546 | 546 | FindCliProc |
| −552 | 552 | MaxCli |
| −558 | 558 | SetCurrentDirName |
| −564 | 564 | GetCurrentDirName |
| −570 | 570 | SetProgramName |
| −576 | 576 | GetProgramName |
| −582 | 582 | SetPrompt |
| −588 | 588 | GetPrompt |
| −594 | 594 | SetProgramDir |
| −600 | 600 | GetProgramDir |
| −606 | 606 | SystemTagList |
| −612 | 612 | AssignLock |
| −618 | 618 | AssignLate |
| −624 | 624 | AssignPath |
| −630 | 630 | AssignAdd |
| −636 | 636 | RemAssignList |
| −642 | 642 | GetDeviceProc |
| −648 | 648 | FreeDeviceProc |
| −654 | 654 | LockDosList |
| −660 | 660 | UnLockDosList |
| −666 | 666 | AttemptLockDosList |
| −672 | 672 | RemDosEntry |
| −678 | 678 | AddDosEntry |
| −684 | 684 | FindDosEntry |
| −690 | 690 | NextDosEntry |
| −696 | 696 | MakeDosEntry |
| −702 | 702 | FreeDosEntry |
| −708 | 708 | IsFileSystem |
| −714 | 714 | Format |
| −720 | 720 | Relabel |
| −726 | 726 | Inhibit |
| −732 | 732 | AddBuffers |
| −738 | 738 | CompareDates |
| −744 | 744 | DateToStr |
| −750 | 750 | StrToDate |
| −756 | 756 | InternalLoadSeg |
| −762 | 762 | InternalUnLoadSeg |
| −768 | 768 | NewLoadSeg |
| −774 | 774 | AddSegment |
| −780 | 780 | FindSegment |
| −786 | 786 | RemSegment |
| −792 | 792 | CheckSignal |
| −798 | 798 | ReadArgs |
| −804 | 804 | FindArg |
| −810 | 810 | ReadItem |
| −816 | 816 | StrToLong |
| −822 | 822 | MatchFirst |
| −828 | 828 | MatchNext |
| −834 | 834 | MatchEnd |
| −840 | 840 | ParsePattern |
| −846 | 846 | MatchPattern |
| −852 | 852 | DosNameFromAnchor (private) |
| −858 | 858 | FreeArgs |
| −870 | 870 | FilePart |
| −876 | 876 | PathPart |
| −882 | 882 | AddPart |
| −888 | 888 | StartNotify |
| −894 | 894 | EndNotify |
| −900 | 900 | SetVar |
| −906 | 906 | GetVar |
| −912 | 912 | DeleteVar |
| −918 | 918 | FindVar |
| −924 | 924 | CliInit |
| −930 | 930 | CliInitNewcli |
| −936 | 936 | CliInitRun |
| −942 | 942 | WriteChars |
| −948 | 948 | PutStr |
| −954 | 954 | VPrintf |
| −966 | 966 | ParsePatternNoCase |
| −972 | 972 | MatchPatternNoCase |
| −978 | 978 | DosGetString (private) |
| −984 | 984 | SameDevice |
| −990 | 990 | SetOwner |

---

## References

- NDK39: `fd/dos_lib.fd`
