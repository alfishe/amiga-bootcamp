[← Home](../README.md) · [Toolchain](README.md)

# NDK — Native Development Kit Versions

## Overview

The **NDK** (Native Development Kit) contains all header files, FD files, link libraries, and autodocs needed to develop for AmigaOS. It is the authoritative source for all structure definitions and API specifications.

---

## Version History

| NDK | OS | Source | Availability |
|---|---|---|---|
| NDK 1.3 | OS 1.3 | Commodore | Archived; ADF collections |
| NDK 2.0 | OS 2.0 | Commodore | Archived |
| NDK 3.1 | OS 3.1 | Commodore (final) | Widely archived, Aminet |
| NDK 3.5 | OS 3.5 | Haage & Partner | Included with OS 3.5 CD |
| NDK 3.9 | OS 3.9 | Haage & Partner | **Free download** from Hyperion/Aminet |
| NDK 3.2 | OS 3.2 | Hyperion | Commercial (~€30), bundled with OS 3.2 |

---

## Where to Download

| NDK | URL |
|---|---|
| NDK 3.9 | Aminet: `dev/misc/NDK39.lha` — **free, recommended baseline** |
| NDK 3.2 | https://www.hyperion-entertainment.com/ (purchase required) |
| NDK 3.1 | Search Aminet or archive.org for `NDK3.1.lha` |

---

## Contents

```
NDK_3.9/
  Include/
    include_h/        C headers (.h)
    include_i/        Assembler includes (.i)
    fd/                FD files (function definitions)
    sfd/               SFD files (extended function definitions)
    pragmas/           SAS/C pragma headers
    inline/            GCC inline headers
    proto/             Portable proto headers
    lvo/               LVO offset include files (.i)
  Documentation/
    autodocs/          Library/device API documentation
  Lib/
    linker_libs/       Amiga link libraries (.lib)
    startup/           C startup code
```

---

## Key Differences Between Versions

| Feature | NDK 3.1 | NDK 3.9 | NDK 3.2 |
|---|---|---|---|
| `exec/exec.h` | OS 3.1 structures | + V39 extensions | + V47 extensions |
| 68040/060 support | Minimal | 040/060 library headers | Full |
| SFD files | No | Yes | Yes |
| Locale support | Basic | Full | Full |
| Datatypes | No | Yes | Yes |
| Reaction GUI | No | No | Yes |

---

## Using NDK with Cross-Compiler

```bash
# Set up include paths:
export NDK=/path/to/NDK_3.9
m68k-amigaos-gcc -I$NDK/Include/include_h \
                  -L$NDK/Lib/linker_libs \
                  -noixemul -o output source.c
```

---

## References

- Hyperion Entertainment: https://www.hyperion-entertainment.com/
- Aminet: https://aminet.net/
