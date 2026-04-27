[← Home](../README.md)

# dos.library — AmigaDOS Overview

## Section Index

| File | Description |
|---|---|
| [dos_base.md](dos_base.md) | DosLibrary structure, RootNode, BCPL heritage |
| [file_io.md](file_io.md) | Open/Close/Read/Write/Seek, buffered I/O (FRead/SetVBuf), FileInfoBlock, practical patterns |
| [locks_examine.md](locks_examine.md) | Lock semantics (shared/exclusive), handler discovery, Examine/ExNext/ExAll, antipatterns |
| [pattern_matching.md](pattern_matching.md) | ParsePattern, MatchPattern, AmigaDOS wildcard syntax |
| [process_management.md](process_management.md) | CreateNewProc, SystemTagList, Execute |
| [packet_system.md](packet_system.md) | DosPacket wire format, ACTION_* codes, handler protocol, BSTR encoding |
| [filesystem.md](filesystem.md) | FFS/OFS block layout, root/file/data blocks, bitmap, hash function; capabilities matrix (max sizes, directory limits, nesting, floppy/HDD); third-party deep-dive (PFS3, SFS, FFS2 — atomic commits vs journaling vs validation); **fragmentation & defragmentation** (bitmap scatter, defrag tool catalog — ReOrg/DiskSafe/Quarterback/SFSdefrag, CF/SSD rationale, best practices); **partition IDs & on-disk layout** (two-layer RDB/signature system, complete DosType hex tables, ASCII diagrams for OFS/FFS/PFS3/SFS metadata placement); **RDB partitioning** (RigidDiskBlock, PartitionBlock linked list, FS headers, partition limits); **Kickstart boot process** (Strap, BootPri selection, Early Startup Menu, Mermaid flowchart); **multi-boot configurations** (dual-OS, recovery, games); partition layout strategy table; ADF reader (Python on modern machine) |
| [environment.md](environment.md) | GetVar/SetVar, local/global/persistent env variables |
| [error_handling.md](error_handling.md) | IoErr, Fault, PrintFault, complete error code table |
| [cli_shell.md](cli_shell.md) | CLI/Shell: pipes, redirection, scripts, ReadArgs template parsing |
