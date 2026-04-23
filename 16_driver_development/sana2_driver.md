[← Home](../README.md) · [Driver Development](README.md)

# Writing a SANA-II Network Device Driver

## Overview

A SANA-II driver is an Amiga device that implements the SANA-II specification. It provides the bridge between a TCP/IP stack (bsdsocket.library) and network hardware. This guide covers writing a complete SANA-II driver from scratch.

---

## Architecture

```
TCP/IP Stack (AmiTCP/Roadshow)
    ↓ OpenDevice("mynet.device", 0, ios2req, 0)
    ↓ CMD_READ / CMD_WRITE / S2_DEVICEQUERY / ...
SANA-II Device Driver (mynet.device)
    ↓ Hardware register access / DMA
Network Hardware (Ethernet NIC / FPGA bridge)
```

---

## Required Commands

Every SANA-II driver **must** implement these commands:

| Command | Code | Description |
|---|---|---|
| `CMD_READ` | 2 | Read a packet (async — queue and reply when packet arrives) |
| `CMD_WRITE` | 3 | Send a packet |
| `CMD_FLUSH` | 8 | Abort all pending I/O |
| `S2_DEVICEQUERY` | 9 | Report hardware capabilities |
| `S2_GETSTATIONADDRESS` | 10 | Return MAC address |
| `S2_CONFIGINTERFACE` | 11 | Set MAC address and bring up |
| `S2_ONLINE` | 14 | Bring interface online |
| `S2_OFFLINE` | 15 | Take interface offline |
| `S2_ADDMULTICASTADDRESS` | 16 | Join multicast group |
| `S2_DELMULTICASTADDRESS` | 17 | Leave multicast group |
| `S2_GETGLOBALSTATS` | 21 | Return packet statistics |
| `S2_ONEVENT` | 22 | Notify on event (link up/down) |
| `S2_READORPHAN` | 23 | Read unmatched packet types |

---

## struct IOSana2Req

```c
/* devices/sana2.h — NDK39/SANA-II Spec */
struct IOSana2Req {
    struct IORequest ios2_Req;
    ULONG  ios2_WireError;       /* wire-level error code */
    ULONG  ios2_PacketType;      /* Ethernet type (e.g. 0x0800 = IPv4) */
    UBYTE  ios2_SrcAddr[SANA2_MAX_ADDR_BYTES];  /* source MAC */
    UBYTE  ios2_DstAddr[SANA2_MAX_ADDR_BYTES];  /* destination MAC */
    ULONG  ios2_DataLength;      /* data length */
    APTR   ios2_Data;            /* packet data (via buffer management) */
    APTR   ios2_StatData;        /* statistics data pointer */
    APTR   ios2_BufferManagement; /* buffer mgmt hooks from stack */
};
```

---

## Buffer Management Hooks

The TCP/IP stack provides buffer copy functions via tags at OpenDevice time. Your driver **must** use these — never copy data directly:

```c
/* In your DevOpen: */
typedef BOOL (*CopyToBuff)(APTR to, APTR from, ULONG len);
typedef BOOL (*CopyFromBuff)(APTR to, APTR from, ULONG len);

struct BufferManagement {
    CopyToBuff   bm_CopyToBuff;
    CopyFromBuff bm_CopyFromBuff;
};

/* Parse tags from ios2req->ios2_BufferManagement: */
struct TagItem *tags = (struct TagItem *)ios2req->ios2_BufferManagement;
struct BufferManagement *bm = AllocMem(sizeof(*bm), MEMF_PUBLIC);
bm->bm_CopyToBuff   = (CopyToBuff)GetTagData(S2_CopyToBuff, 0, tags);
bm->bm_CopyFromBuff = (CopyFromBuff)GetTagData(S2_CopyFromBuff, 0, tags);
ios2req->ios2_BufferManagement = bm;
```

---

## Implementing CMD_READ (Receive Path)

```c
void CmdRead(struct IOSana2Req *ios2, struct MyDevBase *base)
{
    struct MyUnit *unit = (struct MyUnit *)ios2->ios2_Req.io_Unit;
    
    /* CMD_READ is ALWAYS async — queue the request */
    ios2->ios2_Req.io_Flags &= ~IOF_QUICK;
    
    Disable();
    /* Queue by packet type for fast dispatch on interrupt: */
    struct ReadQueue *rq = FindReadQueue(unit, ios2->ios2_PacketType);
    if (!rq) {
        rq = CreateReadQueue(unit, ios2->ios2_PacketType);
    }
    AddTail(&rq->rq_List, &ios2->ios2_Req.io_Message.mn_Node);
    Enable();
    
    /* Do NOT ReplyMsg — will be replied when a packet arrives */
}
```

---

## Implementing CMD_WRITE (Transmit Path)

```c
void CmdWrite(struct IOSana2Req *ios2, struct MyDevBase *base)
{
    struct MyUnit *unit = (struct MyUnit *)ios2->ios2_Req.io_Unit;
    struct BufferManagement *bm = ios2->ios2_BufferManagement;
    
    UBYTE txbuf[1536];  /* max Ethernet frame */
    ULONG len = ios2->ios2_DataLength;
    
    /* Build Ethernet header: */
    CopyMem(ios2->ios2_DstAddr, &txbuf[0], 6);   /* dest MAC */
    CopyMem(unit->mu_StationAddr, &txbuf[6], 6);  /* src MAC */
    txbuf[12] = (ios2->ios2_PacketType >> 8) & 0xFF;
    txbuf[13] = ios2->ios2_PacketType & 0xFF;
    
    /* Copy payload from stack's buffer: */
    bm->bm_CopyFromBuff(&txbuf[14], ios2->ios2_Data, len);
    
    /* Send to hardware: */
    HW_Transmit(unit, txbuf, len + 14);
    
    ios2->ios2_Req.io_Error = 0;
    TermIO(ios2);
}
```

---

## Interrupt Handler (Packet Arrival)

```c
/* Called when hardware signals packet received: */
LONG __saveds RxInterrupt(struct MyDevBase *base __asm("a1"))
{
    struct MyUnit *unit = base->md_Units[0];
    UBYTE rxbuf[1536];
    ULONG len;
    
    while (HW_HasPacket(unit)) {
        len = HW_ReceivePacket(unit, rxbuf, sizeof(rxbuf));
        
        UWORD ptype = (rxbuf[12] << 8) | rxbuf[13];
        
        /* Find a pending CMD_READ for this packet type: */
        struct ReadQueue *rq = FindReadQueue(unit, ptype);
        if (rq && !IsListEmpty(&rq->rq_List)) {
            struct IOSana2Req *ios2 =
                (struct IOSana2Req *)RemHead(&rq->rq_List);
            
            struct BufferManagement *bm = ios2->ios2_BufferManagement;
            bm->bm_CopyToBuff(ios2->ios2_Data, &rxbuf[14], len - 14);
            
            CopyMem(&rxbuf[6], ios2->ios2_SrcAddr, 6);
            ios2->ios2_DataLength = len - 14;
            ios2->ios2_Req.io_Error = 0;
            
            ReplyMsg(&ios2->ios2_Req.io_Message);
        } else {
            unit->mu_Stats.DroppedPackets++;
        }
    }
    return 0;
}
```

---

## S2_DEVICEQUERY Response

```c
void CmdDeviceQuery(struct IOSana2Req *ios2, struct MyDevBase *base)
{
    struct Sana2DeviceQuery *query = ios2->ios2_StatData;
    
    query->DevQueryFormat = 0;
    query->DeviceLevel    = 0;
    query->AddrFieldSize  = 48;    /* 48-bit MAC */
    query->MTU            = 1500;  /* Ethernet MTU */
    query->BPS            = 100000000;  /* 100 Mbps */
    query->HardwareType   = S2WireType_Ethernet;
    
    ios2->ios2_Req.io_Error = 0;
    TermIO(ios2);
}
```

---

## Building

```makefile
CFLAGS = -noixemul -m68000 -Os -fomit-frame-pointer
mynet.device: mynet.o
	$(CC) $(CFLAGS) -nostartfiles -o $@ $^
```

Install to `DEVS:Networks/mynet.device`.

---

## References

- SANA-II Network Device Driver Specification v2 (Commodore)
- NDK39: `devices/sana2.h`
- Example drivers: a2065.device source, plipbox driver
