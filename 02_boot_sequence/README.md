[← Home](../README.md)

# Boot Sequence — Overview

From power-on to Workbench desktop: hardware init, ROM validation, kernel creation, device enumeration, boot block execution, and startup scripts.

## Section Index

| File | Description |
|---|---|
| [cold_boot.md](cold_boot.md) | Power-on to Kickstart: CPU reset vectors, ROM checksum, hardware reset, memory detection, diagnostic indicators, capture vectors |
| [kickstart_rom.md](kickstart_rom.md) | **Kickstart ROM internals: binary structure, module inventory, extraction tools, custom ROM building, EPROM burning** |
| [kickstart_init.md](kickstart_init.md) | ExecBase creation, capture vectors, resident module scan algorithm, 4-phase initialization, bootstrap handoff |
| [dos_boot.md](dos_boot.md) | strap module, boot block format and execution, MountList/DOSDrivers, system assigns, Startup-Sequence walkthrough |
| [early_startup.md](early_startup.md) | Early Startup Control menu: boot device selection, display mode override, recovery scenarios |
