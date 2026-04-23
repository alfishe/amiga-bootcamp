[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# OCS Custom Register Map

Base address: `$00DFF000`. All registers are 16-bit (word) wide. Byte access is valid for the appropriate byte lane.

Legend: **R** = read, **W** = write, **RW** = read-write, **S** = strobe (write triggers action)

## DMA and Interrupt Control

| Offset | Name | Dir | Description |
|---|---|---|---|
| $002 | DMACONR | R | DMA control register (read) |
| $01C | INTENAR | R | Interrupt enable (read) |
| $01E | INTREQR | R | Interrupt request (read) |
| $096 | DMACON | W | DMA control (write: bit15=SET/CLR) |
| $09A | INTENA | W | Interrupt enable (write: bit15=SET/CLR) |
| $09C | INTREQ | W | Interrupt request — ack / force |

## Beam Position (Read Only)

| Offset | Name | Dir | Description |
|---|---|---|---|
| $004 | VPOSR | R | Vertical position high, LOF bit |
| $006 | VHPOSR | R | Vertical + horizontal beam position |
| $007 | VHPOS | R | Horizontal beam position (byte) |

## Copper

| Offset | Name | Dir | Description |
|---|---|---|---|
| $02E | COPCON | W | Copper control (CDANG bit) |
| $080 | COP1LCH | W | Copper list 1 pointer high |
| $082 | COP1LCL | W | Copper list 1 pointer low |
| $084 | COP2LCH | W | Copper list 2 pointer high |
| $086 | COP2LCL | W | Copper list 2 pointer low |
| $088 | COPJMP1 | S | Restart Copper from list 1 |
| $08A | COPJMP2 | S | Restart Copper from list 2 |
| $08C | COPINS | W | Copper instruction (direct write) |
| $000 | BLTDDAT | R | Blitter dest early read (Copper use) |

## Blitter

| Offset | Name | Dir | Description |
|---|---|---|---|
| $040 | BLTCON0 | W | Blitter control 0 (minterm, channels) |
| $042 | BLTCON1 | W | Blitter control 1 (line mode, fill) |
| $044 | BLTAFWM | W | First word mask, channel A |
| $046 | BLTALWM | W | Last word mask, channel A |
| $048 | BLTCPTH | W | Channel C pointer high |
| $04A | BLTCPTL | W | Channel C pointer low |
| $04C | BLTBPTH | W | Channel B pointer high |
| $04E | BLTBPTL | W | Channel B pointer low |
| $050 | BLTAPTH | W | Channel A pointer high |
| $052 | BLTAPTL | W | Channel A pointer low |
| $054 | BLTDPTH | W | Destination pointer high |
| $056 | BLTDPTL | W | Destination pointer low |
| $058 | BLTSIZE | W | Blitter size + start (height×64 + width) |
| $060 | BLTCMOD | W | Channel C modulo |
| $062 | BLTBMOD | W | Channel B modulo |
| $064 | BLTAMOD | W | Channel A modulo |
| $066 | BLTDMOD | W | Destination modulo |
| $070 | BLTCDAT | W | Channel C data register |
| $072 | BLTBDAT | W | Channel B data register |
| $074 | BLTADAT | W | Channel A data register |

## Bitplane Pointers

| Offset | Name | Dir | Description |
|---|---|---|---|
| $0E0 | BPL1PTH | W | Bitplane 1 pointer high |
| $0E2 | BPL1PTL | W | Bitplane 1 pointer low |
| $0E4 | BPL2PTH | W | Bitplane 2 pointer high |
| $0E6 | BPL2PTL | W | Bitplane 2 pointer low |
| $0E8 | BPL3PTH | W | Bitplane 3 pointer high |
| $0EA | BPL3PTL | W | Bitplane 3 pointer low |
| $0EC | BPL4PTH | W | Bitplane 4 pointer high |
| $0EE | BPL4PTL | W | Bitplane 4 pointer low |
| $0F0 | BPL5PTH | W | Bitplane 5 pointer high |
| $0F2 | BPL5PTL | W | Bitplane 5 pointer low |
| $0F4 | BPL6PTH | W | Bitplane 6 pointer high |
| $0F6 | BPL6PTL | W | Bitplane 6 pointer low |

## Bitplane Control

| Offset | Name | Dir | Description |
|---|---|---|---|
| $100 | BPLCON0 | W | Bitplane control 0 (depth, HAM, HIRES, LACE) |
| $102 | BPLCON1 | W | Bitplane scroll (fine scroll values) |
| $104 | BPLCON2 | W | Sprite vs bitplane priority |
| $108 | BPL1MOD | W | Bitplane modulo (odd planes) |
| $10A | BPL2MOD | W | Bitplane modulo (even planes) |
| $110 | BPL1DAT | W | Bitplane 1 data register |
| $112 | BPL2DAT | W | Bitplane 2 data register |
| $114 | BPL3DAT | W | Bitplane 3 |
| $116 | BPL4DAT | W | Bitplane 4 |
| $118 | BPL5DAT | W | Bitplane 5 |
| $11A | BPL6DAT | W | Bitplane 6 |

**BPLCON0 bit layout:**
```
bit 15:    HIRES  (1 = 640 pixel wide)
bit 14-12: BPU2-0 (number of bitplanes: 0–6)
bit 11:    HAM    (1 = Hold-And-Modify mode)
bit 10:    DPF    (dual playfield)
bit  9:    COLOR  (0 = monochrome, 1 = colour)
bit  8:    GAUD   (genlock audio)
bit  7-4:  (various, OCS = 0)
bit  1:    ERSY   (external sync)
bit  0:    ECSENA (ECS enable — must be 0 on OCS)
```

## Display Window and Fetch

| Offset | Name | Dir | Description |
|---|---|---|---|
| $08E | DIWSTRT | W | Display window start (V and H start) |
| $090 | DIWSTOP | W | Display window stop |
| $092 | DDFSTRT | W | Display data fetch start |
| $094 | DDFSTOP | W | Display data fetch stop |

## Sprite Pointers and Data

| Offset | Name | Dir | Description |
|---|---|---|---|
| $120 | SPR0PTH | W | Sprite 0 pointer high |
| $122 | SPR0PTL | W | Sprite 0 pointer low |
| ... | ... | | Sprites 1–7 follow at +4 each |
| $13E | SPR7PTL | W | Sprite 7 pointer low |
| $140 | SPR0POS | W | Sprite 0 position |
| $142 | SPR0CTL | W | Sprite 0 control |
| $144 | SPR0DATA | W | Sprite 0 image data word A |
| $146 | SPR0DATB | W | Sprite 0 image data word B |
| ... | | | Sprites 1–7 follow |
| $178 | SPR7DATB | W | Sprite 7 image data word B |

## Audio Registers

| Offset | Name | Dir | Description |
|---|---|---|---|
| $0A0 | AUD0LCH | W | Audio ch 0 pointer high |
| $0A2 | AUD0LCL | W | Audio ch 0 pointer low |
| $0A4 | AUD0LEN | W | Audio ch 0 length (words) |
| $0A6 | AUD0PER | W | Audio ch 0 period (clock divider) |
| $0A8 | AUD0VOL | W | Audio ch 0 volume (0–64) |
| $0AA | AUD0DAT | W | Audio ch 0 data (direct, non-DMA) |
| ... | | | Channels 1–3 follow at +$10 |

## Serial Port

| Offset | Name | Dir | Description |
|---|---|---|---|
| $030 | SERDAT | W | Serial data and stop bits |
| $018 | SERDATR | R | Serial data receive and status |
| $032 | SERPER | W | Serial period and word length |

## Disk DMA

| Offset | Name | Dir | Description |
|---|---|---|---|
| $020 | DSKPTH | W | Disk pointer high |
| $022 | DSKPTL | W | Disk pointer low |
| $024 | DSKLEN | W | Disk length and write flag |
| $010 | ADKCONR | R | Audio / disk control (read) |
| $09E | ADKCON | W | Audio / disk control (write) |
| $07C | DSKSYNC | W | Disk sync word |

## Colour Registers

| Offset | Name | Dir | Description |
|---|---|---|---|
| $180 | COLOR00 | W | Background / colour 0 |
| $182 | COLOR01 | W | Colour 1 |
| ... | | | |
| $1BE | COLOR31 | W | Colour 31 |

OCS colours: 12-bit RGB (4 bits per component, $0RGB format).

## References

- *Amiga Hardware Reference Manual* 3rd ed. — Appendix B: Register Summary
- NDK39: `hardware/custom.h` — struct Custom definition
- http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node0000.html
