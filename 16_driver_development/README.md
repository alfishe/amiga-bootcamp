[← Home](../README.md)

# Driver Development — Overview

Technical reference for developing hardware drivers on AmigaOS. Covers the exec.device framework, RTG graphics card drivers (Picasso96/CyberGraphX), SANA-II network drivers, and AHI audio drivers.

## Section Index

| File | Description |
|---|---|
| [device_driver_basics.md](device_driver_basics.md) | exec.device framework — IORequest lifecycle, BeginIO/AbortIO, unit management |
| [rtg_driver.md](rtg_driver.md) | Picasso96/RTG driver architecture — SetFunction patching, BoardInfo hooks, VRAM/CRTC management, signal routing, Native driver, compatibility issues, system tuning |
| [sana2_driver.md](sana2_driver.md) | SANA-II network device driver specification |
| [ahi_driver.md](ahi_driver.md) | AHI retargetable audio driver interface |
