[← Home](../README.md) · [Driver Development](README.md)

# Writing AHI Audio Drivers

## Overview

**AHI** (Audio Hardware Interface) is the standard retargetable audio system for AmigaOS. It abstracts audio hardware behind a uniform API, similar to how RTG abstracts graphics cards. AHI drivers are shared libraries that implement the AHI driver protocol.

---

## Architecture

```
Application
    ↓ ahi.device (OpenDevice, CMD_WRITE, etc.)
    ↓
AHI System
    ↓ Calls driver functions via function table
    ↓
AHI Audio Driver (.audio file)
    ↓ Programs hardware / DMA / codec
    ↓
Audio Hardware (Paula, sound card, FPGA audio, codec)
```

---

## Driver File Location

```
DEVS:AHI/myaudio.audio       ; the driver library
DEVS:AudioModes/myaudio      ; mode file (preferences)
```

---

## Required Driver Functions

| Function | LVO | Description |
|---|---|---|
| `AHIsub_AllocAudio` | −30 | Allocate hardware resources |
| `AHIsub_FreeAudio` | −36 | Free hardware resources |
| `AHIsub_Disable` | −42 | Disable audio interrupts |
| `AHIsub_Enable` | −48 | Enable audio interrupts |
| `AHIsub_Start` | −54 | Start playback/recording |
| `AHIsub_Update` | −60 | Update playback parameters |
| `AHIsub_Stop` | −66 | Stop playback/recording |
| `AHIsub_SetVol` | −72 | Set channel volume/panning |
| `AHIsub_SetFreq` | −78 | Set channel frequency |
| `AHIsub_SetSound` | −84 | Set channel sound data |
| `AHIsub_SetEffect` | −90 | Set audio effects |
| `AHIsub_LoadSound` | −96 | Load a sound into hardware |
| `AHIsub_UnloadSound` | −102 | Unload a sound |
| `AHIsub_GetAttr` | −108 | Query driver capabilities |
| `AHIsub_HardwareControl` | −114 | Hardware-specific control |

---

## AHIsub_AllocAudio

```c
ULONG AHIsub_AllocAudio(struct AHIAudioCtrlDrv *audioctrl,
                          struct TagItem *tags)
{
    /* Allocate hardware resources */
    struct MyDriverData *dd = AllocMem(sizeof(*dd), MEMF_PUBLIC|MEMF_CLEAR);
    audioctrl->ahiac_DriverData = dd;
    
    /* Set up interrupt for mixing: */
    dd->dd_Interrupt.is_Node.ln_Type = NT_INTERRUPT;
    dd->dd_Interrupt.is_Node.ln_Pri  = 0;
    dd->dd_Interrupt.is_Node.ln_Name = "myaudio";
    dd->dd_Interrupt.is_Code         = (APTR)PlaybackInterrupt;
    dd->dd_Interrupt.is_Data         = audioctrl;
    
    /* Report capabilities: */
    return AHISF_CANRECORD |    /* can record */
           AHISF_KNOWSTEREO |  /* knows stereo */
           AHISF_MIXING;       /* uses AHI's software mixing */
}
```

---

## AHIsub_Start — Begin Playback

```c
ULONG AHIsub_Start(ULONG flags, struct AHIAudioCtrlDrv *audioctrl)
{
    struct MyDriverData *dd = audioctrl->ahiac_DriverData;
    
    if (flags & AHISF_PLAY) {
        /* Allocate DMA buffer: */
        dd->dd_MixBuffer = AllocMem(audioctrl->ahiac_BuffSamples * 4,
                                     MEMF_CHIP | MEMF_CLEAR);
        
        /* Set up timer interrupt for mixing callback: */
        /* Timer fires at: audioctrl->ahiac_PlayerFreq */
        dd->dd_TimerReq->tr_time.tv_micro =
            1000000 / audioctrl->ahiac_PlayerFreq;
        
        /* Start the interrupt-driven playback loop: */
        AddIntServer(INTB_VERTB, &dd->dd_Interrupt);
    }
    return AHIE_OK;
}
```

---

## Playback Interrupt — The Mixing Callback

```c
LONG __saveds PlaybackInterrupt(struct AHIAudioCtrlDrv *audioctrl __asm("a1"))
{
    struct MyDriverData *dd = audioctrl->ahiac_DriverData;
    
    /* Call AHI's software mixer to fill our buffer: */
    CallHookPkt(audioctrl->ahiac_PlayerFunc, audioctrl, NULL);
    CallHookPkt(audioctrl->ahiac_MixerFunc, audioctrl, dd->dd_MixBuffer);
    
    /* dd->dd_MixBuffer now contains mixed PCM data */
    /* Feed it to hardware DMA / codec / FPGA: */
    HW_SetDMAPointer(dd->dd_HWBase, dd->dd_MixBuffer);
    HW_SetDMALength(dd->dd_HWBase, audioctrl->ahiac_BuffSamples);
    
    return 0;
}
```

---

## AHIsub_GetAttr — Report Capabilities

```c
LONG AHIsub_GetAttr(ULONG attribute, LONG argument, LONG default_val,
                     struct TagItem *tags, struct AHIBase *AHIBase)
{
    switch (attribute) {
        case AHIDB_Bits:         return 16;  /* 16-bit audio */
        case AHIDB_MaxChannels:  return 2;   /* stereo */
        case AHIDB_Frequencies:  return 4;   /* number of supported rates */
        case AHIDB_Frequency:
            switch (argument) {
                case 0: return 22050;
                case 1: return 44100;
                case 2: return 48000;
                case 3: return 96000;
            }
            break;
        case AHIDB_Author:       return (LONG)"My Name";
        case AHIDB_Copyright:    return (LONG)"(C) 2026";
        case AHIDB_Version:      return (LONG)"myaudio 1.0";
        case AHIDB_Annotation:   return (LONG)"FPGA audio driver";
        case AHIDB_Record:       return TRUE;
        case AHIDB_FullDuplex:   return TRUE;
        case AHIDB_MinMixFreq:   return 8000;
        case AHIDB_MaxMixFreq:   return 96000;
    }
    return default_val;
}
```

---

## Audio Mode Registration

Create `DEVS:AudioModes/myaudio`:
```
;; AHI audio mode file
BEGIN
    Name        "MyAudio:HiFi 16 bit stereo++"
    Driver      "DEVS:AHI/myaudio.audio"
    Flags       0
    Frequency   44100 48000 96000
END
```

---

## References

- AHI Developer's Guide (Martin Blom)
- AHI SDK: Aminet `dev/misc/ahidev.lha`
- Example: `paula.audio` driver source (AHI distribution)
