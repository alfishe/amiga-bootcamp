[← Home](../README.md) · [Graphics](README.md)

# Display Modes — Display Database, ModeID, Monitor Specs

## Overview

OS 3.0+ provides a **display database** that abstracts monitor/chipset capabilities. Applications query available modes by `ModeID` rather than hardcoding `HIRES`/`LACE` flags.

---

## ModeID Format

A ModeID is a ULONG:
```
bits 31–16: Monitor ID
bits 15–0:  Mode within that monitor
```

| ModeID | Name | Resolution |
|---|---|---|
| `$00000000` | LORES | 320×256 (PAL) / 320×200 (NTSC) |
| `$00008000` | HIRES | 640×256/200 |
| `$00000004` | LORES-LACE | 320×512/400 |
| `$00008004` | HIRES-LACE | 640×512/400 |
| `$00080000` | SUPERHIRES | 1280×256 (ECS+) |
| `$00080004` | SUPERHIRES-LACE | 1280×512 |
| `$00039000` | DBLPAL-LORES | 320×256 (AGA scan-doubled) |
| `$00039004` | DBLPAL-HIRES | 640×256 (AGA) |
| `$00011000` | DBLNTSC-LORES | 320×200 (AGA) |

---

## Querying the Display Database

```c
/* graphics.library 39+ */
ULONG modeID = INVALID_ID;
struct DisplayInfo di;
struct DimensionInfo dims;

while ((modeID = NextDisplayInfo(modeID)) != INVALID_ID) {
    if (GetDisplayInfoData(NULL, (UBYTE *)&di, sizeof(di),
                           DTAG_DISP, modeID)) {
        if (GetDisplayInfoData(NULL, (UBYTE *)&dims, sizeof(dims),
                               DTAG_DIMS, modeID)) {
            Printf("ModeID $%08lx: %ldx%ld, %ld colours\n",
                    modeID,
                    dims.Nominal.MaxX - dims.Nominal.MinX + 1,
                    dims.Nominal.MaxY - dims.Nominal.MinY + 1,
                    1 << di.NotAvailable ? 0 : dims.MaxDepth);
        }
    }
}
```

---

## Best Mode Selection

```c
ULONG bestMode = BestModeIDA((struct TagItem[]){
    { BIDTAG_NominalWidth,  640 },
    { BIDTAG_NominalHeight, 480 },
    { BIDTAG_Depth,         8 },
    { TAG_DONE, 0 }
});
```

---

## References

- NDK39: `graphics/displayinfo.h`, `graphics/modeid.h`
- ADCD 2.1: `NextDisplayInfo`, `GetDisplayInfoData`, `BestModeIDA`
