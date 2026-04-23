[← Home](../README.md) · [Libraries](README.md)

# layers.library — Window Clipping Layers

## Overview

`layers.library` provides the clipping and damage-repair infrastructure that Intuition windows are built on. Each window's `RastPort` is backed by a `Layer` that manages overlapping regions.

---

## Layer Types

| Flag | Type | Description |
|---|---|---|
| `LAYERSIMPLE` | Simple Refresh | Application must redraw damaged areas |
| `LAYERSMART` | Smart Refresh | System saves obscured regions |
| `LAYERSUPER` | Super BitMap | Application provides full-size bitmap |
| `LAYERBACKDROP` | Backdrop | Behind all other layers |

---

## Key Functions

```c
struct Layer_Info *li = NewLayerInfo();

struct Layer *layer = CreateUpfrontLayer(li, bitmap,
    x1, y1, x2, y2, LAYERSMART, NULL);

/* Lock before drawing: */
LockLayer(0, layer);
/* ... draw into layer->rp ... */
UnlockLayer(layer);

/* Move: */
MoveLayer(0, layer, dx, dy);

/* Resize: */
SizeLayer(0, layer, dw, dh);

/* Cleanup: */
DeleteLayer(0, layer);
DisposeLayerInfo(li);
```

---

## References

- NDK39: `graphics/layers.h`, `graphics/clip.h`
