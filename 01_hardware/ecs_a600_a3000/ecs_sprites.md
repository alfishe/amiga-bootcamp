[← Home](../../README.md) · [Hardware](../README.md) · [ECS](README.md)

# ECS Sprite Enhancements

## Overview

ECS Denise (MOS 8373) extends the [OCS sprite hardware](../ocs_a500/sprites.md) with three register-level enhancements while maintaining full backward compatibility. All eight sprite DMA channels, data formats, and color mapping rules remain identical to OCS — ECS adds control over **where** sprites appear and **at what resolution** they render.

## What Changed from OCS

| Feature | OCS (Denise 8362) | ECS (Denise 8373) | Register |
|---|---|---|---|
| Border visibility | Sprites clipped to display window | Sprites visible in border area | `BPLCON3` bit 3 |
| Pixel resolution | Tied to playfield mode | Independent: lores/hires/shres | `BPLCON3` bits 7-6 |
| Color bank select | Fixed: COLOR16–COLOR31 | Upper bits selectable (AGA prep) | `BPLCON3` bits 15-13 |

---

## BPLCON3 Sprite Bits ($DFF106)

All ECS sprite enhancements are controlled through the `BPLCON3` register. On OCS hardware, this register does not exist — writes are silently ignored.

```
bit 15-13:  BANK2:0     Sprite color bank select (upper bits of color index)
bit  7-6:   SPRES1:0    Sprite resolution
bit  3:     BRDSPRT     Enable sprites in border area
```

### SPRES — Independent Sprite Resolution

ECS decouples sprite pixel width from the playfield display mode. This allows sprites to have a different pixel clock than the background:

| SPRES1:0 | Pixel Width | Pixel Clock | Use Case |
|---|---|---|---|
| `00` | Follow playfield | — | OCS-compatible default |
| `01` | Lores (140ns) | ~7.09 MHz | Large, chunky sprites on hires backgrounds |
| `10` | Hires (70ns) | ~14.18 MHz | Fine-detail sprites on lores backgrounds |
| `11` | Super-hires (35ns) | ~28.37 MHz | Maximum resolution sprites (productivity modes) |

```asm
; Set sprites to hires resolution independent of playfield
    move.w  #$0080, $DFF106     ; BPLCON3: SPRES1:0 = %10 (hires)
```

> [!NOTE]
> SPRES affects the **horizontal pixel resolution** of all 8 sprite channels globally. Individual per-sprite resolution is not possible.

### BRDSPRT — Border Sprite Enable

On OCS, sprites outside the display window boundaries (`DIWSTRT`/`DIWSTOP`) are clipped. ECS allows sprites to appear in the overscan border area:

```asm
; Enable sprites in border region
    move.w  #$0008, $DFF106     ; BPLCON3: BRDSPRT = 1
```

This is useful for status bars, score displays, or HUD elements positioned outside the scrolling playfield.

### BANK — Sprite Color Bank (AGA Preparation)

BPLCON3 bits 15-13 provide upper bits for the sprite color register index. On ECS hardware these bits have limited practical use (only 32 color registers exist), but they establish the register interface that AGA's [256-color sprite palette](../aga_a1200_a4000/aga_sprites.md) builds upon.

---

## "Half-ECS" Trap

> [!WARNING]
> Many Amigas shipped with **ECS Agnus** (Super Agnus 8372A) but **OCS Denise** (8362). This configuration — common in late A500 boards and some A2000 revisions — provides 2 MB Chip RAM addressing but **no sprite enhancements**. Writing to `BPLCON3` on these machines has no effect.
>
> Always check for ECS Denise specifically:
> ```c
> if (GfxBase->ChipRevBits0 & (1 << GFXB_HR_DENISE)) {
>     /* Safe to use BPLCON3 sprite features */
> }
> ```

---

## Programming Notes

- All ECS sprite changes are backward-compatible: leaving `BPLCON3` at `$0000` gives identical behavior to OCS
- `SPRES` only affects horizontal resolution — vertical resolution is always 1 pixel per scanline
- `BRDSPRT` works with both standard and attached sprites
- Sprite DMA format, pointer registers, and collision detection (`CLXCON`/`CLXDAT`) are unchanged from OCS

## See Also

- [OCS Sprite Hardware](../ocs_a500/sprites.md) — base register reference (SPRxPOS/CTL/DATA, color mapping)
- [AGA Sprite Enhancements](../aga_a1200_a4000/aga_sprites.md) — wider sprites, FMODE, 256-color palette banks
- [Sprites — Graphics Programming Guide](../../08_graphics/sprites.md) — OS API, techniques, antipatterns
- [ECS Chipset Internals](chipset_ecs.md) — Super Agnus and ECS Denise overview
- [ECS Register Deltas](ecs_registers_delta.md) — complete BPLCON3 bit definition

## References

- *Amiga Hardware Reference Manual* 3rd ed. — Appendix F (ECS extensions)
- ADCD 2.1 Hardware Manual — ECS Denise sprite section
- NDK39: `hardware/custom.h` — BPLCON3 definition
