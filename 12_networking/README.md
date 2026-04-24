[← Home](../README.md)

# Networking — Overview

AmigaOS has no built-in TCP/IP stack. Third-party stacks (AmiTCP, Miami, Roadshow) provide `bsdsocket.library` — a BSD-compatible socket API in user-space. Network hardware is abstracted via the SANA-II device driver standard.

## Section Index

| File | Description |
|---|---|
| [tcp_ip_stacks.md](tcp_ip_stacks.md) | Stack architecture: Amiga vs Unix model, SANA-II integration, PPP/SLIP dial-up, modem setup, Ethernet cards, MiSTer virtual NIC, detailed stack comparison |
| [bsdsocket.md](bsdsocket.md) | BSD socket API: per-task library base, LVO table, WaitSelect with Exec signals, error handling, BSD/POSIX differences |
| [sana2.md](sana2.md) | SANA-II driver specification: buffer management hooks, send/receive patterns, device query, driver requirements |
| [protocols.md](protocols.md) | Protocol implementation: DNS resolution, TCP client/server, WaitSelect integration, UDP, DHCP sequence |
