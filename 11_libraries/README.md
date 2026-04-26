[← Home](../README.md)

# Common Libraries — Overview

Shared libraries beyond the core exec/dos/graphics/intuition subsystems. These provide utility functions, file format parsing, hardware expansion support, and Workbench integration.

## Section Index

| File | Description |
|---|---|
| [utility.md](utility.md) | TagItem lists with chaining (TAG_MORE), callback hooks (register convention), date/time utilities, tag iteration patterns |
| [expansion.md](expansion.md) | Zorro II/III bus architecture, AutoConfig ROM layout, board enumeration, FPGA implementation notes |
| [icon.md](icon.md) | Workbench icons (.info): DiskObject structure, ToolType parsing, icon types, OS 3.5+ true-color icons |
| [workbench.md](workbench.md) | Workbench integration: WBStartup handling, AppWindow drag-and-drop, AppIcon, AppMenuItem |
| [iffparse.md](iffparse.md) | IFF file parsing: ILBM/8SVX/ANIM, nested chunk hierarchy, ByteRun1 compression, PBM planar deinterleaving, clipboard integration, decision guide vs DataTypes |
| [locale.md](locale.md) | Internationalization: catalog system (.cd/.ct files), locale-aware date/number formatting, character classification |
| [keymap.md](keymap.md) | Keyboard mapping: raw-to-ASCII translation, KeyMap structure, dead keys, rawkey codes, national layouts |
| [rexxsyslib.md](rexxsyslib.md) | ARexx scripting: hosting ARexx ports, command parsing, sending commands, return codes |
| [mathffp.md](mathffp.md) | Motorola FFP and IEEE 754 floating point |
| [layers.md](layers.md) | Window clipping: ClipRect engine, Simple/Smart/Super refresh, damage repair, backfill hooks, layer locking |
| [diskfont.md](diskfont.md) | **Bitmap fonts deep dive: .font file format (FontContentsHeader), font descriptor files (DiskFontHeader), glyph bitmap layout, FONTS: assign, adding/installing fonts, bitmap vs TrueType/OpenType comparison, color fonts (OS 3.0+), Compugraphic outline fonts, AvailFonts enumeration, font loading pipeline** |
| [datatypes.md](datatypes.md) | DataTypes system: object-oriented file loading for images, sound, text, animation via BOOPSI classes |
| [amigaguide.md](amigaguide.md) | AmigaGuide hypertext help system: database format, @commands, API, ARexx integration, cross-database linking |
| [translator.md](translator.md) | translator.library: English-to-phonetic translation for speech synthesis, narrator.device integration, ARPABET phonemes |
