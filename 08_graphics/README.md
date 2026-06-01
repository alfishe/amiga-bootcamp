[← Home](../README.md)

# Graphics Subsystem — Overview

The Amiga graphics system is built on custom DMA-driven hardware (Agnus/Alice + Denise/Lisa) managed through `graphics.library`. It supports planar bitmaps, hardware sprites, a Copper display coprocessor, and a Blitter for fast 2D operations. Three chipset generations (OCS → ECS → AGA) expanded resolution, color depth, and bandwidth.

## Section Index

| File | Description |
|---|---|
| [gfx_base.md](gfx_base.md) | GfxBase structure, chipset detection (OCS/ECS/AGA), PAL/NTSC, display pipeline (MakeVPort/MrgCop/LoadView), blitter queue |
| [bitmap.md](bitmap.md) | BitMap structure, planar layout, allocation |
| [display_modes.md](display_modes.md) | Full chipset comparison, ModeID selection flowchart, CRT vs flat-panel, interlace/progressive tradeoffs, named antipatterns, FPGA/MiSTer impact, historical context, modern analogies, FAQ |
| [ham_ehb_modes.md](ham_ehb_modes.md) | HAM6/HAM8 encoding pipeline, EHB half-brite, fringing, palette programming, FPGA decoder logic |
| [copper.md](copper/copper.md) | Copper coprocessor, instruction format, UCopList |
| [copper_programming.md](copper/copper_programming.md) | Copper deep dive: architecture, copper list construction, gradient and raster effects |
| [copper_reference.md](copper/copper_reference.md) | Copper ISA complete reference: full encoding, control registers, timing, register map, debugging |
| [blitter.md](blitter/blitter.md) | Blitter DMA engine, minterms, BltBitMap |
| [blitter_programming.md](blitter/blitter_programming.md) | Blitter deep dive: minterms, cookie-cut masking, line draw, fill mode |
| [sprites.md](sprites.md) | Hardware sprites: DMA engine, data format, attached 15-color sprites, multiplexing, AGA enhancements, priority control |
| [rastport.md](rastport.md) | RastPort drawing context: draw modes, patterns, layer clipping, text pipeline, blitter minterms |
| [views.md](views.md) | View + ViewPort pipeline: 3-stage Mermaid diagram, ViewPort chaining (split screens), ColorMap/LoadRGB4, named antipatterns, Copper vs Views decision flowchart, modern GPU analogies |
| [text_fonts.md](text_fonts.md) | TextFont bitmap layout, baseline rendering, algorithmic styles, AvailFonts, ColorTextFont, Compugraphic outlines, font scaling, 3 cookbooks, 4 antipatterns, 6 FAQ |
| [pixel_conversion.md](pixel_conversion.md) | Chunky ↔ Planar conversion deep dive: naive, merge/butterfly (Kalms), Copper Chunky, Akiko hardware, Blitter-assisted, RTG bypass, SoA/AoS theory, GPU swizzle modern parallels |
| [animation.md](animation.md) | GEL system deep dive: BOBs, VSprites, AnimObs, hardware foundation (Blitter/Copper/Sprite interaction), collision detection, double buffering, performance tuning |
| [rtg_programming.md](rtg_programming.md) | Retargetable Graphics (CyberGraphX/Picasso96): LockBitMapTags VRAM access, pixel formats, double buffering, bus bandwidth, 16-card catalog, 5 antipatterns, dirty-rect optimization, modern analogies, 6 FAQ |
