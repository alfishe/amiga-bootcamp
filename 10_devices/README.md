[← Home](../README.md)

# Devices — Overview

Amiga devices are shared libraries with an exec I/O request interface. They provide standardised access to hardware peripherals via `OpenDevice`/`CloseDevice` and `DoIO`/`SendIO` patterns.

## Section Index

| File | Description |
|---|---|
| [trackdisk.md](trackdisk.md) | Floppy disk DMA: MFM encoding, track format, disk geometry, track caching, direct HW access |
| [scsi.md](scsi.md) | scsi.device / 2nd.scsi.device — hard disk I/O |
| [serial.md](serial.md) | UART/RS-232: CIA registers, baud rate calculation, serial debugging (KPrintF) |
| [parallel.md](parallel.md) | parallel.device — Centronics parallel port |
| [timer.md](timer.md) | CIA timers, E-clock, VBlank: delays, ReadEClock, periodic patterns, signal-based waiting |
| [audio.md](audio.md) | 4-channel DMA audio: hardware registers, priority allocation, double-buffering, modulation |
| [keyboard.md](keyboard.md) | CIA-A serial handshake, raw key codes, key matrix, reset sequence, FPGA protocol notes |
| [gameport.md](gameport.md) | gameport.device — joystick/mouse port reading |
| [input.md](input.md) | Input handler chain: priority dispatch, event classes, key remapping, Commodities Exchange |
| [console.md](console.md) | console.device — text terminal I/O |
