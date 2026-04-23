[← Home](../README.md) · [Devices](README.md)

# audio.device — DMA Audio Channels

## Overview

`audio.device` provides access to the Amiga's 4 DMA audio channels. Each channel plays 8-bit PCM samples from Chip RAM at programmable rates.

---

## Channel Allocation

```c
UBYTE allocationMap[] = { 1, 2, 4, 8 }; /* channel masks */
struct IOAudio *aio = (struct IOAudio *)
    CreateIORequest(port, sizeof(struct IOAudio));
aio->ioa_Request.io_Message.mn_Node.ln_Pri = 0;
aio->ioa_Data    = allocationMap;
aio->ioa_Length  = sizeof(allocationMap);
OpenDevice("audio.device", 0, (struct IORequest *)aio, 0);
/* aio->ioa_AllocKey = allocation key for this channel */
```

---

## Playing a Sample

```c
aio->ioa_Request.io_Command = CMD_WRITE;
aio->ioa_Request.io_Flags   = ADIOF_PERVOL;
aio->ioa_Data    = sampleData;    /* MUST be in Chip RAM */
aio->ioa_Length  = sampleLength;  /* in bytes */
aio->ioa_Period  = 428;           /* ~8287 Hz (PAL) */
aio->ioa_Volume  = 64;           /* 0–64 */
aio->ioa_Cycles  = 1;            /* 0 = loop forever */
BeginIO((struct IORequest *)aio);
```

### Period Calculation

```
Period = clock_constant / desired_frequency
PAL:  clock = 3546895 Hz → Period = 3546895 / freq
NTSC: clock = 3579545 Hz → Period = 3579545 / freq
```

| Frequency | Period (PAL) |
|---|---|
| 8287 Hz | 428 |
| 11025 Hz | 322 |
| 22050 Hz | 161 |
| 28867 Hz | 124 (minimum safe) |

---

## Channel Registers

| Channel | Address | Description |
|---|---|---|
| 0 | `$DFF0A0` | AUD0 (left) |
| 1 | `$DFF0B0` | AUD1 (right) |
| 2 | `$DFF0C0` | AUD2 (right) |
| 3 | `$DFF0D0` | AUD3 (left) |

Each channel: pointer (PTH/PTL), length (LEN), period (PER), volume (VOL).

---

## References

- NDK39: `devices/audio.h`
- HRM: audio DMA chapter
