[← Home](../README.md) · [Intuition](README.md)

# Menus — MenuStrip Construction

## Overview

Intuition menus are structured as: `Menu` → `MenuItem` → `SubItem`. Menus are attached to windows and appear when the user presses the right mouse button.

---

## GadTools Menu Creation (OS 2.0+)

```c
struct NewMenu nm[] = {
    { NM_TITLE,  "Project",   NULL, 0, 0, NULL },
    {  NM_ITEM,  "New",       "N",  0, 0, NULL },
    {  NM_ITEM,  "Open...",   "O",  0, 0, NULL },
    {  NM_ITEM,  NM_BARLABEL, NULL, 0, 0, NULL },  /* separator */
    {  NM_ITEM,  "Quit",      "Q",  0, 0, NULL },
    { NM_TITLE,  "Edit",      NULL, 0, 0, NULL },
    {  NM_ITEM,  "Cut",       "X",  0, 0, NULL },
    {  NM_ITEM,  "Copy",      "C",  0, 0, NULL },
    {  NM_ITEM,  "Paste",     "V",  0, 0, NULL },
    { NM_END,    NULL,        NULL, 0, 0, NULL }
};

struct Menu *menu = CreateMenus(nm, TAG_DONE);
LayoutMenus(menu, vi, TAG_DONE);
SetMenuStrip(win, menu);

/* In event loop on IDCMP_MENUPICK: */
UWORD code = imsg->Code;
while (code != MENUNULL) {
    struct MenuItem *item = ItemAddress(menu, code);
    UWORD menuNum  = MENUNUM(code);
    UWORD itemNum  = ITEMNUM(code);
    UWORD subNum   = SUBNUM(code);
    /* process selection */
    code = item->NextSelect;
}

/* Cleanup: */
ClearMenuStrip(win);
FreeMenus(menu);
```

---

## Menu Selection Macros

```c
#define MENUNUM(code)   ((code) & 0x1F)        /* menu number (0–31) */
#define ITEMNUM(code)   (((code) >> 5) & 0x3F)  /* item number (0–63) */
#define SUBNUM(code)    (((code) >> 11) & 0x1F)  /* subitem number */
#define FULLMENUNUM(m,i,s) ((m)|((i)<<5)|((s)<<11))
#define MENUNULL        0xFFFF                   /* no selection */
```

---

## References

- NDK39: `libraries/gadtools.h`, `intuition/intuition.h`
- ADCD 2.1: `CreateMenus`, `LayoutMenus`, `SetMenuStrip`
