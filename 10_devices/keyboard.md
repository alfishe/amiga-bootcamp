[← Home](../README.md) · [Devices](README.md)

# keyboard.device — Keyboard Input

## Overview

`keyboard.device` provides raw keycode events from the keyboard controller (8520 CIA-A). Normally used indirectly via `input.device`, but can be accessed directly for keymap-independent scanning.

---

## Keycodes

Amiga keycodes are 7-bit values (0–127). Bit 7 indicates key-up:

| Code | Key | Code | Key |
|---|---|---|---|
| `$00` | \` (backtick) | `$40` | Space |
| `$01`–`$0A` | 1–0 | `$41` | Backspace |
| `$10`–`$19` | Q–P | `$42` | Tab |
| `$20`–`$28` | A–L | `$43` | Enter (keypad) |
| `$31`–`$39` | Z–/ | `$44` | Return |
| `$45` | Escape | `$46` | Delete |
| `$4C` | Cursor Up | `$4D` | Cursor Down |
| `$4E` | Cursor Right | `$4F` | Cursor Left |
| `$50`–`$59` | F1–F10 | `$5F` | Help |
| `$60` | Left Shift | `$61` | Right Shift |
| `$62` | Caps Lock | `$63` | Control |
| `$64` | Left Alt | `$65` | Right Alt |
| `$66` | Left Amiga | `$67` | Right Amiga |

---

## Commands

| Code | Constant | Description |
|---|---|---|
| 2 | `CMD_READ` | Read raw keycodes |
| 5 | `CMD_CLEAR` | Clear keyboard buffer |
| 9 | `KBD_READMATRIX` | Read full key matrix state |
| 10 | `KBD_ADDRESETHANDLER` | Add Ctrl-Amiga-Amiga handler |
| 11 | `KBD_REMRESETHANDLER` | Remove reset handler |
| 12 | `KBD_RESETHANDLERDONE` | Acknowledge reset handler completion |

---

## References

- NDK39: `devices/keyboard.h`
