[← Home](../README.md) · [Libraries](README.md)

# keymap.library — Keyboard Mapping

## Overview

`keymap.library` translates raw keycodes from `keyboard.device` into character codes using the active keymap. Each keymap defines the mapping from physical keys to characters, including dead keys and string sequences.

---

## Key Functions

```c
/* Map a raw keycode + qualifiers to ASCII: */
LONG actual = MapRawKey(&inputEvent, buffer, bufsize, NULL);
/* Returns number of characters, -1 if buffer too small */

/* Map ANSI code back to raw key: */
WORD MapANSI(STRPTR string, WORD count,
             STRPTR buffer, WORD length,
             struct KeyMap *keyMap);
```

---

## struct KeyMap

```c
/* devices/keymap.h — NDK39 */
struct KeyMap {
    UBYTE *km_LoKeyMapTypes;    /* type array for keys 0x00–0x3F */
    ULONG *km_LoKeyMap;         /* mapping array for keys 0x00–0x3F */
    UBYTE *km_LoCapsable;       /* caps-lock bitmap */
    UBYTE *km_LoRepeatable;     /* auto-repeat bitmap */
    UBYTE *km_HiKeyMapTypes;    /* type array for keys 0x40–0x77 */
    ULONG *km_HiKeyMap;
    UBYTE *km_HiCapsable;
    UBYTE *km_HiRepeatable;
};
```

---

## References

- NDK39: `devices/keymap.h`, `libraries/keymap.h`
