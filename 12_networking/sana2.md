[← Home](../README.md) · [Networking](README.md)

# SANA-II — Standard Amiga Network Architecture

## Overview

SANA-II is the standard device driver interface for network hardware on AmigaOS. It defines a uniform API that TCP/IP stacks use to communicate with any network card (Ethernet, WiFi, PPP, etc.).

---

## Architecture

```
Application
    ↓
bsdsocket.library (TCP/IP stack)
    ↓
SANA-II device driver (e.g., prism2.device, a2065.device)
    ↓
Network hardware
```

---

## Opening a SANA-II Device

```c
struct IOSana2Req *s2req = (struct IOSana2Req *)
    CreateIORequest(port, sizeof(struct IOSana2Req));

/* Provide buffer management hooks: */
static struct TagItem s2tags[] = {
    { S2_CopyToBuff,   (ULONG)CopyToBuff },
    { S2_CopyFromBuff, (ULONG)CopyFromBuff },
    { TAG_DONE, 0 }
};
s2req->ios2_BufferManagement = s2tags;

OpenDevice("a2065.device", 0, (struct IORequest *)s2req, 0);
```

---

## Commands

| Code | Constant | Description |
|---|---|---|
| 2 | `CMD_READ` | Read a packet |
| 3 | `CMD_WRITE` | Send a packet |
| 9 | `S2_DEVICEQUERY` | Query hardware capabilities |
| 10 | `S2_GETSTATIONADDRESS` | Get MAC address |
| 11 | `S2_CONFIGINTERFACE` | Configure interface (set MAC) |
| 14 | `S2_ONLINE` | Bring interface online |
| 15 | `S2_OFFLINE` | Take interface offline |
| 21 | `S2_GETGLOBALSTATS` | Get packet statistics |
| 16 | `S2_ADDMULTICASTADDRESS` | Add multicast address |
| 17 | `S2_DELMULTICASTADDRESS` | Remove multicast address |

---

## Packet Reading

```c
s2req->ios2_Req.io_Command = CMD_READ;
s2req->ios2_WireError = 0;
s2req->ios2_PacketType = 0x0800;  /* IPv4 */
SendIO((struct IORequest *)s2req);
/* wait for packet... */
WaitIO((struct IORequest *)s2req);
/* s2req->ios2_Data* contains the received packet */
```

---

## References

- SANA-II Network Device Driver Specification (Commodore)
- NDK39: `devices/sana2.h`
