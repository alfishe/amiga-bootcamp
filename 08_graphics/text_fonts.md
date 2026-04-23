[← Home](../README.md) · [Graphics](README.md)

# Text and Fonts — TextFont, TextAttr, OpenFont, Text

## Overview

AmigaOS uses bitmap fonts rendered through `graphics.library`. Fonts are described by `TextAttr` (request) and `TextFont` (loaded instance). Disk fonts require `diskfont.library`.

---

## Key Structures

```c
/* graphics/text.h — NDK39 */
struct TextAttr {
    STRPTR  ta_Name;    /* font name, e.g. "topaz.font" */
    UWORD   ta_YSize;   /* desired height in pixels */
    UBYTE   ta_Style;   /* FSF_BOLD, FSF_ITALIC, FSF_UNDERLINED */
    UBYTE   ta_Flags;   /* FPF_ROMFONT, FPF_DISKFONT, etc. */
};

struct TextFont {
    struct Message tf_Message;
    UWORD   tf_YSize;      /* font height */
    UBYTE   tf_Style;
    UBYTE   tf_Flags;
    UWORD   tf_XSize;      /* nominal width */
    UWORD   tf_Baseline;   /* baseline from top */
    UWORD   tf_BoldSmear;  /* bold smear width */
    UWORD   tf_Accessors;  /* open count */
    UBYTE   tf_LoChar;     /* first character code */
    UBYTE   tf_HiChar;     /* last character code */
    APTR    tf_CharData;   /* bitmap data */
    UWORD   tf_Modulo;     /* bytes per row of font bitmap */
    APTR    tf_CharLoc;    /* character location table */
    APTR    tf_CharSpace;  /* proportional spacing table */
    APTR    tf_CharKern;   /* kerning table */
};
```

---

## Opening Fonts

```c
/* ROM font (topaz, always available): */
struct TextAttr ta = {"topaz.font", 8, 0, FPF_ROMFONT};
struct TextFont *font = OpenFont(&ta);

/* Disk font (requires diskfont.library): */
struct TextAttr ta2 = {"helvetica.font", 24, 0, FPF_DISKFONT};
struct TextFont *font2 = OpenDiskFont(&ta2);

/* Set in RastPort: */
SetFont(rp, font);
```

---

## Rendering Text

```c
Move(rp, 10, 20);             /* position cursor */
Text(rp, "Hello Amiga", 11);  /* render 11 characters */

/* Get pixel width of a string: */
UWORD width = TextLength(rp, "Hello", 5);
```

---

## Style Flags

```c
#define FSF_UNDERLINED  0x01
#define FSF_BOLD        0x02
#define FSF_ITALIC      0x04
#define FSF_EXTENDED    0x08

/* Set algorithmic style: */
SetSoftStyle(rp, FSF_BOLD | FSF_ITALIC,
             AskSoftStyle(rp));  /* ask which styles the font supports */
```

---

## References

- NDK39: `graphics/text.h`
- ADCD 2.1: `OpenFont`, `OpenDiskFont`, `SetFont`, `Text`, `TextLength`
