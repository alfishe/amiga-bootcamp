[← Home](../README.md) · [Networking](README.md)

# TCP/IP Stacks — AmiTCP, Miami, Roadshow

## Overview

AmigaOS has no built-in TCP/IP stack. Third-party stacks provide `bsdsocket.library`. All stacks present the same API to applications — only configuration and driver support differ.

---

## Stack Comparison

| Feature | AmiTCP 3.0b2 | Miami 3.2 | Roadshow 1.15 |
|---|---|---|---|
| License | Free (Genesis fork) | Commercial | Commercial (demo available) |
| API version | bsdsocket.library v3 | v4 | v4 |
| IPv6 | No | No | No |
| PPP | Via serial | Built-in | Via driver |
| DHCP | External (dhclient) | Built-in | Built-in |
| DNS cache | No | Yes | Yes |
| SANA-II | Yes | Yes | Yes |
| GUI config | MUI prefs | Miami prefs | Roadshow prefs |
| Active development | No | No | Yes (Olaf Barthel) |
| MiSTer recommended | ✅ (free) | — | ✅ (most capable) |

---

## Configuration (Roadshow)

```
; DEVS:NetInterfaces/prism2
DEVICE=prism2.device
UNIT=0
IPTYPE=DHCP
; or:
; ADDRESS=192.168.1.100
; NETMASK=255.255.255.0
; GATEWAY=192.168.1.1

; DEVS:NetInterfaces/lo0
DEVICE=lo0.device
UNIT=0
ADDRESS=127.0.0.1
NETMASK=255.0.0.0
```

---

## Configuration (AmiTCP)

```
; AmiTCP:db/interfaces
prism2 DEV=DEVS:Networks/prism2.device UNIT=0 IP=DHCP

; AmiTCP:db/netdb-myhost
HOST 127.0.0.1 localhost
NAMESERVER 8.8.8.8
DOMAIN local
```

---

## References

- Roadshow SDK: http://roadshow.apc-tcp.de/
- AmiTCP SDK: Aminet `comm/tcp/AmiTCP-SDK-4.3.lha`
