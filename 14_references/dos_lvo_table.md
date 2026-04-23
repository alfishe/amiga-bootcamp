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
| −162 | 162 | DeviceProc (private) |
| −168 | 168 | SetComment |
| −174 | 174 | SetProtection |
| −180 | 180 | DateStamp |
| −186 | 186 | Delay |
| −192 | 192 | WaitForChar |
| −198 | 198 | ParentDir |
| −204 | 204 | IsInteractive |
| −210 | 210 | Execute |
| −216 | 216 | AllocDosObject |
| −222 | 222 | FreeDosObject |
| −228 | 228 | DoPkt |
| −234 | 234 | SendPkt |
| −240 | 240 | WaitPkt |
| −246 | 246 | ReplyPkt |
| −252 | 252 | AbortPkt |
| −258 | 258 | LockRecord |
| −264 | 264 | LockRecords |
| −270 | 270 | UnLockRecord |
| −276 | 276 | UnLockRecords |
| −282 | 282 | SelectInput |
| −288 | 288 | SelectOutput |
| −294 | 294 | FGetC |
| −300 | 300 | FPutC |
| −306 | 306 | UnGetC |
| −312 | 312 | FRead |
| −318 | 318 | FWrite |
| −324 | 324 | FGets |
| −330 | 330 | FPuts |
| −336 | 336 | VFWritef |
| −342 | 342 | VFPrintf |
| −348 | 348 | Flush |
| −354 | 354 | SetVBuf |
| −360 | 360 | DupLockFromFH |
| −366 | 366 | OpenFromLock |
| −372 | 372 | ParentOfFH |
| −378 | 378 | ExamineFH |
| −384 | 384 | SetFileDate |
| −390 | 390 | NameFromLock |
| −396 | 396 | NameFromFH |
| −402 | 402 | SplitName |
| −408 | 408 | SameLock |
| −414 | 414 | SetMode |
| −420 | 420 | ExAll |
| −426 | 426 | ReadLink |
| −432 | 432 | MakeLink |
| −438 | 438 | ChangeMode |
| −444 | 444 | SetFileSize |
| −450 | 450 | SetIoErr |
| −456 | 456 | Fault |
| −462 | 462 | PrintFault |
| −468 | 468 | ErrorReport |
| −474 | 474 | Cli (private) |
| −480 | 480 | CreateNewProc |
| −486 | 486 | RunCommand |
| −492 | 492 | GetConsoleTask |
| −498 | 498 | SetConsoleTask |
| −504 | 504 | GetFileSysTask |
| −510 | 510 | SetFileSysTask |
| −516 | 516 | GetArgStr |
| −522 | 522 | SetArgStr |
| −528 | 528 | FindCliProc |
| −534 | 534 | MaxCli |
| −540 | 540 | SetCurrentDirName |
| −546 | 546 | GetCurrentDirName |
| −552 | 552 | SetProgramName |
| −558 | 558 | GetProgramName |
| −564 | 564 | SetPrompt |
| −570 | 570 | GetPrompt |
| −576 | 576 | SetProgramDir |
| −582 | 582 | GetProgramDir |
| −588 | 588 | SystemTagList |
| −594 | 594 | AssignLock |
| −600 | 600 | AssignLate |
| −606 | 606 | AssignPath |
| −612 | 612 | AssignAdd |
| −618 | 618 | RemAssignList |
| −624 | 624 | GetDeviceProc |
| −630 | 630 | FreeDeviceProc |
| −636 | 636 | LockDosList |
| −642 | 642 | UnLockDosList |
| −648 | 648 | AttemptLockDosList |
| −654 | 654 | RenameDosEntry |
| −660 | 660 | AddDosEntry |
| −666 | 666 | RemDosEntry |
| −672 | 672 | FindDosEntry |
| −678 | 678 | NextDosEntry |
| −684 | 684 | MakeDosEntry |
| −690 | 690 | FreeDosEntry |
| −696 | 696 | IsFileSystem |
| −702 | 702 | Format |
| −708 | 708 | Relabel |
| −714 | 714 | Inhibit |
| −720 | 720 | AddBuffers |
| −726 | 726 | CompareDates |
| −732 | 732 | DateToStr |
| −738 | 738 | StrToDate |
| −744 | 744 | InternalLoadSeg |
| −750 | 750 | InternalUnLoadSeg |
| −756 | 756 | NewLoadSeg |
| −762 | 762 | AddSegment |
| −768 | 768 | FindSegment |
| −774 | 774 | RemSegment |
| −780 | 780 | CheckSignal |
| −786 | 786 | ReadArgs |
| −792 | 792 | FindArg |
| −798 | 798 | ReadItem |
| −804 | 804 | StrToLong |
| −810 | 810 | MatchFirst |
| −816 | 816 | MatchNext |
| −822 | 822 | MatchEnd |
| −828 | 828 | ParsePattern |
| −834 | 834 | MatchPattern |
| −840 | 840 | FreeArgs |
| −846 | 846 | FilePart |
| −852 | 852 | PathPart |
| −858 | 858 | AddPart |
| −864 | 864 | StartNotify |
| −870 | 870 | EndNotify |
| −876 | 876 | SetVar |
| −882 | 882 | GetVar |
| −888 | 888 | DeleteVar |
| −894 | 894 | FindVar |
| −900 | 900 | CliInitNewcli (private) |
| −906 | 906 | CliInitRun (private) |
| −912 | 912 | WriteChars |
| −918 | 918 | PutStr |
| −924 | 924 | VPrintf |
| −930 | 930 | ParsePatternNoCase |
| −936 | 936 | MatchPatternNoCase |
| −942 | 942 | SameDevice (private) |
| −948 | 948 | ExAllEnd |
| −954 | 954 | SetOwner |

---

## References

- NDK39: `fd/dos_lib.fd`
