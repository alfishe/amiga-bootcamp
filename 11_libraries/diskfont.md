[← Home](../README.md) · [Libraries](README.md)

# diskfont.library — Disk-Based Fonts

## Overview

`diskfont.library` loads bitmap fonts from disk (the `FONTS:` assign). ROM fonts (topaz 8, topaz 9) are always available; all others require this library.

---

## Loading a Disk Font

```c
struct Library *DiskfontBase = OpenLibrary("diskfont.library", 0);

struct TextAttr ta = {"helvetica.font", 24, 0, 0};
struct TextFont *font = OpenDiskFont(&ta);
if (font) {
    SetFont(rp, font);
    /* ... render ... */
    CloseFont(font);
}

CloseLibrary(DiskfontBase);
```

---

## Font Directory Structure

```
FONTS:
  helvetica.font      ← font descriptor file
  helvetica/
    24                 ← bitmap data for size 24
    11                 ← bitmap data for size 11
```

---

## Listing Available Fonts

```c
struct List *fontList = NULL;
LONG count = AvailFonts(buf, bufsize, AFF_DISK | AFF_MEMORY);
struct AvailFontsHeader *afh = (struct AvailFontsHeader *)buf;
struct AvailFonts *af = (struct AvailFonts *)&afh[1];
for (int i = 0; i < afh->afh_NumEntries; i++) {
    Printf("%s %ld\n", af[i].af_Attr.ta_Name, af[i].af_Attr.ta_YSize);
}
```

---

## References

- NDK39: `diskfont/diskfont.h`
