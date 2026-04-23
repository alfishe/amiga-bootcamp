[← Home](../README.md) · [AmigaDOS](README.md)

# Environment Variables — GetVar, SetVar

## Overview

AmigaDOS supports both **local** (per-process) and **global** (system-wide) environment variables. Local variables are stored in the process's `pr_LocalVars` MinList; global variables are stored as files in `ENV:` (RAM-backed) and `ENVARC:` (persistent on disk).

---

## API

| LVO | Function | Description |
|---|---|---|
| −900 | `GetVar(name, buf, size, flags)` | Read a variable |
| −906 | `SetVar(name, buf, size, flags)` | Set or create a variable |
| −912 | `DeleteVar(name, flags)` | Remove a variable |
| −918 | `FindVar(name, type)` | Find a LocalVar node |

### Flags

```c
/* dos/var.h — NDK39 */
#define GVF_GLOBAL_ONLY   0x100   /* search only ENV: */
#define GVF_LOCAL_ONLY    0x200   /* search only pr_LocalVars */
#define GVF_BINARY_VAR    0x10    /* treat value as binary data */
#define GVF_DONT_NULL_TERM 0x20   /* don't null-terminate result */
#define LV_VAR            0       /* standard variable */
#define LV_ALIAS          1       /* shell alias */
```

---

## Usage

```c
/* Set a global variable: */
SetVar("EDITOR", "ed", -1, GVF_GLOBAL_ONLY);

/* Read it back: */
char buf[256];
if (GetVar("EDITOR", buf, sizeof(buf), 0) >= 0) {
    Printf("EDITOR = %s\n", buf);
}

/* Delete: */
DeleteVar("EDITOR", GVF_GLOBAL_ONLY);
```

---

## Storage Locations

| Scope | Storage | Persistent? |
|---|---|---|
| Local | `pr_LocalVars` MinList (in-memory) | No — dies with process |
| Global (volatile) | `ENV:` — assign to `RAM:Env/` | No — lost on reboot |
| Global (persistent) | `ENVARC:` — assign to `SYS:Prefs/Env-Archive/` | Yes — survives reboot |

The startup-sequence copies `ENVARC:` to `ENV:` at boot.

---

## References

- NDK39: `dos/var.h`
- ADCD 2.1: `GetVar`, `SetVar`, `DeleteVar`
