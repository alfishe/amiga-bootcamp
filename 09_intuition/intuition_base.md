[← Home](../README.md) · [Intuition](README.md)

# IntuitionBase — Global GUI State

## Overview

`intuition.library` manages screens, windows, menus, gadgets, and the input event pipeline. `IntuitionBase` is the library base containing active display state.

---

## struct IntuitionBase (Key Fields)

```c
/* intuition/intuitionbase.h — NDK39 */
struct IntuitionBase {
    struct Library  LibNode;
    struct View     ViewLord;         /* master View */
    struct Window  *ActiveWindow;     /* currently active window */
    struct Screen  *ActiveScreen;     /* currently active screen */
    struct Screen  *FirstScreen;      /* head of screen list */
    /* ... private fields ... */
};
```

---

## Opening

```c
struct IntuitionBase *IntuitionBase;
IntuitionBase = (struct IntuitionBase *)OpenLibrary("intuition.library", 39);
```

---

## References

- NDK39: `intuition/intuitionbase.h`
