[← Home](../README.md) · [Intuition](README.md)

# Menus

## What Are Menus?

Menus are Intuition's pull-down command system. When the user presses the **right mouse button**, Intuition displays a menu strip attached to the active window's screen title bar. Menus are the primary mechanism for accessing application commands that don't warrant dedicated gadgets.

The menu system has three levels:

```mermaid
graph LR
    STRIP["Menu Strip"] --> M1["Menu: Project"]
    STRIP --> M2["Menu: Edit"]
    STRIP --> M3["Menu: Settings"]
    M1 --> I1["Item: New    (Ctrl+N)"]
    M1 --> I2["Item: Open   (Ctrl+O)"]
    M1 --> SEP["────────────"]
    M1 --> I3["Item: Quit   (Ctrl+Q)"]
    M2 --> I4["Item: Cut    (Ctrl+X)"]
    M2 --> I5["Item: Copy   (Ctrl+C)"]
    M2 --> I6["Item: Paste  (Ctrl+V)"]
    I6 --> S1["Sub: As Text"]
    I6 --> S2["Sub: As Image"]

    style STRIP fill:#e8f4fd,stroke:#2196f3,color:#333
```

| Level | Structure | Max Count | Description |
|---|---|---|---|
| **Menu** | `struct Menu` | 31 | Top-level categories (Project, Edit, etc.) |
| **Item** | `struct MenuItem` | 63 | Commands within a menu |
| **Sub-Item** | `struct MenuItem` | 31 | Nested commands within an item |

---

## GadTools Menu Creation (OS 2.0+)

The preferred way to create menus — handles layout, keyboard shortcuts, and the OS look-and-feel automatically:

### Defining the Menu Structure

```c
#include <libraries/gadtools.h>
#include <proto/gadtools.h>

/* Menu IDs — use an enum for clarity */
enum {
    MENU_NEW = 1, MENU_OPEN, MENU_SAVE, MENU_SAVEAS, MENU_QUIT,
    MENU_CUT, MENU_COPY, MENU_PASTE, MENU_SELECTALL,
    MENU_BOLD, MENU_ITALIC, MENU_UNDERLINE
};

struct NewMenu nm[] = {
    { NM_TITLE,  "Project",       NULL,  0, 0, NULL },
    {  NM_ITEM,  "New",           "N",   0, 0, (APTR)MENU_NEW },
    {  NM_ITEM,  "Open...",       "O",   0, 0, (APTR)MENU_OPEN },
    {  NM_ITEM,  "Save",          "S",   0, 0, (APTR)MENU_SAVE },
    {  NM_ITEM,  "Save As...",    "A",   0, 0, (APTR)MENU_SAVEAS },
    {  NM_ITEM,  NM_BARLABEL,    NULL,  0, 0, NULL },   /* Separator */
    {  NM_ITEM,  "Quit",          "Q",   0, 0, (APTR)MENU_QUIT },

    { NM_TITLE,  "Edit",          NULL,  0, 0, NULL },
    {  NM_ITEM,  "Cut",           "X",   0, 0, (APTR)MENU_CUT },
    {  NM_ITEM,  "Copy",          "C",   0, 0, (APTR)MENU_COPY },
    {  NM_ITEM,  "Paste",         "V",   0, 0, (APTR)MENU_PASTE },
    {  NM_ITEM,  NM_BARLABEL,    NULL,  0, 0, NULL },
    {  NM_ITEM,  "Select All",    "A",   NM_COMMANDSTRING, 0, (APTR)MENU_SELECTALL },

    { NM_TITLE,  "Style",         NULL,  0, 0, NULL },
    {  NM_ITEM,  "Bold",          "B",   CHECKIT|MENUTOGGLE, 0, (APTR)MENU_BOLD },
    {  NM_ITEM,  "Italic",        "I",   CHECKIT|MENUTOGGLE, 0, (APTR)MENU_ITALIC },
    {  NM_ITEM,  "Underline",     "U",   CHECKIT|MENUTOGGLE, 0, (APTR)MENU_UNDERLINE },

    { NM_END,    NULL,            NULL,  0, 0, NULL }
};
```

### NewMenu Field Reference

| Field | Description |
|---|---|
| `nm_Type` | `NM_TITLE`, `NM_ITEM`, `NM_SUB`, or `NM_END` |
| `nm_Label` | Text label, or `NM_BARLABEL` for separator |
| `nm_CommKey` | Keyboard shortcut character (Right-Amiga + key) |
| `nm_Flags` | `CHECKIT`, `CHECKED`, `MENUTOGGLE`, `NM_COMMANDSTRING`, `NM_ITEMDISABLED` |
| `nm_MutualExclude` | Bitmask of items that can't be checked simultaneously |
| `nm_UserData` | Application-defined value — typically a menu command ID |

### Creating and Attaching

```c
/* Get VisualInfo for the screen */
struct Screen *scr = LockPubScreen(NULL);
APTR vi = GetVisualInfo(scr, TAG_DONE);

/* Create the menu structure */
struct Menu *menuStrip = CreateMenus(nm, TAG_DONE);
if (!menuStrip) { /* error */ }

/* Layout the menus (calculates positions/sizes) */
if (!LayoutMenus(menuStrip, vi, GTMN_NewLookMenus, TRUE, TAG_DONE))
{
    FreeMenus(menuStrip);
    /* error */
}

/* Attach to window */
SetMenuStrip(win, menuStrip);

/* Cleanup (in reverse order): */
ClearMenuStrip(win);
FreeMenus(menuStrip);
FreeVisualInfo(vi);
UnlockPubScreen(NULL, scr);
```

---

## Handling Menu Events

### Basic Event Loop

Menu selections arrive as `IDCMP_MENUPICK` events. The `Code` field contains a **packed menu number**:

```c
case IDCMP_MENUPICK:
{
    UWORD menuCode = code;

    while (menuCode != MENUNULL)
    {
        struct MenuItem *item = ItemAddress(menuStrip, menuCode);

        /* Decode menu/item/sub numbers */
        UWORD menuNum = MENUNUM(menuCode);
        UWORD itemNum = ITEMNUM(menuCode);
        UWORD subNum  = SUBNUM(menuCode);

        /* Use UserData for command dispatch (cleaner than numbers) */
        APTR userData = GTMENUITEM_USERDATA(item);

        switch ((ULONG)userData)
        {
            case MENU_NEW:    NewDocument();   break;
            case MENU_OPEN:   OpenDocument();  break;
            case MENU_SAVE:   SaveDocument();  break;
            case MENU_QUIT:   running = FALSE; break;
            case MENU_CUT:    CutSelection();  break;
            case MENU_COPY:   CopySelection(); break;
            case MENU_PASTE:  PasteClipboard(); break;

            case MENU_BOLD:
                /* Check if item is now checked or unchecked */
                if (item->Flags & CHECKED)
                    EnableBold();
                else
                    DisableBold();
                break;
        }

        /* Multi-select: user may have selected multiple items
           by holding the right button while clicking */
        menuCode = item->NextSelect;
    }
    break;
}
```

### Menu Number Encoding

Menu selections are encoded as a single `UWORD`:

```c
/* Decode macros */
#define MENUNUM(code)   ((code) & 0x1F)           /* Bits 0–4:  menu (0–31) */
#define ITEMNUM(code)   (((code) >> 5) & 0x3F)    /* Bits 5–10: item (0–63) */
#define SUBNUM(code)    (((code) >> 11) & 0x1F)   /* Bits 11–15: sub (0–31) */

/* Encode macro */
#define FULLMENUNUM(m, i, s) ((m) | ((i) << 5) | ((s) << 11))

/* No selection */
#define MENUNULL  0xFFFF
```

### Multi-Select

The Amiga supports **multi-select**: the user can hold the right button and select multiple items in sequence. Each selected item's `NextSelect` field points to the next selection in the chain. You **must** walk this chain — otherwise, multi-selected items are silently dropped.

---

## Checkmark and Mutual Exclusion

### Toggle Menus

Items with `CHECKIT | MENUTOGGLE` act as toggles:

```c
{  NM_ITEM,  "Word Wrap",  NULL,  CHECKIT | MENUTOGGLE | CHECKED,  0, (APTR)MENU_WORDWRAP },
```

- `CHECKED` — item starts checked
- `MENUTOGGLE` — clicking toggles between checked/unchecked
- Without `MENUTOGGLE`, `CHECKIT` items are one-way (once checked, stay checked)

### Mutual Exclusion

Force radio-button behavior by setting `nm_MutualExclude` to a bitmask of incompatible items:

```c
/* Only one tab size can be active at a time */
{  NM_ITEM, "Tab: 2",  NULL, CHECKIT|CHECKED, ~1, (APTR)MENU_TAB2 },  /* Excludes items 1,2 */
{  NM_ITEM, "Tab: 4",  NULL, CHECKIT,         ~2, (APTR)MENU_TAB4 },  /* Excludes items 0,2 */
{  NM_ITEM, "Tab: 8",  NULL, CHECKIT,         ~4, (APTR)MENU_TAB8 },  /* Excludes items 0,1 */
```

The bitmask uses **item positions within the menu** (not IDs). Bit 0 = first item, bit 1 = second item, etc. `~1` means "exclude all except item 0."

---

## Sub-Menus

```c
{ NM_TITLE,  "Export",    NULL,  0, 0, NULL },
{  NM_ITEM,  "Image",     NULL,  0, 0, NULL },
{   NM_SUB,  "PNG",       NULL,  0, 0, (APTR)MENU_PNG },
{   NM_SUB,  "JPEG",      NULL,  0, 0, (APTR)MENU_JPEG },
{   NM_SUB,  "IFF ILBM",  NULL,  0, 0, (APTR)MENU_ILBM },
{  NM_ITEM,  "Text",      "T",   0, 0, (APTR)MENU_TEXT },
```

Sub-menus appear as a cascading menu to the right when the user hovers over the parent item. Only one level of sub-menus is supported.

---

## Dynamic Menu Modification

### Disabling/Enabling Items at Runtime

```c
/* Disable "Save" when no document is open */
OffMenu(win, FULLMENUNUM(0, 2, NOSUB));   /* Menu 0, Item 2 */

/* Enable "Paste" when clipboard has content */
OnMenu(win, FULLMENUNUM(1, 2, NOSUB));    /* Menu 1, Item 2 */
```

### Checking/Unchecking Items

```c
struct MenuItem *item = ItemAddress(menuStrip,
    FULLMENUNUM(2, 0, NOSUB));

/* Check programmatically */
item->Flags |= CHECKED;

/* Uncheck */
item->Flags &= ~CHECKED;
```

### Replacing the Entire Menu Strip

```c
ClearMenuStrip(win);
/* Modify or rebuild menuStrip */
SetMenuStrip(win, menuStrip);
```

---

## Keyboard Shortcuts

### Standard Single-Character Shortcuts

The `nm_CommKey` field accepts a single character. Intuition displays it as "Amiga+X" in the menu:

```c
{  NM_ITEM,  "Open...",  "O",  0, 0, (APTR)MENU_OPEN },
/* Displayed as:  Open...     ⌂O  */
```

### Multi-Character Shortcuts (NM_COMMANDSTRING)

For longer key descriptions (non-standard shortcuts):

```c
{  NM_ITEM,  "Find Next", "F3", NM_COMMANDSTRING, 0, (APTR)MENU_FINDNEXT },
/* NM_COMMANDSTRING tells GadTools to display the full string as-is */
```

> **Note**: `NM_COMMANDSTRING` only changes the display text. You must still handle the actual key detection in your `IDCMP_RAWKEY` handler — GadTools does not intercept arbitrary key combinations.

---

## Menu Imagery (Advanced)

Menu items can contain images instead of text:

```c
/* Image-based menu item */
struct Image *icon = /* ... your image ... */;

struct MenuItem imgItem = {
    .NextItem    = NULL,
    .LeftEdge    = 0,
    .TopEdge     = 0,
    .Width       = icon->Width,
    .Height      = icon->Height,
    .Flags       = ITEMTEXT | ITEMENABLED | HIGHCOMP,
    .MutualExclude = 0,
    .ItemFill    = (APTR)icon,
    .SelectFill  = NULL,
    .Command     = 0,
    .SubItem     = NULL,
    .NextSelect  = MENUNULL,
};
```

However, GadTools' `CreateMenus()` does not support image items — this requires manual `struct Menu`/`MenuItem` construction.

---

## Pitfalls

### 1. Not Walking NextSelect

```c
/* BUG — only handles first selection, drops multi-select */
struct MenuItem *item = ItemAddress(menuStrip, code);
HandleItem(item);
/* Missing: code = item->NextSelect; loop */
```

### 2. ClearMenuStrip Before Closing Window

If you call `CloseWindow()` without `ClearMenuStrip()` first, Intuition may access freed menu memory during the close process.

```c
/* CORRECT order */
ClearMenuStrip(win);
CloseWindow(win);
FreeMenus(menuStrip);
```

### 3. LayoutMenus with Wrong VisualInfo

The VisualInfo must match the screen the window is on. Using a VisualInfo from a different screen causes corrupted menu rendering.

### 4. Modifying Menu Strip While Active

Never modify `struct MenuItem` fields while the menu strip is attached to a window. Always `ClearMenuStrip()` first, modify, then `SetMenuStrip()` again.

### 5. Shortcut Key Collisions

Intuition automatically intercepts Right-Amiga+key combinations matching menu shortcuts. If two items share the same shortcut letter, only the first match is triggered.

---

## Best Practices

1. **Use `GTMENUITEM_USERDATA()`** for command dispatch — more robust than position-based menu/item numbers
2. **Always walk `NextSelect`** to handle multi-select properly
3. **Use `NM_BARLABEL`** to visually group related items with separators
4. **Follow platform conventions**: Project menu first, Quit at bottom with separator, Edit menu second
5. **Use `MENUTOGGLE`** for boolean settings — users expect toggle behavior
6. **Disable items** with `OffMenu()` when they don't apply — don't hide them
7. **Clean up in order**: `ClearMenuStrip()` → `CloseWindow()` → `FreeMenus()` → `FreeVisualInfo()`
8. **Use `GTMN_NewLookMenus, TRUE`** for the modern 3D menu appearance (OS 3.0+)

---

## References

- NDK 3.9: `intuition/intuition.h`, `libraries/gadtools.h`
- ADCD 2.1: `CreateMenus()`, `LayoutMenus()`, `SetMenuStrip()`, `ClearMenuStrip()`, `FreeMenus()`
- AmigaOS Reference Manual (RKRM): Libraries, Chapter 6 — Menus
- See also: [IDCMP](idcmp.md), [Windows](windows.md), [GadTools (Gadgets)](gadgets.md)
