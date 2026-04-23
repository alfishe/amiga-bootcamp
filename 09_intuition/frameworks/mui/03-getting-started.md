[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Getting Started

## Required Includes

Every MUI application needs at minimum:

```c
#include <libraries/mui.h>
```

Depending on your compiler, you also need one of the following for function prototypes:

```c
/* For SAS/C, DICE, and other traditional compilers */
#include <clib/muimaster_protos.h>
#include <pragmas/muimaster_pragmas.h>

/* For GCC */
#include <inline/muimaster.h>
```

A typical MUI program also includes standard AmigaOS headers:

```c
#include <dos/dos.h>
#include <graphics/gfxmacros.h>
#include <workbench/workbench.h>
#include <clib/alib_protos.h>
#include <clib/exec_protos.h>
#include <clib/dos_protos.h>
#include <clib/graphics_protos.h>
#include <clib/intuition_protos.h>
#include <clib/gadtools_protos.h>
#include <clib/utility_protos.h>
#include <clib/asl_protos.h>
```

## Opening the Library

Before using any MUI functions, open `muimaster.library`:

```c
#define MUIMASTER_NAME    "muimaster.library"
#define MUIMASTER_VMIN    11

struct Library *MUIMasterBase;

if (!(MUIMasterBase = OpenLibrary(MUIMASTER_NAME, MUIMASTER_VMIN)))
{
    /* handle error */
}
```

The minimum required version is **11**. Some macros in `libraries/mui.h` require V11 or above.

When your application exits, close the library:

```c
CloseLibrary(MUIMasterBase);
```

## Minimal "Hello MUI" Application

Here is the smallest possible MUI application that opens a window with some text:

```c
#include <libraries/mui.h>
#include <clib/muimaster_protos.h>
#include <clib/exec_protos.h>
#include <clib/intuition_protos.h>
#include <pragmas/muimaster_pragmas.h>
#include <pragmas/exec_pragmas.h>
#include <pragmas/intuition_pragmas.h>
#include <stdio.h>
#include <stdlib.h>

struct Library *MUIMasterBase;
extern struct Library *SysBase;

int main(int argc, char *argv[])
{
    APTR app, window;

    if (!(MUIMasterBase = OpenLibrary(MUIMASTER_NAME, MUIMASTER_VMIN)))
    {
        printf("Failed to open %s\n", MUIMASTER_NAME);
        return 20;
    }

    app = ApplicationObject,
        MUIA_Application_Title      , "HelloMUI",
        MUIA_Application_Version    , "$VER: HelloMUI 1.0",
        MUIA_Application_Copyright  , "Your Name",
        MUIA_Application_Author     , "Your Name",
        MUIA_Application_Description, "A minimal MUI application",
        MUIA_Application_Base       , "HELLOMUI",

        SubWindow, window = WindowObject,
            MUIA_Window_Title, "Hello MUI",
            MUIA_Window_ID   , MAKE_ID('H','L','O','1'),

            WindowContents, VGroup,
                Child, TextObject,
                    MUIA_Text_Contents, "\33cHello, MUI World!",
                    End,
                End,

            End,
        End;

    if (!app)
    {
        printf("Failed to create Application.\n");
        CloseLibrary(MUIMasterBase);
        return 20;
    }

    /* Close window when requested */
    DoMethod(window, MUIM_Notify, MUIA_Window_CloseRequest, TRUE,
        app, 2, MUIM_Application_ReturnID, MUIV_Application_ReturnID_Quit);

    set(window, MUIA_Window_Open, TRUE);

    {
        ULONG sigs = 0;

        while (DoMethod(app, MUIM_Application_NewInput, &sigs)
               != MUIV_Application_ReturnID_Quit)
        {
            if (sigs)
            {
                sigs = Wait(sigs | SIGBREAKF_CTRL_C);
                if (sigs & SIGBREAKF_CTRL_C)
                    break;
            }
        }
    }

    set(window, MUIA_Window_Open, FALSE);
    MUI_DisposeObject(app);
    CloseLibrary(MUIMasterBase);

    return 0;
}
```

## The demo.h Pattern

The official MUI examples use a common header file called `demo.h` that centralizes includes and provides helper functions. This is a recommended pattern for your own projects:

```c
/* demo.h - common includes and helpers for MUI applications */

#include <libraries/mui.h>
#include <dos/dos.h>
#include <graphics/gfxmacros.h>
#include <workbench/workbench.h>
#include <clib/alib_protos.h>
#include <clib/exec_protos.h>
#include <clib/dos_protos.h>
#include <clib/icon_protos.h>
#include <clib/graphics_protos.h>
#include <clib/intuition_protos.h>
#include <clib/gadtools_protos.h>
#include <clib/utility_protos.h>
#include <clib/asl_protos.h>

#ifndef __GNUC__
#include <clib/muimaster_protos.h>
#else
#include <inline/muimaster.h>
#endif

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

extern struct Library *SysBase, *IntuitionBase, *UtilityBase;
extern struct Library *GfxBase, *DOSBase, *IconBase;
struct Library *MUIMasterBase;

/* A fail function that cleans up and exits */
static VOID fail(APTR app, char *str)
{
    if (app)
        MUI_DisposeObject(app);

#ifndef _DCC
    if (MUIMasterBase)
        CloseLibrary(MUIMasterBase);
#endif

    if (str)
    {
        puts(str);
        exit(20);
    }
    exit(0);
}

/* Open muimaster.library */
static VOID init(VOID)
{
#ifndef _DCC
    if (!(MUIMasterBase = OpenLibrary(MUIMASTER_NAME, MUIMASTER_VMIN)))
        fail(NULL, "Failed to open " MUIMASTER_NAME ".");
#endif
}
```

## Compiler Setup

### SAS/C

The official examples were written for SAS/C. Key settings:

- Stack size: at least 8192 bytes (`LONG __stack = 8192;`)
- Include pragmas for library calls
- Use `__saveds` and `__asm` register keywords for dispatcher functions

### DICE

DICE requires slightly different macros:

```c
#define REG(x) __ ## x
#define ASM
#define SAVEDS __geta4
```

DICE also handles library opening differently; the examples use conditional compilation for DICE.

### GCC

GCC uses inline headers rather than pragmas:

```c
#include <inline/muimaster.h>
```

GCC does not need `__asm` or `__saveds` for dispatcher functions.

### MAXON C

Similar to GCC in that `ASM` and `SAVEDS` are defined as empty:

```c
#define ASM
#define SAVEDS
```

## Build Workflow

A typical build for SAS/C:

```
sc LINK AppWindow.c demo.h
```

For GCC cross-compilation:

```
m68k-amigaos-gcc -o AppWindow AppWindow.c -lmuimaster
```

Ensure your NDK (Native Developer Kit) include paths are set correctly so that `libraries/mui.h` and the clib/inline headers are found.

---

Previous: [Architecture](02-architecture.md)
Next: [Core Concepts](04-core-concepts.md)
