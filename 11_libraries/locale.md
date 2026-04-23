[← Home](../README.md) · [Libraries](README.md)

# locale.library — Internationalisation

## Overview

`locale.library` (OS 2.1+) provides language-aware string lookup, date/number formatting, and character classification for internationalised applications.

---

## Core Pattern

```c
struct Library *LocaleBase = OpenLibrary("locale.library", 38);
struct Catalog *cat = OpenCatalog(NULL, "myapp.catalog",
                                  OC_BuiltInLanguage, "english",
                                  TAG_DONE);

/* Get localised string: */
STRPTR str = GetCatalogStr(cat, MSG_HELLO, "Hello");  /* fallback */

CloseCatalog(cat);
CloseLibrary(LocaleBase);
```

---

## Locale-Aware Formatting

```c
struct Locale *loc = OpenLocale(NULL);  /* user's default */

/* Format a date: */
FormatDate(loc, "%A %e %B %Y", &datestamp, &hook);

/* Format a number: */
/* Uses loc->loc_GroupSeparator, loc->loc_DecimalPoint */

CloseLocale(loc);
```

---

## References

- NDK39: `libraries/locale.h`
