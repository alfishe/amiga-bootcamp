[← Home](../README.md) · [Libraries](README.md)

# iffparse.library — IFF File Parsing

## Overview

IFF (Interchange File Format) is EA/Commodore's universal container format. `iffparse.library` provides stream-oriented parsing/writing of IFF files. Common IFF types: ILBM (images), 8SVX (audio), ANIM (animation), FTXT (formatted text).

---

## IFF Structure

```
FORM <size> <type>
  <chunk_id> <size> <data...>
  <chunk_id> <size> <data...>
  ...
```

All values are big-endian. Chunks are padded to even byte boundaries.

---

## Key Functions

```c
struct Library *IFFParseBase = OpenLibrary("iffparse.library", 0);
struct IFFHandle *iff = AllocIFF();

/* Open from file: */
iff->iff_Stream = (ULONG)Open("image.iff", MODE_OLDFILE);
InitIFFasDOS(iff);
OpenIFF(iff, IFFF_READ);

/* Register chunks we want to stop at: */
StopChunk(iff, ID_ILBM, ID_BMHD);
StopChunk(iff, ID_ILBM, ID_BODY);
StopChunk(iff, ID_ILBM, ID_CMAP);

/* Parse: */
LONG error;
while ((error = ParseIFF(iff, IFFPARSE_SCAN)) == 0) {
    struct ContextNode *cn = CurrentChunk(iff);
    switch (cn->cn_ID) {
        case ID_BMHD:
            ReadChunkBytes(iff, &bmhd, sizeof(bmhd));
            break;
        case ID_CMAP:
            ReadChunkBytes(iff, palette, cn->cn_Size);
            break;
        case ID_BODY:
            ReadChunkBytes(iff, bodydata, cn->cn_Size);
            break;
    }
}

CloseIFF(iff);
Close((BPTR)iff->iff_Stream);
FreeIFF(iff);
```

---

## Common Chunk IDs

| FORM Type | Chunk | Description |
|---|---|---|
| `ILBM` | `BMHD` | Bitmap header (width, height, depth) |
| `ILBM` | `CMAP` | Colour map (R,G,B triples) |
| `ILBM` | `BODY` | Image body data |
| `ILBM` | `CAMG` | Amiga display mode |
| `8SVX` | `VHDR` | Voice header |
| `8SVX` | `BODY` | Audio sample data |
| `ANIM` | `ANHD` | Animation header |
| `ANIM` | `DLTA` | Delta frame data |

---

## References

- NDK39: `libraries/iffparse.h`, `datatypes/pictureclass.h`
