[← Home](../README.md) · [Driver Development](README.md)

# Writing Picasso96/RTG Display Drivers

## Overview

**RTG** (Retargetable Graphics) allows the Amiga to use non-native display hardware (graphics cards). The two major RTG systems are **Picasso96** and **CyberGraphX**. Both use a board driver model where a `.card` file provides hardware-specific acceleration.

---

## Architecture

```
Application
    ↓ graphics.library / cybergraphics.library / Picasso96API
    ↓
RTG System (P96 or CGX)
    ↓ Calls board driver functions
    ↓
Board Driver (.card file)
    ↓ Programs hardware registers
    ↓
Graphics Card Hardware (Cirrus, S3, Permedia, FPGA framebuffer...)
```

---

## Picasso96 Board Driver Interface

A P96 board driver is a shared library exposing specific functions:

### Required Functions

| Function | Description |
|---|---|
| `FindCard(boardInfo)` | Detect and identify the graphics card |
| `InitCard(boardInfo)` | Initialise card, set up memory map |
| `SetSwitch(boardInfo, state)` | Switch between Amiga native and RTG display |
| `SetColorArray(boardInfo, start, count)` | Set palette entries |
| `SetDAC(boardInfo, type)` | Configure DAC mode |
| `SetGC(boardInfo, modeInfo, border)` | Set graphics context (resolution, depth) |
| `SetPanning(boardInfo, addr, w, x, y)` | Set display start address (scrolling) |
| `SetDisplay(boardInfo, state)` | Enable/disable display output |

### Optional Acceleration Functions

| Function | Description |
|---|---|
| `BlitRect(boardInfo, ri, x1, y1, x2, y2, w, h, mask, mode)` | Accelerated rectangle blit |
| `FillRect(boardInfo, ri, x, y, w, h, pen, mask, mode)` | Accelerated rectangle fill |
| `InvertRect(boardInfo, ri, x, y, w, h, mask, mode)` | Accelerated rectangle invert |
| `BlitRectNoMaskComplete(...)` | Blit without mask |
| `BlitTemplate(...)` | Text/pattern blit |
| `DrawLine(...)` | Accelerated line drawing |
| `SetSprite(boardInfo, state)` | Hardware sprite control |
| `SetSpritePosition(boardInfo, x, y)` | Move hardware sprite |
| `SetSpriteImage(boardInfo, ...)` | Set sprite image data |
| `SetSpriteColor(boardInfo, idx, r, g, b)` | Set sprite palette |

---

## struct BoardInfo

```c
/* P96 BoardInfo — key fields */
struct BoardInfo {
    UBYTE          *MemoryBase;      /* card framebuffer base */
    ULONG           MemorySize;      /* framebuffer size */
    UBYTE          *RegisterBase;    /* MMIO register base */
    ULONG           BoardType;       /* board type ID */
    UBYTE          *ChipBase;        /* chip register base */
    
    /* Function pointers (set by driver): */
    APTR            SetSwitch;
    APTR            SetColorArray;
    APTR            SetDAC;
    APTR            SetGC;
    APTR            SetPanning;
    APTR            SetDisplay;
    APTR            WaitVerticalSync;
    
    /* Acceleration (NULL = software fallback): */
    APTR            BlitRect;
    APTR            FillRect;
    APTR            InvertRect;
    APTR            DrawLine;
    APTR            BlitTemplate;
    APTR            BlitRectNoMaskComplete;
    
    /* Sprite: */
    APTR            SetSprite;
    APTR            SetSpritePosition;
    APTR            SetSpriteImage;
    APTR            SetSpriteColor;
    
    /* Display mode database: */
    struct ModeInfo *ModeInfoList;
    
    /* Color palette (256 entries): */
    UBYTE           CLUT[256 * 3];
    
    /* ... many more fields ... */
};
```

---

## Minimal FindCard Implementation

```c
BOOL FindCard(struct BoardInfo *bi)
{
    struct ConfigDev *cd = NULL;
    
    /* Scan Zorro bus for our card: */
    cd = FindConfigDev(cd, MY_MANUFACTURER_ID, MY_PRODUCT_ID);
    if (!cd) return FALSE;
    
    bi->MemoryBase   = cd->cd_BoardAddr;
    bi->MemorySize   = cd->cd_BoardSize;
    bi->RegisterBase = cd->cd_BoardAddr + REGISTER_OFFSET;
    
    return TRUE;
}
```

---

## Minimal InitCard Implementation

```c
BOOL InitCard(struct BoardInfo *bi)
{
    /* Set up function pointers: */
    bi->SetSwitch    = (APTR)MySetSwitch;
    bi->SetColorArray = (APTR)MySetColorArray;
    bi->SetDAC       = (APTR)MySetDAC;
    bi->SetGC        = (APTR)MySetGC;
    bi->SetPanning   = (APTR)MySetPanning;
    bi->SetDisplay   = (APTR)MySetDisplay;
    
    /* Optional acceleration: */
    bi->FillRect     = (APTR)MyFillRect;
    bi->BlitRect     = (APTR)MyBlitRect;
    
    /* Register display modes: */
    AddResolution(bi, 640, 480, 8);   /* 640x480 256 colours */
    AddResolution(bi, 800, 600, 16);  /* 800x600 16-bit */
    AddResolution(bi, 1024, 768, 24); /* 1024x768 24-bit */
    
    /* Reset hardware: */
    HW_Reset(bi->RegisterBase);
    
    return TRUE;
}
```

---

## SetSwitch — Native ↔ RTG Toggle

```c
BOOL MySetSwitch(struct BoardInfo *bi, BOOL state)
{
    if (state) {
        /* Switch TO RTG display */
        HW_EnableOutput(bi->RegisterBase);
        /* Disable Amiga native display if using pass-through: */
        custom.dmacon = DMAF_RASTER;  /* turn off bitplane DMA */
    } else {
        /* Switch BACK to Amiga native */
        HW_DisableOutput(bi->RegisterBase);
        custom.dmacon = DMAF_SETCLR | DMAF_RASTER;
    }
    return state;
}
```

---

## Installation

```
DEVS:Monitors/mycard.card     ; the board driver
DEVS:Monitors/mycard          ; monitor file (text config)
```

---

## References

- Picasso96 SDK (P96 developer documentation)
- CyberGraphX SDK
- Example: UAE RTG driver (`uaegfx.card` source)
