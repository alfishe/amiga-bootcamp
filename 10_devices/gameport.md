[← Home](../README.md) · [Devices](README.md)

# gameport.device — Joystick and Mouse

## Overview

`gameport.device` reads joystick and mouse ports (active on port 1 for joystick, port 0 for mouse). Uses CIA and custom chip registers.

---

## Controller Types

```c
/* devices/gameport.h */
#define GPCT_ALLOCATED   -1   /* port is allocated */
#define GPCT_NOCONTROLLER 0   /* nothing connected */
#define GPCT_MOUSE       1   /* mouse */
#define GPCT_RELJOYSTICK 2   /* relative joystick (proportional) */
#define GPCT_ABSJOYSTICK 3   /* absolute joystick */
```

---

## Reading a Joystick

```c
struct IOStdReq *gp = CreateStdIO(port);
OpenDevice("gameport.device", 1, (struct IORequest *)gp, 0);

/* Set controller type: */
UBYTE type = GPCT_ABSJOYSTICK;
gp->io_Command = GPD_SETCTYPE;
gp->io_Data    = &type;
gp->io_Length  = 1;
DoIO((struct IORequest *)gp);

/* Set trigger conditions: */
struct GamePortTrigger trigger = {
    GPTF_UPKEYS | GPTF_DOWNKEYS,  /* report buttons */
    10000,   /* X delta timeout */
    10000,   /* Y delta timeout */
    1, 1     /* X/Y delta threshold */
};
gp->io_Command = GPD_SETTRIGGER;
gp->io_Data    = &trigger;
gp->io_Length  = sizeof(trigger);
DoIO((struct IORequest *)gp);

/* Read events: */
struct InputEvent ie;
gp->io_Command = GPD_READEVENT;
gp->io_Data    = &ie;
gp->io_Length  = sizeof(ie);
DoIO((struct IORequest *)gp);
/* ie.ie_Code, ie.ie_position.ie_xy give button/direction */

CloseDevice((struct IORequest *)gp);
```

---

## References

- NDK39: `devices/gameport.h`
