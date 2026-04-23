[← Home](../README.md) · [Toolchain](README.md)

# Makefile Patterns for Amiga Cross-Compilation

## Overview

Standard Makefile patterns for building Amiga executables from Linux/macOS using the bebbo cross-toolchain or vasm/vlink.

---

## GCC Cross-Compilation

```makefile
# Makefile for m68k-amigaos-gcc
PREFIX  = m68k-amigaos-
CC      = $(PREFIX)gcc
AS      = $(PREFIX)as
LD      = $(PREFIX)gcc
STRIP   = $(PREFIX)strip

NDK     = /opt/amiga/m68k-amigaos/ndk-include

CFLAGS  = -noixemul -m68000 -Os -fomit-frame-pointer \
          -I$(NDK) -Wall -Wextra
LDFLAGS = -noixemul -Wl,--emit-relocs
LIBS    = -lamiga

TARGET  = myapp
SRCS    = main.c util.c
OBJS    = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $^ $(LIBS)
	$(STRIP) $@

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
```

---

## vasm/vlink Assembly Project

```makefile
VASM  = vasmm68k_mot
VLINK = vlink

AFLAGS = -Fhunk -m68000 -I/opt/amiga/ndk/Include/include_i
LFLAGS = -bamigahunk -s

TARGET = myprog
SRCS   = main.s gfx.s sound.s
OBJS   = $(SRCS:.s=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(VLINK) $(LFLAGS) -o $@ $^

%.o: %.s
	$(VASM) $(AFLAGS) -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)
```

---

## Mixed C + Assembly

```makefile
CC   = m68k-amigaos-gcc
VASM = vasmm68k_mot

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.s
	$(VASM) -Fhunk -m68000 -o $@ $<

myapp: main.o fastblit.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)
```

---

## References

- [gcc_amiga.md](gcc_amiga.md) — GCC setup
- [vasm_vlink.md](vasm_vlink.md) — vasm/vlink setup
