[← Home](../../README.md) · [Hardware](../README.md)

# Zorro Bus — Expansion Architecture

## Overview

The Amiga uses the **Zorro** expansion bus for add-on cards. There are two generations:

- **Zorro II** — 16-bit, 24-bit addressing, 7 MHz, compatible with A2000/A3000/A4000
- **Zorro III** — 32-bit, 32-bit addressing, up to 33 MHz burst, A3000/A4000 only

Zorro uses **AutoConfig** — a standardised plug-and-play configuration protocol that predates PCI by several years.

## Zorro II

| Parameter | Value |
|---|---|
| Data bus | 16-bit |
| Address bus | 24-bit |
| Clock | 7.14 MHz (bus cycle ≈ 280 ns) |
| Max transfer | ~5 MB/s (DMA) |
| Address space | $A00000–$EFFFFF (I/O), $200000–$9FFFFF (RAM) |
| Slots | 5 (A2000), 3 (A3000) |

Zorro II cards appear in the 16 MB address space. RAM cards are configured into $200000–$9FFFFF. I/O cards use $A00000–$DEFFFF.

## Zorro III

| Parameter | Value |
|---|---|
| Data bus | 32-bit |
| Address bus | 32-bit |
| Clock | Up to 33 MHz burst |
| Max transfer | ~40 MB/s (DMA) |
| Address space | $01000000 and above |
| Slots | 4 (A3000), 5 (A4000) |

Zorro III extends into the 32-bit address space, allowing large RAM cards (32–128 MB) and fast peripherals. Requires a 32-bit CPU (68030+) and OS support.

## AutoConfig

Zorro uses **AutoConfig** — a hardware plug-and-play protocol that lets the OS discover, size, and map expansion boards at boot without jumpers. Each board presents a 256-byte ROM at the configuration address (`$E80000` for Zorro II, `$FF000000` for Zorro III) containing its manufacturer ID, product code, size, and type. The OS walks the `/CFGIN`/`/CFGOUT` daisy chain, reads each ROM, assigns a base address, and tells the board to relocate.

See [AutoConfig Protocol](autoconfig.md) for the full hardware-level specification — CFGIN/CFGOUT mechanics, nibble-pair ROM format, size codes, shut-up behavior, and FPGA implementation notes. See [expansion.library](../../11_libraries/expansion.md) for the software API (`FindConfigDev`, `ConfigBoard`, `ConfigDev` structure) and manufacturer ID tables.

## Real-World Performance & Bottlenecks

While the theoretical speeds are high, real-world Zorro performance is often gated by the Amiga's system bus controller and motherboard design.

### The "Buster" Bottleneck
In the A3000 and A4000, the **Buster** chip manages Zorro III traffic. 
- **Revision 9**: Contained bugs that made Zorro III DMA unstable or slow.
- **Revision 11**: The "Golden" revision. It fixed several timing bugs and allowed for reliable **Burst Mode** transfers, which are essential for reaching speeds above 10 MB/s.

### Bandwidth Comparison (Real-World)

| Interface | Effective CPU-to-VRAM | Notes |
|---|---|---|
| **Zorro II** | ~2.5 – 3.5 MB/s | Gated by 7 MHz 68000 bus timing. |
| **Zorro III** | ~10 – 15 MB/s | Requires Buster 11 and a 68040/060. |
| **PCI Bridge** | ~20 – 30 MB/s | Limited by the Zorro-to-PCI bridge interface. |
| **Local Bus** | **~60 – 80 MB/s** | Bypasses Zorro; uses CPU-slot (CyberStorm PPC). |

### 2. PCI Bridgeboards (Mediator, G-REX, Prometheus)
PCI bridges allowed the Amiga to break out of the aging Zorro ecosystem and tap into the vast, cheap pool of PC hardware.

#### Hardware Architecture
*   **Mediator (Elbox)**: The most popular solution. It consists of a "Logic Board" (containing GALs/CPLDs) and a "Busboard." It uses a **Memory Windowing** technique (typically 8MB) to map the vast 4GB PCI address space into the Amiga's 24-bit or 32-bit space.
*   **G-REX (DCE)**: Designed for high-end PowerPC systems. It connects directly to the **CPU local slot** of a BlizzardPPC or CyberStormPPC. Unlike the Mediator, it uses **Linear Mapping**, making the entire PCI memory space directly addressable without window switching, resulting in superior performance.
*   **Prometheus (Mayap/Individual Computers)**: A simpler Zorro III-to-PCI bridge using a single PLX bridge chip.

#### Software & Libraries
*   **pci.library**: The standard API for PCI hardware on the Amiga. It handles resource allocation (BARs), interrupt routing, and device discovery.
*   **OpenPCI**: An open-source alternative library designed to provide a unified driver interface across different bridge brands.
*   **Mediator Multimedia CD**: The proprietary driver suite from Elbox, required for many of their advanced features (like using a graphics card's VRAM as system Fast RAM).

#### Supported PCI Cards
| Category | Supported Models | Notable Drivers |
|---|---|---|
| **Graphics** | 3dfx Voodoo 3/4/5, ATI Radeon 9200/9250, S3 ViRGE | Picasso96, CyberGraphX v4 |
| **Sound** | Sound Blaster 128, ESS Solo-1, ForteMedia FM801 | AHI (Amiga Hardware Interface) |
| **Networking** | Realtek 8139 (10/100 Mbps) | SANA-II (Roadshow, Genesis) |
| **USB** | NEC-based cards (e.g., Elbox Spider) | Poseidon USB Stack |
| **TV/Video** | Brooktree Bt848/878 based cards | TVPaint, VGR |

> [!TIP]
> **Mediator VRAM trick**: One of the most powerful features of the Mediator is the ability to use the 128MB+ of RAM on a Radeon card as system Fast RAM. While slower than local motherboard RAM, it is significantly faster than swapping to a hard drive.

### 3. FPGA-Based Modern Cards
Modern Zorro cards like the **MNT ZZ9000** use an FPGA to provide RTG, Ethernet, and USB. They often include an ARM processor or specialized hardware logic to perform operations (like JPEG decoding) locally on the card, reducing the amount of raw data that needs to be sent over the Zorro bus.

*   **Product Page**: [MNT ZZ9000](https://mntre.com/zz9000)
*   **Official Sources (GitLab)**: [Firmware & Drivers](https://source.mnt.re/amiga)

## References

- NDK39: `libraries/expansion.h`, `libraries/configregs.h`, `libraries/configvars.h`
- ADCD 2.1 Autodocs: `expansion` — http://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node025B.html
- *Amiga Hardware Reference Manual* 3rd ed. — AutoConfig chapter
- Dave Haynie's Zorro III specification documents
- Mediator PCI Technical Reference — http://www.elbox.com/mediator_tech.html

## See Also

- [Bus Architecture](bus_architecture.md) — Bus hierarchy, PCI bridge address windowing, register access, cross-domain transfers
- [AutoConfig Protocol](autoconfig.md) — Board enumeration, CFGIN/CFGOUT, ExpansionRom encoding
- [Address Space](address_space.md) — Full 24-bit/32-bit Amiga address maps
- [Gary System Controller (OCS)](../ocs_a500/gary_system_controller.md) — A500/A2000 bus glue, Buster interaction
- [Gary System Controller (ECS)](../ecs_a600_a3000/gary_system_controller.md) — A3000 Fat Gary, Zorro III via Super Buster

