[← Home](../README.md) · [Devices](README.md)

# console.device — Text Terminal I/O

## Overview

`console.device` provides ANSI-compatible text rendering into Intuition windows. It translates raw keycodes to ASCII and supports a rich set of escape sequences for cursor positioning, colour, and text formatting.

---

## Opening

```c
struct IOStdReq *con = CreateStdIO(port);
con->io_Data   = (APTR)win;  /* the Intuition Window */
con->io_Length = sizeof(struct Window);
OpenDevice("console.device", 0, (struct IORequest *)con, 0);
```

---

## Common Escape Sequences

| Sequence | Description |
|---|---|
| `\033[H` | Home cursor |
| `\033[nA` | Cursor up n lines |
| `\033[nB` | Cursor down n lines |
| `\033[nC` | Cursor right n columns |
| `\033[nD` | Cursor left n columns |
| `\033[y;xH` | Move to row y, column x |
| `\033[J` | Clear to end of screen |
| `\033[K` | Clear to end of line |
| `\033[nm` | Set graphics rendition (colour/style) |
| `\033[0m` | Reset attributes |
| `\033[1m` | Bold |
| `\033[3m` | Italic |
| `\033[4m` | Underline |
| `\033[30–37m` | Foreground colour |
| `\033[40–47m` | Background colour |

---

## References

- NDK39: `devices/conunit.h`
- ADCD 2.1: console.device autodocs
