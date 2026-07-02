[← Home](../README.md) · [Boot Sequence](README.md)

# Disk Boot — Floppy, Hard Drive, and Storage Media

## Overview

The Amiga's disk boot process is orchestrated by the Kickstart ROM, transitioning the system from hardware initialization into a running operating system. After the CPU resets and `exec.library` initializes the system, resident device drivers (like `trackdisk.device` for floppies and `scsi.device` for internal IDE/SCSI) are brought online. The `expansion.library` then performs the AutoConfig scan, executing boot ROMs on expansion cards which parse Rigid Disk Blocks (RDB) and mount hard drive partitions into the system.

Finally, the `strap` module orchestrates the boot process by enumerating all discovered boot nodes, sorting them by priority, and attempting to read a 1024-byte bootblock from the highest-priority device. The physical journey to fetch this bootblock differs significantly depending on the media. Floppy disks rely on CPU-driven MFM decoding and direct hardware control of the CIA and Paula chips. Hard drives use a smart controller (SCSI or IDE) that abstracts the media behind a block-device interface. Despite these differences, both the floppy and hard drive paths converge at the same bootblock execution and subsequent `dos.library` handoff.

Understanding these two paths — and the ecosystem of controllers, drivers, and modern storage media that surrounds them — is essential for anyone working with real hardware, FPGA cores, emulators, or disk image tooling. This article covers the physical details of floppy and hard drive boot, RDB partitioning, the controller/driver landscape, CompactFlash as a modern replacement, and practical workflows for preparing disk images.

**Prerequisites:** [Cold Boot](cold_boot.md) (what happens before media is touched), [Kickstart Init](kickstart_init.md) (how resident modules and device drivers are initialized).

**What happens next:** [DOS Boot](dos_boot.md) (how the bootblock hands off to `dos.library` and the Startup-Sequence).

---

## The Generic Boot Flow

Regardless of whether the boot medium is a DD floppy, a 4 GB SCSI hard drive, or a CompactFlash card plugged into a Gayle IDE port, every Amiga boot passes through the same high-level phases. The differences are in *how* each phase discovers and reads the medium — not in *what* it does with the data once loaded.

```mermaid
graph TD
    A["Power On / Reset"] --> B["Kickstart ROM Init"]
    B --> C["exec: Initialize resident modules<br/>(trackdisk.device, scsi.device, etc.)"]
    C --> D["expansion.library: AutoConfig scan<br/>(discover Zorro cards, boot ROMs)"]
    D --> E["strap module: Enumerate bootable devices"]
    E --> F{"Boot medium found?"}
    F -->|"Yes"| G["Read 1024-byte bootblock<br/>from selected device"]
    F -->|"No"| H["Display 'Insert Workbench' hand"]
    G --> I["Validate bootblock checksum"]
    I -->|"Valid"| J["Execute bootblock code at $000C"]
    I -->|"Invalid"| H
    J --> K["dos.library mounts volume"]
    K --> L["Execute S:Startup-Sequence"]
```

The critical insight is that the bootblock is always **1024 bytes** (two 512-byte sectors), always loaded into a **dynamically allocated memory buffer** (typically Chip RAM as requested by the boot node), and always **checksummed identically** — whether it came off a floppy track via MFM DMA or off an IDE drive via a CPU PIO loop. The boot code in the bootblock itself doesn't know or care what physical medium it was read from. This abstraction is what makes the Amiga's boot architecture elegant: the complexity is in the *path to the bootblock*, not in the bootblock itself.

### What Does the Bootblock Code Actually Do?

A common misconception is that the 1024-byte bootblock contains the filesystem driver (e.g., FFS or PFS3) or complex logic to read the disk. It does not. 

For standard AmigaOS bootable disks, the bootblock code is **completely identical** regardless of whether the disk is formatted as OFS, FFS, Directory Caching (DC-FFS), or International FFS. The standard bootblock (written by the Workbench `Install` command) contains less than 100 bytes of 68000 assembly code. Its sole purpose is to bridge the gap between the low-level `strap` module and the higher-level operating system.

When `strap` executes the bootblock at offset `$000C`, the code performs a very specific, minimal handoff:
1. It uses `exec.library` to locate `dos.library` in the ROM.
2. On OS 2.0+, it opens `dos.library`, sets a specific initialization flag in the library's base structure, and closes it.
3. It locates `expansion.library` (or `dos.library` on OS 1.3) and extracts the pointer to its `rt_Init` (ROM initialization) vector.
4. It returns this pointer to `strap` (in CPU register `A0`), along with a success code (`D0 = 0`).
5. `strap` then executes a direct `JMP` to that ROM routine, handing off control to the OS to mount the boot volume and execute `S:Startup-Sequence`.

Because this standard boot code only manipulates ROM pointers and does no actual disk I/O, it is **filesystem-agnostic** and **medium-agnostic**. The actual filesystem driver used to read `S:Startup-Sequence` is either resident in the Kickstart ROM (for FFS/OFS) or was previously loaded into RAM from the Rigid Disk Block during the AutoConfig scan (for third-party filesystems like PFS3).

*(Note: Custom bootblocks, such as those used by trackloading games or the demoscene, replace this standard code entirely to bypass `dos.library` and take direct control of the hardware. See [Custom Loaders and DRM](../05_reversing/custom_loaders_and_drm.md) for details.)*

For the detailed bootblock format, checksum algorithm, and `dos.library` handoff sequence, see [DOS Boot](dos_boot.md).

---

## Booting from Floppy (DF0:)

### The Hardware Chain

Floppy boot is the most hardware-intimate boot path on the Amiga. There is no smart controller, no command protocol, and no abstraction layer between the CPU and the spinning magnetic disk. The system uses three chips in concert:

| Component | Role |
|---|---|
| **CIA-B** ($BFD000) | Motor control, drive select, head stepping, side select, /DSKCHANGE detection |
| **Paula** ($DFF000) | Disk DMA engine — streams raw MFM bitstream to/from Chip RAM |
| **CPU** | Decodes MFM data, validates checksums, executes bootblock |

The Kickstart ROM's `trackdisk.device` orchestrates this hardware. It is a true device driver in the exec sense — it responds to `CMD_READ`, `TD_MOTOR`, `TD_CHANGESTATE` — but internally it is doing bare-metal register manipulation, not issuing commands to a smart controller.

### Step-by-Step Physical Process

```mermaid
sequenceDiagram
    participant KS as Kickstart (trackdisk.device)
    participant CIA as CIA-B ($BFD100)
    participant Paula as Paula ($DFF020–$DFF026)
    participant RAM as Chip RAM

    KS->>CIA: Select DF0: (drive select bits)
    KS->>CIA: MTR ON (start motor)
    Note over CIA: Motor spin-up (~500 ms)
    KS->>CIA: Step head to Track 0
    KS->>CIA: Select Side 0 (lower head)
    KS->>Paula: Set DSKPT → Chip RAM buffer
    KS->>Paula: Set DSKLEN → track length + DMA enable
    Note over Paula: Paula waits for $4489 MFM sync word
    Paula->>RAM: DMA streams raw MFM bitstream (one full track)
    Paula-->>KS: DSKBLK interrupt (transfer complete)
    KS->>KS: Decode MFM → extract sectors 0–1 (bootblock)
    KS->>KS: Validate bootblock checksum
    KS->>KS: JMP to bootblock code ($00000C)
```

### MFM Encoding — What the Hardware Actually Sees

The magnetic surface of an Amiga floppy does not store bytes. It stores a continuous stream of **flux transitions** — magnetic polarity changes that Paula's disk DMA reads as a raw bitstream. The data is encoded using **Modified Frequency Modulation (MFM)**, which interleaves clock bits between data bits to ensure the bitstream never has too many consecutive zeros (which would cause the read head to lose synchronization).

Each Amiga sector on disk is preceded by a **sync word**: `$4489`. Paula's hardware is specifically designed to watch for this pattern in the raw MFM stream. When it detects `$4489`, it knows the next bits are the start of a sector header. This is a hardware-level pattern match — Paula has a dedicated sync register at `$DFF07E` (DSKSYNC) that holds the word to watch for.

The encoding works as follows:

| Data Bit | MFM Encoding Rule |
|---|---|
| 1 | Always preceded by clock bit 0: → `01` |
| 0 (after a 1) | No clock needed: → `00` |
| 0 (after a 0) | Clock bit inserted: → `10` |

This means every data byte expands to 16 MFM bits (2 bytes on disk). A DD floppy track stores 11 sectors × 512 bytes = 5632 data bytes, which become ~12,668 bytes of MFM-encoded data (including sector headers, gaps, and checksums) — fitting within the ~12,800 raw bytes per track that the drive physically supports at 300 RPM.

> [!NOTE]
> `trackdisk.device` reads an entire track into a Chip RAM buffer as raw MFM, then decodes it in software to extract individual sectors. It does not read individual sectors — the granularity of the DMA transfer is always one full track. This is why AmigaDOS floppy access is track-oriented, and why reading a single byte from a floppy still reads 5.5 KB of data into the track buffer.

### Custom Trackloaders and the Floppy's Unique Property

The floppy boot path has a property that no other Amiga boot medium shares: **the bootblock code can bypass DOS entirely**. Because `trackdisk.device` provides raw sector access and the bootblock executes with full supervisor privileges, game developers routinely replaced the standard bootblock with custom trackloaders that read non-standard disk formats (extra sectors per track, long tracks, modified MFM encoding) directly via Paula's DMA registers. This is the foundation of Amiga game copy protection and the demoscene's disk-based intros.

For an in-depth treatment of custom trackloaders, non-standard disk formats, and physical DRM tricks, see [Custom Loaders and DRM](../05_reversing/custom_loaders_and_drm.md).

---

## Booting from Hard Drive

### The Smart Device Paradigm

Hard drive boot is architecturally the opposite of floppy boot. Instead of the CPU directly controlling motors and reading raw bitstreams, a **smart controller** handles all physical media interaction. The CPU communicates with the controller through a command/response protocol — either ATA task file registers (for IDE) or SCSI command descriptor blocks (for SCSI). The controller translates these high-level commands into the low-level operations needed to read sectors from the physical media.

This abstraction means the CPU never sees MFM encoding, head positioning, or rotational timing. It sends a command ("read sector at LBA N"), waits for the controller to signal completion, and then retrieves the data. The data path from controller to RAM is where the critical architectural distinction lies — and where the existing documentation in this repository had an error that needs correcting.

### PIO vs DMA — The Critical Distinction

> [!WARNING]
> **Stock Commodore IDE controllers have no DMA.** The Gayle chip (A600, A1200) and the A4000 motherboard IDE interface are strictly PIO (Programmed I/O). The CPU executes a `MOVE.W` loop to transfer every word of data between the IDE data register and system RAM. This consumes 100% of the CPU during disk I/O. Only SCSI controllers (A3000, A4000T, Zorro cards) and the third-party FastATA Zorro IDE card have DMA capability. This distinction is fundamental to understanding Amiga storage performance.

| Transfer Method | How It Works | CPU Load | Controllers |
|---|---|---|---|
| **PIO (Programmed I/O)** | CPU reads/writes every word via `MOVE.W` loop between device register and RAM | **100%** during transfer | Gayle IDE (A600/A1200), A4000 IDE, Buddha, Catweasel, TF1260 |
| **DMA (Direct Memory Access)** | Controller's DMA engine transfers data to/from RAM autonomously; CPU is free | **~0%** during transfer | A3000 SCSI (SDMAC), A4000T SCSI, A2091, GVP Series II, A4091, FastATA |

### IDE Boot — Step by Step (PIO Path)

This is the boot path for the most common Amiga hard drive setup: an A1200 or A600 with a 2.5" hard drive or CompactFlash card connected to the Gayle IDE port.

```mermaid
sequenceDiagram
    participant KS as Kickstart (scsi.device)
    participant Gayle as Gayle IDE Registers ($DA0000)
    participant Drive as IDE Drive / CF Card
    participant RAM as System RAM (Chip or Fast)

    KS->>Gayle: Write ATA command: IDENTIFY DEVICE ($EC)
    Gayle->>Drive: Forward command to drive
    Drive-->>Gayle: Drive sets DRQ (data ready)
    Note over KS,RAM: CPU MOVE.W loop — 256 words
    KS->>Gayle: Read data register ($DA0000), word by word
    KS->>RAM: Store each word to RAM buffer
    Note over KS: Parse drive identity, confirm media present
    KS->>Gayle: Write ATA command: READ SECTORS ($20), LBA 0
    Gayle->>Drive: Forward command
    Drive-->>Gayle: DRQ set (sector ready)
    KS->>Gayle: CPU MOVE.W loop — read 256 words (512 bytes)
    KS->>RAM: Store to RAM — this is the first RDB sector
    KS->>KS: Check for "RDSK" signature ($5244534B)
    Note over KS: Parse RDB → find PartitionList → select boot partition
    KS->>Gayle: READ SECTORS for bootblock (2 sectors)
    KS->>RAM: CPU PIO transfer — 1024 bytes
    KS->>KS: Validate bootblock checksum
    KS->>KS: Execute bootblock → dos.library
```

Note the key difference from floppy boot: there is no MFM decoding, no motor control, and no DMA from the disk subsystem. But there is also no DMA *to* RAM — every word passes through a CPU register. On a stock 68020 at 14 MHz (A1200), this yields approximately 1.5 MB/s sustained throughput, regardless of how fast the drive itself is.

### SCSI Boot — Step by Step (DMA Path)

This is the boot path for an A3000 with its onboard WD33C93/SDMAC SCSI controller, or a big-box Amiga with a Zorro SCSI card.

```mermaid
sequenceDiagram
    participant KS as Kickstart (scsi.device)
    participant SCSI as WD33C93 / NCR 53C710
    participant DMA as SDMAC / Card DMA Engine
    participant Drive as SCSI Hard Drive
    participant RAM as Fast RAM

    KS->>SCSI: Issue SCSI READ(10) CDB — LBA 0, count 1
    SCSI->>Drive: SCSI bus arbitration → selection → command
    Drive-->>SCSI: Data-In phase — sector data on SCSI bus
    SCSI->>DMA: Signal data ready
    DMA->>RAM: Bus-mastering DMA transfer (512 bytes)
    DMA-->>KS: Interrupt: transfer complete
    Note over KS: CPU was free during the entire transfer
    KS->>KS: Check for "RDSK" signature
    Note over KS: Parse RDB → find boot partition
    KS->>SCSI: READ(10) for bootblock (2 sectors)
    SCSI->>Drive: SCSI bus transfer
    DMA->>RAM: DMA — 1024 bytes to Fast RAM
    DMA-->>KS: Interrupt
    KS->>KS: Validate bootblock, execute → dos.library
```

The key advantage: the CPU is idle during data transfer. On a system with a 68040 or 68060 doing background computation (rendering, decompression), SCSI DMA means disk I/O doesn't stall the CPU. This is why the A3000's SCSI architecture was considered superior to the later A4000's cost-reduced IDE — despite IDE drives being cheaper and more readily available.

### AutoConfig and Boot ROMs — How Controllers Appear

Before any hard drive can boot, its controller must be discovered and its device driver must be loaded. For onboard controllers (Gayle IDE, A3000 SCSI), the drivers are resident modules in the Kickstart ROM — they initialize automatically during the RomTag scan. For Zorro expansion cards, the process is more involved:

1. **AutoConfig scan** — `expansion.library` walks the Zorro bus, reading each card's configuration registers to determine manufacturer ID, product ID, and memory requirements. See [AutoConfig](../01_hardware/common/autoconfig.md).

2. **DiagArea check** — If a card's AutoConfig ROM contains a **DiagArea** structure, the Kickstart copies it into RAM and calls its `da_DiagPoint` routine. This is where SCSI controllers install their device driver (`scsi.device`, `gvpscsi.device`, etc.) into the exec device list — *before* any boot device is selected.

3. **Boot ROM execution** — If the DiagArea also contains a boot vector (`da_BootPoint`), the card can participate in the boot device selection process. The boot ROM typically scans the attached SCSI bus for drives, reads their RDB, and registers bootable partitions with the strap module.

This DiagArea mechanism is what allows a GVP SCSI card to boot an Amiga 2000 from a SCSI drive without any software on a floppy — the card's ROM contains both the device driver and the boot code.

> [!NOTE]
> The TF1260 accelerator's IDE port is a notable exception to this pattern. It has **no boot ROM** — the `ehide.device` driver is not in the card's ROM or the Kickstart ROM. You must boot from another device (typically the A1200's internal Gayle IDE port) and load the driver with `LoadModule DEVS:ehide.device` during the Startup-Sequence. This means TF1260 IDE storage is never the primary boot device.

---

## RDB Partitioning — From the Boot Perspective

The **Rigid Disk Block (RDB)** is the Amiga's partitioning standard — a self-describing, linked-list structure that is far more flexible than the PC's contemporary MBR scheme. Understanding how the Kickstart interprets the RDB at boot time is essential for setting up bootable hard drives.

> [!IMPORTANT]
> **RDB vs. Boot Block:** Do not confuse the **Rigid Disk Block** with the Amiga's **Boot Block**. 
> - The **RDB** sits at the physical start of the hard drive. It is a vast reserved area (often 256 KB or more) containing a linked list of 512-byte blocks that defines the disk geometry, partitions, and embedded filesystems. It is initialized by tools like HDToolBox when a drive is first set up.
> - The **Boot Block** sits at the start of a formatted partition (like `DH0:`) or a floppy disk. It is exactly 1024 bytes long and its only job is to hand off control to `dos.library` to start the OS. It has no knowledge of disk geometry or partitions.

For the complete RDB on-disk structure (field offsets, checksums, PartitionBlock layout, FileSysHdr format), see [Filesystem — RDB section](../07_dos/filesystem.md).

### The RDB Scan and Reserved Bounds (Blocks 0 to ∞)

When a hard drive device driver spins up and reports a disk to Kickstart, the boot code doesn't stubbornly look only at block 0. Instead, it begins a **16-block scan**, reading blocks 0 through 15 (defined in the OS headers as `RDB_LOCATION_LIMIT`). It searches each sector for the 4-byte magic signature `RDSK` (`$5244534B`) at offset `$00`. 

This 16-sector search window is a stroke of engineering genius that serves three distinct purposes:
1. **Coexistence:** If the RDB were permanently locked to block 0, it would instantly conflict with PC MBR partitioning or Mac partition maps. By allowing the `RDSK` block to drift to block 1, 2, or even 15, the Amiga can natively share a drive with other platforms.
2. **Bad Block Resilience:** If block 0 develops a physical defect (a common reality on 1980s SCSI drives), the RDB can be anchored at block 1 or 2 instead. The partition map survives a single-block failure without condemning the drive.
3. **Controller Quirks:** Some early controllers arrogantly reserved block 0 for their own internal metadata. The 16-block window effortlessly steps around them.

#### The "Minimum 16 Sectors" Rule

Because the `RDSK` anchor block can technically be located anywhere up to block 15, the actual file systems and partition data must logically start *after* this window to be entirely safe. Consequently, there is an unwritten, practical rule: the absolute **minimum reserved space** for the RDB area must be at least **16 sectors**. 

If you were to boldly start your first partition at sector 4, but your partitioning tool wrote the `RDSK` block to sector 2 and its subsequent `PART`/`LSEG` chain naturally spilled into sector 4, formatting that partition would immediately obliterate your RDB chain! By reserving a minimum of 16 sectors (and ensuring the first partition starts at sector 16 or later), the entire `RDB_LOCATION_LIMIT` window acts as an inviolable safe harbor for the partition map. 

#### No Maximum Limit

While 16 sectors is the mathematical minimum for structural safety, the **maximum limit** is completely unbounded. The reserved area for the RDB can span up to the full disk! 

Because the RDB is fundamentally a linked list of independent 512-byte sectors (`RDSK` points to `PART`, which points to `FSHD`, which points to `LSEG`), it simply weaves its way through whatever empty physical space you've left before the first partition begins. If you ever needed to embed a massive 100 MB driver directly into the disk metadata, you would simply instruct your partitioning tool to start `DH0:` at sector 204,800. The Kickstart ROM will blindly follow the linked list, jumping from sector to sector, assembling the massive driver without ever complaining.

### Deep Dive: The RDB Linked List

Once the `RDSK` block is found, it acts as the anchor for a self-describing web of metadata. The RDB is not a flat table; it is a collection of linked blocks pointing to each other by block number. 

```mermaid
graph TD
    RDSK["RDSK Block<br/>(Drive Geometry & Pointers)"]
    PART1["PART Block<br/>(Partition 1: DH0)"]
    PART2["PART Block<br/>(Partition 2: GDH3)"]
    FSHD["FSHD Block<br/>(File System Header: FFS v47.4)"]
    LSEG1["LSEG Block<br/>(Driver Code Chunk 1)"]
    LSEG2["LSEG Block<br/>(Driver Code Chunk 2)"]

    RDSK -->|rdb_PartitionList| PART1
    PART1 -->|pb_Next| PART2
    PART2 -->|pb_Next| NULL["$FFFFFFFF (End)"]

    RDSK -->|rdb_FileSysHdrList| FSHD
    FSHD -->|fh_Next| NULL2["$FFFFFFFF (End)"]
    
    FSHD -->|fh_SegListBlocks| LSEG1
    LSEG1 -->|ls_Next| LSEG2
    LSEG2 -->|ls_Next| NULL3["$FFFFFFFF (End)"]
```

- **`PART` (Partition Block)**: Defines a logical volume (e.g., DH0:). It specifies the start/end cylinders, boot priority, and crucially, the **DosType** (`DOS\1`, `DOS\3`, `PFS\3`) which tells the OS which filesystem driver to use.
- **`FSHD` (File System Header Block)**: Registers a filesystem driver with the system. It maps a specific DosType to a binary driver.
- **`LSEG` (LoadSeg Block)**: The actual binary code of the filesystem driver, split across multiple physical sectors.

### Boot Priority — How Kickstart Picks a Partition

The Kickstart walks the `PART` linked list and collects every partition that has the **`PBF_BOOTABLE`** and **`PBF_AUTOMOUNT`** flags set. These partitions are sorted by their **`de_BootPri`** field (a signed 8-bit value, range −128 to +127). The partition with the highest BootPri wins. Ties are broken by list order.

| BootPri | Typical Use |
|---|---|
| 5 | Default for DH0: (Workbench partition) |
| 0 | Default for secondary partitions (DH1:, DH2:) |
| −128 | Never auto-boot (data-only partition) |
| ≥ 15 | Overrides floppy boot (floppy BootPri is typically 5 on KS 2.0+) |

> [!IMPORTANT]
> Floppy drives (DF0:) have a **built-in boot priority**. On KS 2.0+, the floppy's effective BootPri is 5, so a hard drive partition with BootPri ≥ 6 boots first even with a floppy inserted. Setting a partition's BootPri to 15 or higher guarantees it boots before any floppy.

### Filesystem Loading from RDB

The RDB can store **complete filesystem driver binaries** inline. The mechanism:

1. Each `FSHD` block declares a `DosType`, version, and `patch_flags` (usually `0x180`), along with standard execution variables like `dn_global_vec = -1`. 
2. The `FSHD` points into a chain of `LSEG` blocks. These blocks hold a standard Amiga **[hunk-format executable](../03_loader_and_exec_format/hunk_format.md)**, sliced into 492-byte pieces (a standard 512-byte block minus the 20-byte `LSEG` header).
3. At boot, the Kickstart ROM's `strap` module walks the RDB. For any partition whose `DosType` isn't served natively by the ROM (such as `PFS\3` or `SFS\0`), it reconstructs the hunk image from the `LSEG` chain.
4. It then loads and relocates the image into RAM—just like executing any other Amiga program—and registers it in `FileSystem.resource`.

#### Driver Size Limits and the RDB Reserved Area

There is no hardcoded software limit on the length of an `LSEG` chain. The actual size of the drivers you can embed is bounded only by the **RDB Reserved Area**—the physical gap of sectors between the start of the disk (where `RDSK` lives) and the beginning of the first partition (`PART`).

- Historically, Commodore's HDToolBox reserved exactly **2 cylinders** for the RDB area by default. On a standard drive geometry (e.g., 16 heads × 63 sectors), 2 cylinders provides roughly **1 MB** of space.
- Modern command-line partitioning workflows often auto-reserve around **512 sectors (256 KB)**, which is highly efficient and more than enough space.
- Standard drivers like `FastFileSystem` (~40 KB) or `pfs3aio` (~70 KB) easily fit within the first few dozen sectors.
- If an exceptionally large driver is required, the reserved area can simply be expanded by pushing the start cylinder of the first partition further down the disk.

```text
[ Physical Disk Layout ]

Block 0      Block 2                     Block 512 (Example)                 End of Disk
│            │                           │                                   │
▼            ▼                           ▼                                   ▼
┌────────────┬───────────────────────────┬─────────────────┬─────────────────┐
│ RDSK Block │ FSHD & LSEG Driver Chains │ Partition DH0:  │ Partition DH1:  │
│ (Metadata) │ (PFS3, FFS v47.4, etc.)   │ (Boot Volume)   │ (Data Volume)   │
└────────────┴───────────────────────────┴─────────────────┴─────────────────┘
             ▲                           ▲
             │                           │
             └───────────────────────────┘
                 RDB Reserved Area
             (Gap for Embedded Drivers)

*Legend: 1 Block = 1 physical sector (always 512 bytes at the RDB level, regardless of the filesystem's logical block size inside the partitions).*
```

This elegant design is why a foreign filesystem like PFS3 can boot on a bone-stock A1200 without any ROM updates. The driver is carried directly on the disk and initialized before the `dos.library` even asks for the boot partition.

---

### Real World Example: The 26 GB AmigaOS 3.2 Partition

Consider a modern Amiga setup: an A1200 running OS 3.2.3, booting from a large CompactFlash card (or a VHD image in an emulator). You examine the drive and find a partition named `GDH3` that is **26.0 GB** in size.

If you inspect this partition with HDToolBox, you'll see a specific configuration engineered by the OS 3.2 installer to overcome the classic Amiga's historical limitations:

```text
[ RDB Partition Configuration ]
drive:      GDH3
dos type:   DOS\3 (FFS-Intl)
size:       26.0 GB (cylinders 474–3873)
block size: 4096 bytes
mask:       0x00FFFFFE
```

How does the classic Amiga boot and mount a 26 GB partition using the legacy FastFileSystem? The secret lies in a carefully orchestrated set of RDB fields:

#### 1. Embedded Filesystem (`FSHD`) and Large Disk Addressing
The OS 3.2 installer injects the modern **FastFileSystem v47.4** driver directly into the RDB's `LSEG` blocks. The Kickstart ROM (even if it's an older 3.1 ROM) loads this v47.4 driver during the AutoConfig scan. 

This modern FFS version includes support for **TD64** (Trackdisk 64-bit) and **NSD** (New Style Device) addressing. Historically, the Amiga accessed disks using 32-bit byte offsets (`CMD_READ`), which artificially capped disk sizes at **4 GB** (2^32 bytes). TD64 and NSD are extended command sets (`TD_READ64`, `NSD_READ64`) that allow 64-bit offsets, allowing FFS v47.4 to command the `scsi.device` to safely read and write past the 4 GB barrier.

#### 2. The 4096-Byte Block Size (`de_SizeBlock`)
Classic FFS was designed for 512-byte blocks. On a 26 GB partition, using 512-byte blocks would create an immense amount of metadata overhead (bitmaps, block headers) resulting in severe memory exhaustion and agonizingly slow disk validation.

OS 3.2 solves this by setting the RDB's filesystem block size to **4096 bytes** (8 physical sectors per logical block). 
- **Performance:** 4K blocks align beautifully with the physical flash pages of modern CF cards and SSDs, drastically improving write speeds (sometimes by 5x to 8x).
- **Overhead reduction:** The number of blocks the filesystem must track is cut by 8x, keeping the bitmap size small enough to fit in the Amiga's limited RAM.

#### 3. The Mask (`de_Mask`)
The mask is set to `0x00FFFFFE`. The mask dictates which areas of system RAM the device driver is allowed to DMA into. 
- The `FE` at the end (even address) ensures the DMA buffer is word-aligned, which is required by most Amiga controllers.
- The `00FFFFFF` (24-bit) mask was standard on the A500/A2000 because they only had 24-bit address buses. A mask of `0x00FFFFFE` allows data to be DMA'd into 32-bit Fast RAM (e.g., above the 16 MB boundary on accelerator cards), bypassing slow Chip RAM bounces.

By combining the **embedded v47.4 driver** (to break the 4GB barrier), **4096-byte blocks** (to solve memory overhead and speed up flash writes), and a **32-bit DMA mask** (to leverage accelerator RAM), the Amiga elegantly mounts a 26 GB partition using an architecture designed in 1985.

---

### HDToolBox — The Standard Partitioning Tool

HDToolBox is the Workbench utility for creating and editing RDB partition tables. Key operations:

- **Read Configuration** — detect drive geometry (cylinders, heads, sectors)
- **Partition Drive** — create, resize, and delete partitions
- **Change Filesystem** — add filesystem binaries (`FSHD`/`LSEG` blocks) to the RDB
- **Set Boot Priority** — configure which partition boots first
- **Save Changes to Drive** — write the RDB and partition blocks to disk

> [!NOTE]
> HDToolBox requires the correct device driver name in its `SCSI_DEVICE_NAME` ToolType (accessible via the Workbench Icon > Information menu). For Gayle IDE, this is `scsi.device`. For WinUAE emulated drives, it's `uaehf.device`. Getting this wrong is the most common reason HDToolBox shows "no drives found."

---

## Controllers and Drivers — The Ecosystem

The Amiga storage ecosystem spans Commodore's own controllers, dozens of Zorro expansion cards, and accelerator-integrated interfaces. Each has its own device driver, performance characteristics, and boot behavior.

### Commodore Native Controllers

| Controller | Models | Device Driver | Transfer | DMA? | Boot? | Peak Throughput |
|---|---|---|---|---|---|---|
| **Gayle IDE** | A600, A1200 | `scsi.device` (v43+) | PIO mode 0 | ❌ No | ✅ Yes (ROM driver) | ~1.5 MB/s (68020@14 MHz) |
| **A4000 IDE** | A4000, A4000T | `scsi.device` | PIO | ❌ No | ✅ Yes (ROM driver) | ~2.5 MB/s (68030@25 MHz) |
| **A3000 SCSI** | A3000, A3000T | `scsi.device` (v39) | SCSI-1 | ✅ SDMAC | ✅ Yes (ROM driver) | ~3.5 MB/s |
| **A4000T SCSI** | A4000T | `scsi.device` | SCSI-2 | ✅ NCR 53C710 | ✅ Yes (ROM driver) | ~5 MB/s |

The confusing naming — both the IDE and SCSI interfaces use drivers called `scsi.device` — is a historical accident. Commodore named the A600/A1200 IDE driver `scsi.device` for compatibility with existing RDB tools that hardcoded the name. Despite the name, the Gayle `scsi.device` speaks ATA, not SCSI. See [SCSI](../10_devices/scsi.md) for the full driver interface specification.

For Gayle IDE hardware details — register layout, byte-lane mapping, interrupt routing via CIA-A — see [Gayle IDE & PCMCIA](../01_hardware/common/gayle_ide_pcmcia.md).

### Zorro Expansion SCSI Cards

| Card | Chip | Device Driver | Bus | DMA? | Peak Throughput | Notes |
|---|---|---|---|---|---|---|
| **A2091** | WD33C93 | `scsi.device` | Zorro II | ✅ Yes | ~2.5 MB/s | Commodore. 14 MHz clock hack popular |
| **A2090** | WD33C93 | `scsi.device` | Zorro II | ✅ Yes | ~1.5 MB/s | Earlier design, less reliable |
| **GVP Series II** | WD33C93A | `gvpscsi.device` | Zorro II | ✅ DPRC | ~3.5 MB/s | Proprietary driver — incompatible with Commodore `scsi.device` |
| **GVP HC+8** | WD33C93A | `gvpscsi.device` | Zorro II | ✅ DPRC | ~3.5 MB/s | 8 MB RAM onboard. No termpower — issue with modern SCSI emulators |
| **A4091** | NCR 53C710 | `2nd.scsi.device` | Zorro III | ✅ Yes | ~8–10 MB/s | Fastest stock Commodore SCSI. ReA4091 open-source revival |
| **Blizzard SCSI Kit** | NCR 53C80 | `BlizkitSCSI.device` | Accelerator bus | ✅ Yes | ~3 MB/s | Plugs into Blizzard 1230/1260 |
| **Cyberstorm SCSI** | NCR 53C710/720 | `cybscsi.device` | Accelerator bus | ✅ Yes | ~10 MB/s | Phase5 accelerator boards |

> [!NOTE]
> GVP cards use a proprietary DPRC (Dual-Port RAM Controller) chip and require GVP-specific partitioning software (FaaastPrep or ExpertPrep). They are **not compatible** with Commodore's HDToolBox or `scsi.device`. If you're working with a GVP card, you must use `gvpscsi.device` in all tooltype and script references.

### Third-Party IDE Controllers (Zorro)

| Card | Device Driver | Bus | DMA? | Peak Throughput | Notes |
|---|---|---|---|---|---|
| **Buddha** | `buddha.device` | Zorro II | ❌ PIO | ~2 MB/s | 2 IDE ports. Popular for big-box Amigas |
| **FastATA** | `fastatahd.device` | Zorro II | ✅ DMA | ~6–8 MB/s | **Only Amiga IDE card with DMA** — UDMA/33 support |
| **Catweasel** | `catweasel.device` | Zorro II | ❌ PIO | ~2 MB/s | Also includes floppy controller for HD/ED disks |

### Accelerator-Integrated Storage

| Accelerator | Interface | Device Driver | Boot? | Notes |
|---|---|---|---|---|
| **TF1260** (TerribleFire) | IDE | `ehide.device` | ❌ **No autoboot** | Driver not in ROM. Must boot from Gayle IDE first, then `LoadModule DEVS:ehide.device` |
| **Blizzard 1230/1260** | SCSI (optional kit) | `BlizkitSCSI.device` | ✅ DiagArea boot ROM | NCR 53C80 based |
| **Cyberstorm MK II/III** | SCSI (onboard) | `cybscsi.device` | ✅ DiagArea boot ROM | NCR 53C710/720. High performance |
| **ACA-1233n** | — | — | — | No onboard storage interface |
| **Warp 1260** | — | — | — | No onboard storage interface |

#### TF1260 IDE — The LoadModule Workaround

The TerribleFire TF1260 accelerator for the A1200 includes an onboard IDE port, but it **cannot autoboot** because the `ehide.device` driver is not stored in the card's flash ROM. The setup workflow:

1. Install your primary boot volume on the A1200's **internal Gayle IDE** port (typically a CF card via adapter)
2. Copy `ehide.device` to `DEVS:` on the boot volume
3. Add to `S:Startup-Sequence` (before `SetPatch`):
   ```
   C:LoadModule >NIL: DEVS:ehide.device
   ```
4. Connect a second drive to the TF1260 IDE port — it will appear as an additional device after boot

> [!WARNING]
> The TF1260 IDE interface can be temperamental. It is recommended to remove capacitors E123C and E125C from the A1200 motherboard for stability, and to use high-quality 3.3V CompactFlash cards. Some users create custom Kickstart ROMs that include `ehide.device` to enable autobooting from the TF1260 port.

---

## CompactFlash — The Modern Boot Medium

CompactFlash cards have become the standard storage medium for classic Amigas, replacing mechanical hard drives in virtually all modern setups. The reason is simple: CF cards implement **True IDE mode** — they present themselves as standard ATA devices, speak the same command protocol as a hard drive, and plug into the same 44-pin or 40-pin IDE connector via a passive adapter (no active electronics needed).

### Why CF Works

| Property | Mechanical HDD | CompactFlash |
|---|---|---|
| Interface protocol | ATA (IDE) | ATA (True IDE mode) — identical |
| Seek time | 8–20 ms | ~0.1 ms (no moving parts) |
| Power consumption | 2–5 W | 0.1–0.5 W |
| Noise | Audible | Silent |
| Shock resistance | Fragile | Solid-state |
| Availability (2020s) | Extinct (2.5" PATA) | Widely available |

### Practical Setup

For an A1200 with Gayle IDE:

1. **Adapter** — A 44-pin 2.5" IDE to CF adapter. Passive adapters work; no active electronics needed. Ensure the adapter supports the correct voltage (3.3V for most modern CF cards).

2. **Card selection** — Not all CF cards work reliably. Industrial-grade cards with genuine True IDE mode are preferred. Some consumer cards implement only a subset of ATA commands, causing compatibility issues.

3. **MaxTransfer setting** — This is the most common CF pitfall.

> [!WARNING]
> **The MaxTransfer gotcha**: The Gayle IDE interface can corrupt data if a single transfer exceeds a certain size. You **must** set `MaxTransfer` to `$0001FE00` (130,560 bytes) in the RDB PartitionBlock for every partition. In HDToolBox, this is under the partition's "Advanced Options." Failure to set this correctly causes **silent data corruption** — files appear to write successfully but contain garbage. This applies to all Gayle-connected devices (hard drives and CF cards alike). See [ATAPI](../10_devices/atapi.md) for a detailed explanation.

### SD Cards and MicroSD

SD and MicroSD cards can be used with IDE-to-SD adapters, but these adapters contain active bridge electronics (SD uses a different protocol from ATA). Compatibility is less reliable than with CF cards, and some adapters introduce latency or compatibility issues. CF remains the recommended solid-state option for classic Amiga IDE.

---

## Preparing Disk Images and Media

Whether you're setting up a CF card for real hardware, building an HDF for an emulator, or creating an ADF floppy image, there are three distinct workflows available — each suited to different situations.

### amitools — Modern Cross-Platform Workflow

The `amitools` Python package provides `rdbtool` and `xdftool` for creating and manipulating Amiga disk images entirely from a modern computer (macOS, Linux, Windows). This is the fastest workflow for headless/scripted setups.

**Installation:**

```bash
pip install amitools
```

**Complete recipe — Create a bootable HDF from scratch:**

```bash
# 1. Create a 500 MB HDF file and initialize the RDB
rdbtool work.hdf create size=500Mi + init

# 2. Add two partitions: DH0 (100 MB, bootable) and DH1 (rest)
rdbtool work.hdf add size=100Mi name=DH0 bootable=True boot_pri=5 \
  + add name=DH1

# 3. (Optional) Add PFS3 filesystem to the RDB
rdbtool work.hdf fsadd pfs3aio dos_type=PFS3 version=19.2

# 4. Format partitions with FFS (DOS\3 = FFS + International mode)
xdftool work.hdf open part=DH0 + format "Workbench" ffs intl
xdftool work.hdf open part=DH1 + format "Work" ffs intl

# 5. Pack a Workbench installation into DH0
xdftool work.hdf open part=DH0 + pack ./wb31_files/

# Verify the RDB:
rdbtool work.hdf info
rdbtool work.hdf list

# Verify the filesystem:
xdftool work.hdf open part=DH0 + list
```

**ADF floppy images:**

```bash
# Create a blank DD floppy image
xdftool blank.adf create

# Format it
xdftool blank.adf format "MyDisk" ofs

# Pack files
xdftool blank.adf pack ./my_files/

# List contents
xdftool blank.adf list
```

> [!NOTE]
> `rdbtool` creates the RDB and partition table; `xdftool` handles the filesystem layer (formatting, file operations). For PFS3 partitions, `rdbtool` can add the filesystem binary to the RDB (`fsadd`), but the partition must be quick-formatted from within a booted Amiga or WinUAE — `xdftool` cannot write PFS3 filesystem structures, only FFS/OFS.

### WinUAE — GUI-Based Workflow

WinUAE provides the most complete disk preparation workflow because it runs a real AmigaOS instance, giving you access to HDToolBox and all native formatting tools. This is the recommended approach when you need PFS3, complex partition layouts, or when preparing a CF card for real hardware.

**Creating an HDF image:**

1. In WinUAE, go to **Settings → Hard Drives → Add Hardfile**
2. Set the size (e.g., 500 MB), choose a filename, click **Create**
3. Set controller to **UAE** or **IDE (Auto)**
4. Boot from a Workbench Install ADF
5. Open HDToolBox (see below for ToolType setup)
6. Partition, format, and install Workbench

**Partitioning with HDToolBox in WinUAE:**

1. Select HDToolBox in the `Tools` drawer — **do not double-click yet**
2. Open **Icon → Information** and change the `SCSI_DEVICE_NAME` ToolType:
   - For UAE hardfiles: `uaehf.device`
   - For real CF cards accessed via WinUAE: `uaehf.device`
3. Double-click HDToolBox — it should detect your drive
4. **Change Drive Type → Define New → Read Configuration** (auto-detect geometry)
5. **Partition Drive** — create your partitions, set BootPri, select filesystem
6. **Save Changes to Drive** — writes the RDB
7. Reboot the emulation for partitions to appear

**Writing to a real CF card from WinUAE:**

1. Insert CF card into a USB card reader
2. On Windows, open an **Administrator Command Prompt**:
   ```
   diskpart
   list disk          (identify your CF card by size)
   select disk N      (replace N with CF card number)
   clean              (removes all Windows partitions)
   exit
   ```
3. Launch WinUAE **as Administrator** (right-click → Run as Administrator)
4. Go to **Hard Drives → Add Hard Drive** and select the physical CF card
5. Set controller to **IDE0** and ensure **Read/Write** is checked
6. Boot and use HDToolBox with `SCSI_DEVICE_NAME=uaehf.device`

> [!WARNING]
> When using `diskpart clean`, double-check the disk number. Selecting the wrong disk will erase your Windows drive. Always verify by disk size.

**Transferring an HDF to a CF card:**

On **Windows**, use `Win32DiskImager` to write the `.hdf` file directly to the CF card. On **macOS/Linux**:

```bash
# Identify the CF card device (e.g., /dev/disk4 on macOS, /dev/sdc on Linux)
# WARNING: Triple-check the device — writing to the wrong device destroys data

# macOS:
diskutil list                    # identify CF card
diskutil unmountDisk /dev/diskN  # unmount
sudo dd if=work.hdf of=/dev/rdiskN bs=1m

# Linux:
lsblk                           # identify CF card
sudo dd if=work.hdf of=/dev/sdX bs=1M status=progress
sync
```

### Native Amiga Workflow

If you're working on a running Amiga with a hard drive already installed, you can prepare additional drives or partitions natively.

**HDToolBox (partitioning):**

```
; From Workbench: open the Tools drawer, run HDToolBox
; Or from Shell:
1> SYS:Tools/HDToolBox scsi.device
```

**Install (write bootblock):**

```
; Make a partition bootable by writing a standard bootblock:
1> Install DH0:
```

**Format (from Shell):**

```
; Quick format a partition:
1> Format DRIVE DH1: NAME "Work" FFS INTL QUICK
```

**Format (from Workbench):**

Select the partition icon → **Icons → Format Disk** → choose Quick Format.

### Decision Guide — Which Workflow to Use

| Scenario | Recommended Workflow |
|---|---|
| **Building an HDF for an emulator** | `amitools` (fast, scriptable, no GUI needed) |
| **Preparing a CF card for real hardware** | WinUAE (full HDToolBox access, PFS3 support) |
| **Creating an ADF floppy image** | `amitools xdftool` (simplest) |
| **Adding PFS3 to an existing drive** | WinUAE or native HDToolBox (PFS3 requires Amiga-side formatting) |
| **Automated/CI disk image builds** | `amitools` (fully scriptable, headless) |
| **Repartitioning a drive on a running Amiga** | Native HDToolBox |
| **Mass-producing identical CF cards** | `amitools` to create master HDF → `dd` to clone |

---

## Physical Failure Modes

### Floppy Failures

| Failure | Symptom | Cause | Recovery |
|---|---|---|---|
| **No boot (hand icon)** | Kickstart shows "Insert Workbench" | Bootblock corrupt, disk unformatted, or wrong filesystem ID | Re-install bootblock with `Install DF0:` |
| **Read errors (blinking drive light)** | Repeated retries, eventual failure | Dirty heads, media degradation, demagnetization | Clean heads with isopropyl alcohol; disk may be unrecoverable |
| **Track 0 failure** | Drive clicks repeatedly, never boots | Track 0 sensor misalignment or physical media damage at track 0 | Replace drive mechanism |
| **Alignment drift** | Reads own disks but not disks from other drives | Stepper motor calibration drift | Realign with reference disk (Amiga Test Kit) |
| **Motor doesn't spin** | No activity | CIA-B failure, broken belt (rare on Amigas), or power supply issue | Check CIA-B; replace drive |

### Hard Drive / IDE Failures

| Failure | Symptom | Cause | Recovery |
|---|---|---|---|
| **No drive detected** | HDToolBox shows no drives | Wrong device driver name in ToolType, cable issue, drive DOA | Verify `SCSI_DEVICE_NAME`, check cable, test drive in another system |
| **RDB not found** | Drive detected but no partitions | RDB corrupted or overwritten (e.g., by a PC partitioning tool) | Restore RDB from backup; or re-partition (data lost) |
| **Filesystem validation on every boot** | "Validating DH0:" message on every reboot | Unclean shutdown with FFS, bitmap corruption | Let validation complete; switch to PFS3 for instant recovery |
| **Data corruption (silent)** | Files contain garbage | `MaxTransfer` not set correctly on Gayle IDE | Set `MaxTransfer=$0001FE00` in RDB; re-copy affected files |
| **Spin-up timeout** | Drive detected intermittently | Power supply insufficient for mechanical drive spin-up | Use a powered CF adapter, or replace with CF card |

### CompactFlash-Specific Failures

| Failure | Symptom | Cause | Recovery |
|---|---|---|---|
| **Incompatible card** | Drive not detected or read errors | Card lacks True IDE mode, or uses incompatible ATA commands | Try a different CF brand (industrial-grade recommended) |
| **Write protect** | Writes fail silently or with errors | CF card's internal write-protect activated | Replace card, or check adapter switch |
| **Capacity mismatch** | Partition extends beyond physical media | HPA (Host Protected Area) reduces reported size | Disable HPA with `hdparm` or equivalent tool |
| **Wear-out (rare)** | Increasing bad sectors over time | Flash cell exhaustion after millions of write cycles | Replace card; industrial CF rated for 2M+ cycles |

---

## Floppy vs Hard Drive vs CompactFlash — Summary

| Property | DD Floppy (DF0:) | IDE Hard Drive (DH0:) | CompactFlash (DH0:) |
|---|---|---|---|
| **Capacity** | 880 KB | 20 MB – 4 GB (FFS limit) | 512 MB – 4 GB (FFS), 128 GB (PFS3) |
| **Boot discovery** | Bootblock at sectors 0–1 | RDB scan → partition → bootblock | Same as IDE HDD (True IDE mode) |
| **Transfer method** | Paula DMA (MFM → Chip RAM) | PIO (CPU `MOVE.W` loop) | PIO (same as IDE HDD) |
| **DMA?** | Yes (Paula disk DMA, but MFM-encoded) | No (stock Gayle/A4000 IDE) | No (same interface) |
| **CPU load during I/O** | Moderate (DMA reads, CPU decodes MFM) | 100% (CPU transfers every word) | 100% (same as IDE) |
| **Throughput** | ~50 KB/s | ~1.5 MB/s (A1200), ~2.5 MB/s (A4000) | Same as IDE (limited by interface, not card) |
| **OS bypass possible?** | Yes (custom trackloaders) | No (always goes through device driver and RDB) | No |
| **Partitioning** | None (whole disk = one volume) | RDB (multiple partitions, boot priority) | RDB (same as HDD) |
| **Filesystem options** | OFS, FFS | OFS, FFS, PFS3, SFS | Same as HDD |
| **Removable at runtime?** | Yes (trackdisk.device tracks /DSKCHANGE) | No (hot-removal = data loss) | No (treated as fixed disk) |
| **Failure mode** | Media degradation, alignment | Mechanical failure, spin-up timeout | Wear-out (rare), incompatibility |

---

## Historical Context and Modern Analogies

### The Great Confusion: RDB vs. Boot Block

It is extremely common to confuse the Amiga's **Rigid Disk Block (RDB)** with the Amiga's **Boot Block** used on floppy disks, or to mistakenly equate the RDB to the PC's **Master Boot Record (MBR)**. Understanding the distinction is critical to Amiga storage architecture:

- **The RDB** (Physical Drive Level): Sits at the start of the *physical hard drive*. It is **not fixed-length**. Instead of a single static table, it is a vast reserved physical area containing a **linked list** of 512-byte blocks. It is initialized by HDToolbox when you connect disk first time and start partitioning it.
- **The Boot Block** (Volume Level): Sits at the start of each *formatted partition* (e.g., `DH0:`) or floppy disk. It is exactly **1024 bytes** (2 sectors) in length. Its only job is to hand off control to `dos.library` and start the OS. It has no knowledge of disk geometry or partitions.


### How Competitors Handled Disk Boot

The Amiga's RDB architecture was remarkably advanced for its era, contrasting sharply with the rigidity of the IBM PC.

| Concept | Amiga RDB (1985) | IBM PC MBR (1983) | Modern PC GPT (2006+) |
|---|---|---|---|
| **Structure** | Linked list of 512-byte blocks | Fixed 512-byte static table | Static array of 128-byte entries |
| **Partition Slots** | Practically Unlimited (bounded only by reserved gap) | Exactly 4 primary partitions | Typically 128 partitions |
| **Embedded Drivers** | Yes (`FSHD`/`LSEG` chains) | No | No (UEFI drivers live in an ESP partition, not the partition table) |
| **OS Independence** | Self-describing; OS loads foreign drivers directly from disk | Relies entirely on BIOS `INT 13h` | Relies on UEFI firmware |

### Modern Analogies

| Amiga Concept | Modern Equivalent | Explanation |
|---|---|---|
| **RDB (Rigid Disk Block)** | GPT (GUID Partition Table) | Both allow a massive number of partitions and store complex metadata. |
| **Boot Block (1024 bytes)** | VBR (Volume Boot Record) | The OS-specific loader code sitting inside a specific partition. |
| **FileSysHdr / LSEG in RDB** | Linux `initramfs` | Filesystem drivers loaded from the disk *before* the root filesystem is mounted. |
| **AutoConfig + DiagArea** | UEFI Option ROMs | Expansion cards automatically inject their drivers into the firmware's database at boot. |
| **BootPri** | UEFI Boot Order | Numbered priority list determining which device boots first. |

---

## MiSTer / FPGA Notes

FPGA Amiga cores (MiSTer, Minimig, PiStorm) emulate the Gayle IDE interface to present `.hdf` files stored on an SD card as virtual hard drives.

- **HDF compatibility** — MiSTer expects RDB-partitioned `.hdf` files. Create them with `rdbtool` or WinUAE. The core maps the HDF file to the emulated Gayle registers at `$DA0000`.

- **ADF mounting** — Floppy images (`.adf`) are mapped to the emulated `trackdisk.device` — Paula's disk DMA reads from the ADF file as if it were a physical track.

- **SCSI emulation** — Some cores provide a virtual SCSI controller for higher performance; this bypasses the Gayle PIO bottleneck and can theoretically deliver higher throughput since the "DMA" is just a memory copy on the FPGA.

- **MaxTransfer** — The Gayle `MaxTransfer` issue applies to MiSTer's Gayle emulation too. Set `$0001FE00` in the RDB to avoid corruption, even though the "hardware" is emulated.

---

## References

- **NDK 3.9**: `devices/trackdisk.h`, `devices/scsidisk.h`, `dos/filehandler.h`
- **ADCD 2.1**: `Devices_Manual_guide/TrackDisk`, `Devices_Manual_guide/SCSI`
- **amitools**: https://github.com/cnvogelg/amitools — `rdbtool`, `xdftool`, `romtool`
- See also: [Cold Boot](cold_boot.md) — what happens before disk access
- See also: [DOS Boot](dos_boot.md) — bootblock format and `dos.library` handoff
- See also: [Kickstart Init](kickstart_init.md) — how device drivers are initialized
- See also: [Early Startup](early_startup.md) — manual boot device selection
- See also: [Gayle IDE & PCMCIA](../01_hardware/common/gayle_ide_pcmcia.md) — Gayle register layout
- See also: [AutoConfig](../01_hardware/common/autoconfig.md) — Zorro bus and expansion ROM protocol
- See also: [SCSI](../10_devices/scsi.md) — `scsi.device` driver interface and `HD_SCSICMD`
- See also: [ATAPI](../10_devices/atapi.md) — ATA protocol, ATAPI packets, CF card details
- See also: [Filesystem](../07_dos/filesystem.md) — RDB structure, FFS/OFS block layout, PFS3/SFS comparison
- See also: [Custom Loaders and DRM](../05_reversing/custom_loaders_and_drm.md) — custom floppy trackloaders
