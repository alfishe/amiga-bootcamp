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
| [cdfs.md](cdfs.md) | **CD-ROM filesystems**: ISO 9660 (PVD layout, levels 1–3), Rock Ridge (SUSP/RRIP tags), Joliet (UCS-2), UDF (ECMA-167), HFS; handler architecture (three-layer stack, DOSDrivers mounting, DosType IDs, disc change detection); **7 handler implementations** compared (CDFileSystem, CacheCDFS, AmiCDFS, AsimCDFS, BabelCDFS, AllegroCDFS, ODFileSystem — master comparison table, decision flowchart); CD-DA audio routing; hardware platforms (CDTV SCSI, CD32 Akiko, desktop IDE/SCSI); burning tips; 4 named pitfalls; Rainbow Book standards table; formal ECMA/ISO/IEEE references |
| [environment.md](environment.md) | GetVar/SetVar, local/global/persistent env variables |
| [error_handling.md](error_handling.md) | IoErr, Fault, PrintFault, complete error code table |
| [cli_shell.md](cli_shell.md) | CLI/Shell deep dive: architecture (process creation), BCPL→C history, pipes & I/O redirection, script cookbook (7 real-world patterns), ReadArgs API with template qualifiers, resident commands, shell environment (startup files, variables, prompt customization), 24 built-in commands, 4 named antipatterns, historical context (TRIPOS), modern analogies |
