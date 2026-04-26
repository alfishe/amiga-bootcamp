[← Home](../README.md)

# Devices — Overview

Amiga devices are shared libraries with an exec I/O request interface. They provide standardised access to hardware peripherals via `OpenDevice`/`CloseDevice` and `DoIO`/`SendIO` patterns.

## Section Index

| File | Description |
|---|---|
| [trackdisk.md](trackdisk.md) | Floppy disk DMA: MFM encoding, track format, disk geometry, track caching, direct HW access |
| [scsi.md](scsi.md) | Hard disk/CD-ROM I/O: per-model interfaces, Gayle bandwidth limits, native vs vendor drivers, HD_SCSICMD, CD-ROM commands, TD64/NSD 64-bit |
| [serial.md](serial.md) | UART/RS-232: CIA registers, baud rate calculation, serial debugging (KPrintF) |
| [parallel.md](parallel.md) | Centronics parallel port: CIA-A Port B mapping, hardware pinout, direct register access |
| [timer.md](timer.md) | CIA timers, E-clock, VBlank: delays, ReadEClock, periodic patterns, signal multiplexing, resource exhaustion |
| [audio.md](audio.md) | 4-channel DMA audio: Paula architecture, DMA slot budget, named antipatterns, use-case cookbook, decision flowchart (audio.device vs direct HW), FPGA/MiSTer impact, cross-platform comparison |
| [keyboard.md](keyboard.md) | CIA-A serial handshake, raw key codes, key matrix, reset sequence, FPGA protocol notes |
| [gameport.md](gameport.md) | Joystick/mouse port: quadrature decoding, XOR state, fire buttons, controller types |
| [input.md](input.md) | Input handler chain: priority dispatch, event classes, key remapping, Commodities Exchange |
| [console.md](console.md) | Text terminal I/O: ANSI escape sequences, cursor/color control, raw key events, CON:/RAW: handlers |
