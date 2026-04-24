[← Home](../README.md)

# Graphics Subsystem — Overview

The Amiga graphics system is built on custom DMA-driven hardware (Agnus/Alice + Denise/Lisa) managed through `graphics.library`. It supports planar bitmaps, hardware sprites, a Copper display coprocessor, and a Blitter for fast 2D operations. Three chipset generations (OCS → ECS → AGA) expanded resolution, colour depth, and bandwidth.

## Section Index

| File | Description |
|---|---|
| [gfx_base.md](gfx_base.md) | GfxBase structure, chipset detection (OCS/ECS/AGA), PAL/NTSC, display pipeline (MakeVPort/MrgCop/LoadView), blitter queue |
| [bitmap.md](bitmap.md) | BitMap structure, planar layout, allocation |
| [display_modes.md](display_modes.md) | Chipset comparison (OCS/ECS/AGA), ModeID system, PAL/NTSC timing, DMA slot budget |
| [ham_ehb_modes.md](ham_ehb_modes.md) | HAM6/HAM8 encoding pipeline, EHB half-brite, fringing, palette programming, FPGA decoder logic |
| [copper.md](copper.md) | Copper coprocessor, instruction format, UCopList |
| [copper_programming.md](copper_programming.md) | Copper deep dive: architecture, copper list construction, gradient and raster effects |
| [blitter.md](blitter.md) | Blitter DMA engine, minterms, BltBitMap |
| [blitter_programming.md](blitter_programming.md) | Blitter deep dive: minterms, cookie-cut masking, line draw, fill mode |
| [sprites.md](sprites.md) | Hardware sprites: DMA engine, data format, attached 15-colour sprites, multiplexing, AGA enhancements, priority control |
| [rastport.md](rastport.md) | RastPort drawing context: draw modes, patterns, layer clipping, text pipeline, blitter minterms |
| [views.md](views.md) | View, ViewPort, MakeVPort, display construction |
| [text_fonts.md](text_fonts.md) | TextFont bitmap layout, baseline rendering, algorithmic styles, AvailFonts enumeration |
| [animation.md](animation.md) | AnimOb, BOB, VSprite, GEL system |
