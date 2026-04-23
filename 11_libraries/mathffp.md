[← Home](../README.md) · [Libraries](README.md)

# Math Libraries — Floating Point

## Overview

AmigaOS provides multiple math libraries for floating-point operations. The 68000 has no FPU, so all math is done in software unless a 68881/68882/68040/68060 FPU is present.

---

## Library Stack

| Library | Format | Description |
|---|---|---|
| `mathffp.library` | FFP (Motorola Fast Floating Point) | Original Amiga format (32-bit) |
| `mathieeesingbas.library` | IEEE 754 single (32-bit) | IEEE single precision |
| `mathieeedoubbas.library` | IEEE 754 double (64-bit) | IEEE double precision |
| `mathtrans.library` | FFP | Transcendental functions (sin, cos, sqrt) |
| `mathieeesingtrans.library` | IEEE single | IEEE single transcendentals |
| `mathieeedoubtrans.library` | IEEE double | IEEE double transcendentals |

---

## FFP Format

Motorola FFP is NOT IEEE 754:
```
Bits 31–8: 24-bit mantissa (normalised, implicit 1.xxx)
Bits  7–1: 7-bit exponent (excess-64)
Bit     0: sign (0=positive, 1=negative)
```

---

## Using IEEE Math

```c
struct Library *MathIeeeSingBasBase =
    OpenLibrary("mathieeesingbas.library", 0);

float a = 3.14f;
float b = 2.0f;
float c = IEEESPMul(a, b);  /* 6.28 */
float d = IEEESPAdd(a, b);  /* 5.14 */
float e = IEEESPDiv(a, b);  /* 1.57 */

CloseLibrary(MathIeeeSingBasBase);
```

---

## 68881/68882 FPU

When an FPU is present, the math libraries are replaced with ROM patches that use native FPU instructions. The application code is identical — the library transparently switches to hardware.

```c
if (SysBase->AttnFlags & AFF_68881) {
    /* 68881/68882 FPU present */
}
if (SysBase->AttnFlags & AFF_FPU40) {
    /* 68040 internal FPU */
}
```

---

## References

- NDK39: `libraries/mathffp.h`, `libraries/mathieeesp.h`
