[← Home](../README.md) · [References](README.md)

# Custom Chip Register Map

## Overview

All Amiga custom chip registers are memory-mapped at base address `$DFF000`. This is the complete register map for OCS/ECS/AGA.

---

## Register Table

| Offset | Name | R/W | Description |
|---|---|---|---|
| `$000` | `BLTDDAT` | R | Blitter destination early read |
| `$002` | `DMACONR` | R | DMA control read |
| `$004` | `VPOSR` | R | Beam position (V high bits + LOF) |
| `$006` | `VHPOSR` | R | Beam position (V low + H) |
| `$008` | `DSKDATR` | R | Disk data early read |
| `$00A` | `JOY0DAT` | R | Joystick/mouse port 0 |
| `$00C` | `JOY1DAT` | R | Joystick/mouse port 1 |
| `$00E` | `CLXDAT` | R | Collision detection |
| `$010` | `ADKCONR` | R | Audio/disk control read |
| `$012` | `POT0DAT` | R | Pot port 0 data |
| `$014` | `POT1DAT` | R | Pot port 1 data |
| `$016` | `POTGOR` | R | Pot port data read |
| `$018` | `SERDATR` | R | Serial port data + status |
| `$01A` | `DSKBYTR` | R | Disk data byte + status |
| `$01C` | `INTENAR` | R | Interrupt enable read |
| `$01E` | `INTREQR` | R | Interrupt request read |
| `$020` | `DSKPTH` | W | Disk DMA pointer (high) |
| `$022` | `DSKPTL` | W | Disk DMA pointer (low) |
| `$024` | `DSKLEN` | W | Disk DMA length |
| `$026` | `DSKDAT` | W | Disk DMA data write |
| `$028` | `REFPTR` | W | Refresh pointer |
| `$02A` | `VPOSW` | W | Beam position write (V) |
| `$02C` | `VHPOSW` | W | Beam position write (H) |
| `$02E` | `COPCON` | W | Copper control |
| `$030` | `SERDAT` | W | Serial port data write |
| `$032` | `SERPER` | W | Serial port period/control |
| `$034` | `POTGO` | W | Pot port control |
| `$036` | `JOYTEST` | W | Joystick counter test |
| `$038` | `STREQU` | S | Short frame strobe (ECS) |
| `$03A` | `STRVBL` | S | Vertical blank strobe (ECS) |
| `$03C` | `STRHOR` | S | Horizontal sync strobe (ECS) |
| `$03E` | `STRLONG` | S | Long frame strobe (ECS) |
| `$040` | `BLTCON0` | W | Blitter control 0 |
| `$042` | `BLTCON1` | W | Blitter control 1 |
| `$044` | `BLTAFWM` | W | Blitter A first word mask |
| `$046` | `BLTALWM` | W | Blitter A last word mask |
| `$048` | `BLTCPTH` | W | Blitter C pointer (high) |
| `$04A` | `BLTCPTL` | W | Blitter C pointer (low) |
| `$04C` | `BLTBPTH` | W | Blitter B pointer (high) |
| `$04E` | `BLTBPTL` | W | Blitter B pointer (low) |
| `$050` | `BLTAPTH` | W | Blitter A pointer (high) |
| `$052` | `BLTAPTL` | W | Blitter A pointer (low) |
| `$054` | `BLTDPTH` | W | Blitter D pointer (high) |
| `$056` | `BLTDPTL` | W | Blitter D pointer (low) |
| `$058` | `BLTSIZE` | W | Blitter size (starts blit) |
| `$05A` | `BLTCON0L` | W | Blitter control 0 (lower bits, ECS) |
| `$05C` | `BLTSIZV` | W | Blitter V size (ECS) |
| `$05E` | `BLTSIZH` | W | Blitter H size (ECS, starts blit) |
| `$060` | `BLTCMOD` | W | Blitter C modulo |
| `$062` | `BLTBMOD` | W | Blitter B modulo |
| `$064` | `BLTAMOD` | W | Blitter A modulo |
| `$066` | `BLTDMOD` | W | Blitter D modulo |
| `$070` | `BLTCDAT` | W | Blitter C data |
| `$072` | `BLTBDAT` | W | Blitter B data |
| `$074` | `BLTADAT` | W | Blitter A data |
| `$078` | `SPRHDAT` | W | Ext sprite data (ECS) |
| `$07C` | `DENISEID` | R | Denise/Lisa chip ID (ECS/AGA) |
| `$07E` | `DSKSYNC` | W | Disk sync pattern |
| `$080`–`$08C` | `COP1LCH`–`COP2LCL` | W | Copper list 1/2 pointers |
| `$088` | `COPJMP1` | S | Copper jump strobe 1 |
| `$08A` | `COPJMP2` | S | Copper jump strobe 2 |
| `$08C` | `COPINS` | W | Copper instruction fetch |
| `$08E` | `DIWSTRT` | W | Display window start |
| `$090` | `DIWSTOP` | W | Display window stop |
| `$092` | `DDFSTRT` | W | Data fetch start |
| `$094` | `DDFSTOP` | W | Data fetch stop |
| `$096` | `DMACON` | W | DMA control write |
| `$098` | `CLXCON` | W | Collision control |
| `$09A` | `INTENA` | W | Interrupt enable |
| `$09C` | `INTREQ` | W | Interrupt request |
| `$09E` | `ADKCON` | W | Audio/disk control |
| `$0A0`–`$0D8` | `AUD0–3` | W | Audio channels (PTH/PTL/LEN/PER/VOL/DAT) |
| `$0E0`–`$0FE` | `BPL1PTH`–`BPL8PTL` | W | Bitplane pointers 1–8 |
| `$100` | `BPLCON0` | W | Bitplane control 0 |
| `$102` | `BPLCON1` | W | Bitplane control 1 (scroll) |
| `$104` | `BPLCON2` | W | Bitplane control 2 (priority) |
| `$106` | `BPLCON3` | W | Bitplane control 3 (AGA) |
| `$108` | `BPL1MOD` | W | Bitplane modulo (odd planes) |
| `$10A` | `BPL2MOD` | W | Bitplane modulo (even planes) |
| `$10C` | `BPLCON4` | W | Bitplane control 4 (AGA) |
| `$110`–`$11E` | `BPL1DAT`–`BPL8DAT` | W | Bitplane data |
| `$120`–`$13E` | `SPR0PTH`–`SPR7PTL` | W | Sprite pointers 0–7 |
| `$140`–`$17E` | `SPR0POS`–`SPR7DATB` | W | Sprite position/control/data |
| `$180`–`$1BE` | `COLOR00`–`COLOR31` | W | Color palette registers |
| `$1C0` | `HTOTAL` | W | H total (ECS) |
| `$1C2` | `HSSTOP` | W | H sync stop (ECS) |
| `$1C4` | `HBSTRT` | W | H blank start (ECS) |
| `$1C6` | `HBSTOP` | W | H blank stop (ECS) |
| `$1C8` | `VTOTAL` | W | V total (ECS) |
| `$1CA` | `VSSTOP` | W | V sync stop (ECS) |
| `$1CC` | `VBSTRT` | W | V blank start (ECS) |
| `$1CE` | `VBSTOP` | W | V blank stop (ECS) |
| `$1DC` | `BEAMCON0` | W | Beam counter control (ECS) |
| `$1DE` | `HSSTRT` | W | H sync start (ECS) |
| `$1E0` | `VSSTRT` | W | V sync start (ECS) |
| `$1E4` | `DIWHIGH` | W | Display window high bits (ECS) |
| `$1FC` | `FMODE` | W | Fetch mode (AGA) |

---

## DMA Enable Bits (DMACON)

| Bit | Name | Description |
|---|---|---|
| 0 | `AUD0EN` | Audio channel 0 |
| 1 | `AUD1EN` | Audio channel 1 |
| 2 | `AUD2EN` | Audio channel 2 |
| 3 | `AUD3EN` | Audio channel 3 |
| 4 | `DSKEN` | Disk DMA |
| 5 | `SPREN` | Sprite DMA |
| 6 | `BLTEN` | Blitter DMA |
| 7 | `COPEN` | Copper DMA |
| 8 | `BPLEN` | Bitplane DMA |
| 9 | `DMAEN` | Master DMA enable |
| 10 | `BLTPRI` | Blitter priority (nasty) |
| 15 | `SET/CLR` | Set/clear control |

---

## Interrupt Bits (INTENA/INTREQ)

| Bit | Name | Description |
|---|---|---|
| 0 | `TBE` | Serial transmit buffer empty |
| 1 | `DSKBLK` | Disk block finished |
| 2 | `SOFT` | Software interrupt |
| 3 | `PORTS` | CIA-A (I/O ports, timers) |
| 4 | `COPER` | Copper |
| 5 | `VERTB` | Vertical blank |
| 6 | `BLIT` | Blitter finished |
| 7 | `AUD0` | Audio channel 0 |
| 8 | `AUD1` | Audio channel 1 |
| 9 | `AUD2` | Audio channel 2 |
| 10 | `AUD3` | Audio channel 3 |
| 11 | `RBF` | Serial receive buffer full |
| 12 | `DSKSYN` | Disk sync word found |
| 13 | `EXTER` | CIA-B (parallel, serial) |
| 14 | `INTEN` | Master interrupt enable |
| 15 | `SET/CLR` | Set/clear control |

---

## References

- HRM: *Amiga Hardware Reference Manual* — complete register descriptions
- NDK39: `hardware/custom.h`, `hardware/dmabits.h`, `hardware/intbits.h`
